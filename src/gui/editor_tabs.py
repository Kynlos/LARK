"""Tab widget for managing multiple open files."""

import os
from PyQt6.QtWidgets import (
    QTabWidget, QMenu, QMessageBox,
    QFileDialog, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QKeySequence
from ..editor import CasebookEditor
from .file_watcher import FileWatcher
from .minimap import Minimap

class EditorContainer(QWidget):
    """Container for editor and minimap."""
    
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.minimap = Minimap()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addWidget(self.editor)
        layout.addWidget(self.minimap)
        
        self.setLayout(layout)
        self.minimap.set_editor(self.editor)

class EditorTabs(QTabWidget):
    """Tab widget containing multiple editors."""
    
    currentFileChanged = pyqtSignal(str)  # Signal emitted when current file changes
    
    def __init__(self, parent=None, grammar_manager=None, main_window=None):
        super().__init__(parent)
        self.grammar_manager = grammar_manager
        self.main_window = main_window
        self.setup_ui()
        self.open_files = {}  # Map of file paths to editors
        
        # Set up file watcher
        self.file_watcher = FileWatcher(self)
        self.file_watcher.fileChanged.connect(self.on_file_changed)
        
        # Set up auto-save timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.start(60000)  # Auto-save every minute
        
    def setup_ui(self):
        """Initialize the UI."""
        # Set tab properties
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setDocumentMode(True)
        
        # Connect signals
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self.on_current_changed)
        
        # Set context menu policy
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def create_editor(self):
        """Create a new editor instance."""
        editor = CasebookEditor(self, self.grammar_manager)
        editor.modificationChanged.connect(self.on_modification_changed)
        editor.textChanged.connect(self.on_text_changed)
        editor.selectionChanged.connect(self.on_selection_changed)
        editor.SCN_MODIFIED.connect(self.on_text_changed)  # For undo/redo state
        
        # Create container with minimap
        container = EditorContainer(editor)
        return container, editor
        
    def open_file(self, filepath):
        """Open a file in a new tab."""
        # Check if file is already open
        if filepath in self.open_files:
            self.setCurrentWidget(self.open_files[filepath].parent())
            return
            
        try:
            # Create new editor
            container, editor = self.create_editor()
            
            # Load file content
            with open(filepath, 'r', encoding='utf-8') as f:
                editor.setText(f.read())
                
            # Add to tab widget
            filename = os.path.basename(filepath)
            index = self.addTab(container, filename)
            
            # Store in open files map
            self.open_files[filepath] = editor
            
            # Start watching file
            self.file_watcher.watch_file(filepath)
            
            # Set as current tab
            self.setCurrentIndex(index)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            
    def save_current_file(self):
        """Save the current file."""
        container = self.currentWidget()
        if not container:
            return
            
        editor = container.editor
        filepath = self.get_file_path(editor)
        if not filepath:
            return self.save_current_file_as()
            
        try:
            # Stop watching file during save
            self.file_watcher.unwatch_file(filepath)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(editor.text())
                
            # Resume watching file
            self.file_watcher.watch_file(filepath)
            
            editor.setModified(False)
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False
            
    def save_current_file_as(self):
        """Save the current file with a new name."""
        container = self.currentWidget()
        if not container:
            return False
            
        editor = container.editor
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "Casebook Files (*.case);;All Files (*.*)"
        )
        
        if not filepath:
            return False
            
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(editor.text())
                
            # Update tab text and open files map
            old_path = self.get_file_path(editor)
            if old_path in self.open_files:
                self.file_watcher.unwatch_file(old_path)
                del self.open_files[old_path]
                
            self.open_files[filepath] = editor
            self.setTabText(self.currentIndex(), os.path.basename(filepath))
            
            # Start watching new file
            self.file_watcher.watch_file(filepath)
            
            editor.setModified(False)
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False
            
    def close_tab(self, index):
        """Close the specified tab."""
        container = self.widget(index)
        if not container:
            return
            
        editor = container.editor
        
        # Check for unsaved changes
        if editor.isModified():
            filename = self.tabText(index)
            reply = QMessageBox.question(
                self,
                "Save Changes",
                f"Save changes to {filename}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_current_file():
                    return
                    
        # Remove from open files map and file watcher
        filepath = self.get_file_path(editor)
        if filepath in self.open_files:
            self.file_watcher.unwatch_file(filepath)
            del self.open_files[filepath]
            
        # Remove tab
        self.removeTab(index)
        
    def get_file_path(self, editor):
        """Get the file path for an editor."""
        for path, ed in self.open_files.items():
            if ed == editor:
                return path
        return None
        
    def on_current_changed(self, index):
        """Handle current tab change."""
        container = self.widget(index)
        if container:
            editor = container.editor
            filepath = self.get_file_path(editor)
            self.currentFileChanged.emit(filepath)
            if self.main_window:
                self.main_window.update_edit_actions()
            
    def on_modification_changed(self, modified):
        """Handle modification state change."""
        editor = self.sender()
        index = -1
        for i in range(self.count()):
            if self.widget(i).editor == editor:
                index = i
                break
                
        if index >= 0:
            filename = os.path.basename(self.get_file_path(editor) or "Untitled")
            if modified:
                filename += "*"
            self.setTabText(index, filename)
            
    def on_text_changed(self):
        """Handle text changes."""
        editor = self.sender()
        container = editor.parent().parent()  # editor -> container -> tab widget
        if container == self.currentWidget() and self.main_window:
            self.main_window.update_edit_actions()
            
    def on_selection_changed(self):
        """Handle selection changes."""
        editor = self.sender()
        container = editor.parent().parent()  # editor -> container -> tab widget
        if container == self.currentWidget() and self.main_window:
            self.main_window.update_edit_actions()
            
    def on_file_changed(self, filepath):
        """Handle external file changes."""
        editor = self.open_files.get(filepath)
        if not editor:
            return
            
        if editor.isModified():
            # File changed but we have unsaved changes
            reply = QMessageBox.question(
                self,
                "File Changed",
                f"The file has been modified outside the editor and you have unsaved changes.\n"
                f"Do you want to reload it and lose your changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                editor.setText(f.read())
            editor.setModified(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not reload file: {str(e)}")
            
    def auto_save(self):
        """Auto-save all modified files."""
        for filepath, editor in self.open_files.items():
            if editor.isModified():
                try:
                    # Stop watching file during save
                    self.file_watcher.unwatch_file(filepath)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(editor.text())
                        
                    # Resume watching file
                    self.file_watcher.watch_file(filepath)
                    
                    editor.setModified(False)
                except Exception as e:
                    print(f"Auto-save failed for {filepath}: {str(e)}")
                    
    def show_context_menu(self, position):
        """Show context menu for tabs."""
        menu = QMenu()
        
        # Add actions
        save_action = QAction("Save", self)
        save_action.setIcon(self.window().resource_manager.get_icon("save"))
        save_action.triggered.connect(self.save_current_file)
        menu.addAction(save_action)
        
        save_as_action = QAction("Save As...", self)
        save_as_action.setIcon(self.window().resource_manager.get_icon("save"))
        save_as_action.triggered.connect(self.save_current_file_as)
        menu.addAction(save_as_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(lambda: self.close_tab(self.currentIndex()))
        menu.addAction(close_action)
        
        close_all_action = QAction("Close All", self)
        close_all_action.triggered.connect(self.close_all_tabs)
        menu.addAction(close_all_action)
        
        menu.exec(self.mapToGlobal(position))
        
    def close_all_tabs(self):
        """Close all open tabs."""
        while self.count() > 0:
            self.close_tab(0)
            
    def has_unsaved_changes(self):
        """Check if any open files have unsaved changes."""
        for i in range(self.count()):
            container = self.widget(i)
            if container and container.editor.isModified():
                return True
        return False
        
    def set_font_size(self, size):
        """Set font size for all editors."""
        for i in range(self.count()):
            container = self.widget(i)
            if container:
                font = container.editor.font()
                font.setPointSize(size)
                container.editor.setFont(font)
