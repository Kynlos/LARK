"""Editor tabs management."""

import os
from PyQt6.QtWidgets import QTabWidget, QMessageBox, QFileDialog
from PyQt6.QtCore import pyqtSignal, Qt
from .editor_container import EditorContainer
from ..utils.file_watcher import FileWatcher

class EditorTabs(QTabWidget):
    """Manages editor tabs."""
    
    currentFileChanged = pyqtSignal(str)  # Signal emitted when current file changes
    
    def __init__(self, parent=None, grammar_manager=None, main_window=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.currentChanged.connect(self._on_current_changed)
        
        self.grammar_manager = grammar_manager
        self.main_window = main_window
        self.file_watcher = FileWatcher()
        self.file_watcher.fileChanged.connect(self._on_file_changed)
        
        # Track open files
        self.open_files = {}  # filepath -> editor mapping
        
    def create_editor(self, filepath=None):
        """Create a new editor container and editor."""
        container = EditorContainer(self, self.grammar_manager)
        if filepath:
            container.set_file_path(filepath)
        editor = container.editor
        
        # Connect editor signals
        editor.modificationChanged.connect(
            lambda modified: self._on_modification_changed(editor, modified)
        )
        
        return container, editor
        
    def new_file(self):
        """Create a new file tab."""
        container, editor = self.create_editor()
        self.addTab(container, "Untitled")
        self.setCurrentWidget(container)
        editor.setFocus()
        return editor
        
    def open_file(self, filepath):
        """Open a file in a new tab or focus existing tab."""
        # Check if file is already open
        if filepath in self.open_files:
            # Find and activate the tab
            for i in range(self.count()):
                container = self.widget(i)
                if container.get_file_path() == filepath:
                    self.setCurrentIndex(i)
                    return self.open_files[filepath]
        
        try:
            # Read file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create new editor
            container, editor = self.create_editor(filepath)
            
            # Set content
            editor.setText(content)
            
            # Add tab
            self.addTab(container, os.path.basename(filepath))
            self.setCurrentWidget(container)
            
            # Track open file
            self.open_files[filepath] = editor
            
            # Start watching file
            self.file_watcher.watch_file(filepath)
            
            editor.setModified(False)
            return editor
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening File",
                f"Could not open file: {filepath}\n\nError: {str(e)}"
            )
            return None
            
    def save_file(self, editor=None, filepath=None):
        """Save the current file."""
        if editor is None:
            container = self.currentWidget()
            if not container:
                return False
            editor = container.editor
            
        if filepath is None:
            container = editor.parent()
            filepath = container.get_file_path()
            
        if not filepath:
            return self.save_file_as(editor)
            
        try:
            # Get content from editor
            content = editor.text()
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Update editor state
            editor.setModified(False)
            
            # Update tab text (in case it was a new file)
            container = editor.parent()
            if container:
                idx = self.indexOf(container)
                if idx >= 0:
                    self.setTabText(idx, os.path.basename(filepath))
                    
            return True
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Saving File",
                f"Could not save file: {filepath}\n\nError: {str(e)}"
            )
            return False
            
    def save_file_as(self, editor=None):
        """Save the current file with a new name."""
        if editor is None:
            container = self.currentWidget()
            if not container:
                return False
            editor = container.editor
            
        container = editor.parent()
        current_file = container.get_file_path()
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            current_file if current_file else "",
            "All Files (*.*)"
        )
        
        if not filepath:
            return False
            
        # Update file tracking
        if current_file:
            self.file_watcher.unwatch_file(current_file)
            del self.open_files[current_file]
            
        self.open_files[filepath] = editor
        container.set_file_path(filepath)
        self.setTabText(self.currentIndex(), os.path.basename(filepath))
        
        # Start watching new file
        self.file_watcher.watch_file(filepath)
        
        # Save the file
        return self.save_file(editor, filepath)
        
    def save_current_file(self):
        """Save the current file."""
        container = self.currentWidget()
        if container:
            return self.save_file(container.editor)
        return False
        
    def close_tab(self, index):
        """Close the specified tab."""
        container = self.widget(index)
        if not container:
            return
            
        editor = container.editor
        if editor.isModified():
            reply = QMessageBox.question(
                self,
                "Save Changes",
                "The document has been modified.\nDo you want to save your changes?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                if not self.save_file(editor):
                    return  # Don't close if save was cancelled or failed
            elif reply == QMessageBox.StandardButton.Cancel:
                return
                
        # Stop watching file
        filepath = container.get_file_path()
        if filepath:
            self.file_watcher.unwatch_file(filepath)
            del self.open_files[filepath]
            
        self.removeTab(index)
        
    def close_all_tabs(self):
        """Close all open tabs."""
        while self.count() > 0:
            self.close_tab(0)
            
    def _on_current_changed(self, index):
        """Handle current tab change."""
        container = self.widget(index)
        if container:
            self.currentFileChanged.emit(container.get_file_path() or "")
            
    def _on_modification_changed(self, editor, modified):
        """Handle editor modification state change."""
        container = editor.parent()
        if not container:
            return
            
        idx = self.indexOf(container)
        if idx < 0:
            return
            
        filename = os.path.basename(container.get_file_path()) if container.get_file_path() else "Untitled"
        if modified:
            filename += "*"
        self.setTabText(idx, filename)
        
    def _on_file_changed(self, filepath):
        """Handle external file changes."""
        if filepath not in self.open_files:
            return
            
        editor = self.open_files[filepath]
        if editor.isModified():
            reply = QMessageBox.question(
                self,
                "File Changed",
                f"The file {filepath} has been modified outside the editor.\n"
                "Do you want to reload it and lose your changes?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            editor.setText(content)
            editor.setModified(False)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error Reloading File",
                f"Could not reload file: {filepath}\n\nError: {str(e)}"
            )
            
    def update_font_size(self, size):
        """Update font size for all editors."""
        for i in range(self.count()):
            container = self.widget(i)
            if container:
                font = container.editor.font()
                font.setPointSize(size)
                container.editor.setFont(font)
                
    def get_current_file(self):
        """Get the path of the currently active file."""
        current = self.currentWidget()
        if current:
            return current.get_file_path()
        return None
        
    def get_editor_for_file(self, file_path):
        """Get the editor widget for a given file path."""
        if file_path in self.open_files:
            return self.open_files[file_path]
        return None
        
    def has_unsaved_changes(self):
        """Check if any open files have unsaved changes."""
        for i in range(self.count()):
            container = self.widget(i)
            if container and container.editor.isModified():
                return True
        return False
