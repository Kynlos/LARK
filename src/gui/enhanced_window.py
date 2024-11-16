"""Enhanced main window implementation for the Casebook Editor."""

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QToolBar, QStatusBar,
    QLabel, QSpinBox, QComboBox, QHBoxLayout, QSplitter
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont
from .file_tree import ProjectTree
from .editor_tabs import EditorTabs
from ..resources.resource_manager import ResourceManager

class StatusWidget(QWidget):
    """Custom status widget showing file info and editor state."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the status widget UI."""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)  # Add some space between items
        
        # Create labels with monospace font
        font = QFont("Consolas", 9)
        
        self.file_label = QLabel("No file open")
        self.file_label.setFont(font)
        
        self.position_label = QLabel("Ln 1, Col 1")
        self.position_label.setFont(font)
        self.position_label.setMinimumWidth(100)
        
        self.encoding_label = QLabel("UTF-8")
        self.encoding_label.setFont(font)
        self.encoding_label.setMinimumWidth(50)
        
        self.line_ending_label = QLabel("LF")
        self.line_ending_label.setFont(font)
        self.line_ending_label.setMinimumWidth(40)
        
        self.scene_label = QLabel()
        self.scene_label.setFont(font)
        
        # Add stretch before labels to right-align them
        layout.addWidget(self.file_label)
        layout.addStretch()
        layout.addWidget(self.position_label)
        layout.addWidget(self.encoding_label)
        layout.addWidget(self.line_ending_label)
        layout.addWidget(self.scene_label)
        
        self.setLayout(layout)
        
    def update_file_info(self, filepath):
        """Update file information."""
        if filepath:
            self.file_label.setText(f"File: {os.path.basename(filepath)}")
            self.encoding_label.setText("UTF-8")
            self.detect_line_endings(filepath)
        else:
            self.file_label.setText("No file open")
            self.encoding_label.setText("")
            self.line_ending_label.setText("")
            
    def update_position(self, line, col):
        """Update cursor position."""
        self.position_label.setText(f"Ln {line}, Col {col}")
        
    def update_scene(self, scene_name):
        """Update current scene name."""
        if scene_name:
            self.scene_label.setText(f"Scene: {scene_name}")
        else:
            self.scene_label.setText("")
            
    def detect_line_endings(self, filepath):
        """Detect line endings in the file."""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
                if b'\r\n' in content:
                    self.line_ending_label.setText("CRLF")
                elif b'\n' in content:
                    self.line_ending_label.setText("LF")
                elif b'\r' in content:
                    self.line_ending_label.setText("CR")
                else:
                    self.line_ending_label.setText("")
        except:
            self.line_ending_label.setText("")

class EnhancedWindow(QMainWindow):
    """Enhanced main window with modern features."""
    
    MAX_RECENT_FILES = 10
    
    def __init__(self, grammar_manager=None):
        super().__init__()
        
        # Initialize managers
        self.grammar_manager = grammar_manager
        self.resource_manager = ResourceManager()
        
        # Initialize state
        self.current_file = None
        self.recent_files = []
        self.load_recent_files()
        
        # Create UI components
        self.editor_tabs = EditorTabs(self, grammar_manager, self)
        self.project_tree = ProjectTree()
        
        # Connect signals
        self.editor_tabs.currentFileChanged.connect(self.on_current_file_changed)
        self.project_tree.fileActivated.connect(self.open_file)
        
        # Initialize UI
        self.init_ui()
        
        # Load settings
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Casebook Editor")
        self.setGeometry(100, 100, 1024, 768)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Create file tree
        self.file_tree = ProjectTree()
        self.file_tree.fileActivated.connect(self.open_file)
        splitter.addWidget(self.file_tree)
        
        # Create editor tabs
        self.editor_tabs = EditorTabs(grammar_manager=self.grammar_manager, main_window=self)
        self.editor_tabs.currentFileChanged.connect(self.on_current_file_changed)
        splitter.addWidget(self.editor_tabs)
        
        # Set splitter sizes (30% tree, 70% editor)
        splitter.setSizes([300, 700])

        # Create UI elements
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_status_bar()
        
        # Set initial file tree root to current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.file_tree.set_root_path(project_root)

    def create_menu_bar(self):
        """Create the menu bar with all actions."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = self.create_action("&New", "Create a new file", QKeySequence.StandardKey.New, "new.png")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = self.create_action("&Open", "Open a file", QKeySequence.StandardKey.Open, "open.png")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        quick_open_action = self.create_action("Quick &Open", "Quickly open a file", "Ctrl+P", "open.png")
        quick_open_action.triggered.connect(self.quick_open)
        file_menu.addAction(quick_open_action)
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Recent Files")
        self.update_recent_menu()
        
        file_menu.addSeparator()
        
        save_action = self.create_action("&Save", "Save the current file", QKeySequence.StandardKey.Save, "save.png")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = self.create_action("Save &As", "Save as a new file", QKeySequence.StandardKey.SaveAs, "save.png")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = self.create_action("&Exit", "Exit the application", QKeySequence.StandardKey.Quit, "exit.png")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        # Create undo action
        self.undo_action = self.create_action("&Undo", "Undo last action", QKeySequence.StandardKey.Undo, "undo.png")
        self.undo_action.triggered.connect(self.undo)
        edit_menu.addAction(self.undo_action)
        
        # Create redo action
        self.redo_action = self.create_action("&Redo", "Redo last action", QKeySequence.StandardKey.Redo, "redo.png")
        self.redo_action.triggered.connect(self.redo)
        edit_menu.addAction(self.redo_action)
        
        edit_menu.addSeparator()
        
        # Create cut action
        self.cut_action = self.create_action("Cu&t", "Cut selection", QKeySequence.StandardKey.Cut, "cut.png")
        self.cut_action.triggered.connect(self.cut)
        edit_menu.addAction(self.cut_action)
        
        # Create copy action
        self.copy_action = self.create_action("&Copy", "Copy selection", QKeySequence.StandardKey.Copy, "copy.png")
        self.copy_action.triggered.connect(self.copy)
        edit_menu.addAction(self.copy_action)
        
        # Create paste action
        self.paste_action = self.create_action("&Paste", "Paste from clipboard", QKeySequence.StandardKey.Paste, "paste.png")
        self.paste_action.triggered.connect(self.paste)
        edit_menu.addAction(self.paste_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        # Create zoom actions
        zoom_in_action = self.create_action("Zoom &In", "Increase font size", QKeySequence.StandardKey.ZoomIn, "zoom-in.png")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = self.create_action("Zoom &Out", "Decrease font size", QKeySequence.StandardKey.ZoomOut, "zoom-out.png")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        view_menu.addSeparator()
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = self.create_action("&About", "About Casebook Editor", None, "about.png")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """Create the toolbar with common actions."""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # File operations
        new_action = self.create_action("New", "Create new file", QKeySequence.StandardKey.New, "new.png")
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        open_action = self.create_action("Open", "Open file", QKeySequence.StandardKey.Open, "open.png")
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        save_action = self.create_action("Save", "Save file", QKeySequence.StandardKey.Save, "save.png")
        save_action.triggered.connect(self.save_file)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # Edit operations
        cut_action = self.create_action("Cut", "Cut selection", QKeySequence.StandardKey.Cut, "cut.png")
        cut_action.triggered.connect(self.cut)
        toolbar.addAction(cut_action)
        
        copy_action = self.create_action("Copy", "Copy selection", QKeySequence.StandardKey.Copy, "copy.png")
        copy_action.triggered.connect(self.copy)
        toolbar.addAction(copy_action)
        
        paste_action = self.create_action("Paste", "Paste from clipboard", QKeySequence.StandardKey.Paste, "paste.png")
        paste_action.triggered.connect(self.paste)
        toolbar.addAction(paste_action)
        
        toolbar.addSeparator()
        
        # Undo/Redo
        undo_action = self.create_action("Undo", "Undo last action", QKeySequence.StandardKey.Undo, "undo.png")
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)
        
        redo_action = self.create_action("Redo", "Redo last action", QKeySequence.StandardKey.Redo, "redo.png")
        redo_action.triggered.connect(self.redo)
        toolbar.addAction(redo_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        zoom_out_action = self.create_action("Zoom Out", "Decrease font size", QKeySequence.StandardKey.ZoomOut, "zoom-out.png")
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(50, 200)
        self.zoom_spin.setValue(100)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.valueChanged.connect(self.zoom_changed)
        toolbar.addWidget(self.zoom_spin)
        
        zoom_in_action = self.create_action("Zoom In", "Increase font size", QKeySequence.StandardKey.ZoomIn, "zoom-in.png")
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
    def create_status_bar(self):
        """Create the status bar with file and editor information."""
        self.status_widget = StatusWidget()
        self.statusBar().addPermanentWidget(self.status_widget)
        
    def create_action(self, text, status_tip=None, shortcut=None, icon=None):
        """Create a QAction with the given properties."""
        action = QAction(text, self)
        if status_tip:
            action.setStatusTip(status_tip)
        if shortcut:
            if isinstance(shortcut, str):
                action.setShortcut(QKeySequence(shortcut))
            else:
                action.setShortcut(shortcut)
        if icon:
            icon_obj = self.resource_manager.get_icon(icon.replace('.png', ''))
            if icon_obj:
                action.setIcon(icon_obj)
        return action
        
    def on_current_file_changed(self, filepath):
        """Handle current file change."""
        # Update window title
        title = filepath if filepath else "Untitled"
        self.setWindowTitle(f"{title} - Casebook Editor")
        
        # Connect signals from current editor
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.cursorPositionChanged.connect(self.update_cursor_position)
            editor.sceneChanged.connect(self.update_scene)
            self.update_edit_actions()
        
    def update_cursor_position(self):
        """Update the cursor position in status bar."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            line, col = editor.getCursorPosition()
            self.status_widget.update_position(line + 1, col + 1)
        
    def update_scene(self, scene_name):
        """Update the current scene in status bar."""
        self.status_widget.update_scene(scene_name)
        
    def new_file(self):
        """Create a new file."""
        self.editor_tabs.addTab(self.editor_tabs.create_editor(), "Untitled")
        
    def open_file(self, filepath=None):
        """Open a file."""
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "Casebook Files (*.case);;All Files (*.*)"
            )
            
        if not filepath:
            return
            
        # Convert to absolute path
        filepath = os.path.abspath(filepath)
        
        try:
            # Check if file is already open
            for i in range(self.editor_tabs.count()):
                container = self.editor_tabs.widget(i)
                if container and self.editor_tabs.get_file_path(container.editor) == filepath:
                    self.editor_tabs.setCurrentIndex(i)
                    return
                    
            # Open new file
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Create new editor
            container, editor = self.editor_tabs.create_editor()
            editor.setText(content)
            
            # Add tab
            filename = os.path.basename(filepath)
            index = self.editor_tabs.addTab(container, filename)
            self.editor_tabs.setCurrentIndex(index)
            
            # Update file path
            self.editor_tabs.open_files[filepath] = editor
            
            # Start watching file
            self.editor_tabs.file_watcher.watch_file(filepath)
            
            # Add to recent files
            self.add_recent_file(filepath)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
            
    def save_file(self):
        """Save the current file."""
        self.editor_tabs.save_current_file()
            
    def save_file_as(self):
        """Save as a new file."""
        self.editor_tabs.save_current_file_as()
            
    def zoom_in(self):
        """Increase zoom level."""
        current = self.zoom_spin.value()
        self.zoom_spin.setValue(min(current + 10, 200))
        
    def zoom_out(self):
        """Decrease zoom level."""
        current = self.zoom_spin.value()
        self.zoom_spin.setValue(max(current - 10, 50))
        
    def zoom_changed(self, value):
        """Handle zoom level changes."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.set_zoom(value)

    def load_recent_files(self):
        """Load recent files list from settings."""
        # TODO: Load from settings file
        self.recent_files = []
        
    def save_recent_files(self):
        """Save recent files list to settings."""
        # TODO: Save to QSettings
        pass
        
    def add_recent_file(self, filepath):
        """Add a file to the recent files list."""
        if not filepath:
            return
            
        # Remove if already exists
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
            
        # Add to start of list
        self.recent_files.insert(0, filepath)
        
        # Keep only MAX_RECENT_FILES entries
        self.recent_files = self.recent_files[:self.MAX_RECENT_FILES]
        
        # Save and update menu
        self.save_recent_files()
        self.update_recent_menu()
        
    def update_recent_menu(self):
        """Update the recent files menu."""
        self.recent_menu.clear()
        
        if not self.recent_files:
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.recent_menu.addAction(no_files_action)
            return
            
        for filepath in self.recent_files:
            action = QAction(os.path.basename(filepath), self)
            action.setData(filepath)
            action.setStatusTip(filepath)
            action.triggered.connect(lambda checked, path=filepath: self.open_file(path))
            self.recent_menu.addAction(action)
            
        self.recent_menu.addSeparator()
        clear_action = QAction("Clear Recent Files", self)
        clear_action.triggered.connect(self.clear_recent_files)
        self.recent_menu.addAction(clear_action)
        
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.recent_files.clear()
        self.save_recent_files()
        self.update_recent_menu()
        
    def quick_open(self):
        """Show quick open dialog."""
        from .quick_open import QuickOpenDialog
        dialog = QuickOpenDialog(self.recent_files, self)
        dialog.fileSelected.connect(self.open_file)
        dialog.exec()

    def undo(self):
        """Undo last action."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.undo()
            
    def redo(self):
        """Redo last action."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.redo()
            
    def cut(self):
        """Cut selected text."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.cut()
            
    def copy(self):
        """Copy selected text."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.copy()
            
    def paste(self):
        """Paste clipboard text."""
        container = self.editor_tabs.currentWidget()
        if container:
            editor = container.editor
            editor.paste()
            
    def update_edit_actions(self):
        """Update edit action states based on current editor."""
        container = self.editor_tabs.currentWidget()
        has_editor = container is not None
        
        self.undo_action.setEnabled(has_editor and container.editor.isUndoAvailable())
        self.redo_action.setEnabled(has_editor and container.editor.isRedoAvailable())
        self.cut_action.setEnabled(has_editor and container.editor.hasSelectedText())
        self.copy_action.setEnabled(has_editor and container.editor.hasSelectedText())
        self.paste_action.setEnabled(has_editor)

    def load_settings(self):
        """Load application settings."""
        settings = QSettings("Codeium", "Casebook Editor")
        
        # Load window geometry
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Load window state
        state = settings.value("windowState")
        if state:
            self.restoreState(state)
            
        # Load recent files
        recent_files = settings.value("recentFiles", [])
        if recent_files:
            self.recent_files = recent_files
            self.update_recent_menu()
            
        # Load editor settings
        font_size = settings.value("fontSize", 12, type=int)
        self.editor_tabs.set_font_size(font_size)
        
        # Load zoom level
        zoom = settings.value("zoom", 100, type=int)
        if hasattr(self, 'zoom_spin'):
            self.zoom_spin.setValue(zoom)
            
    def save_settings(self):
        """Save application settings."""
        settings = QSettings("Codeium", "Casebook Editor")
        
        # Save window geometry and state
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
        # Save recent files
        settings.setValue("recentFiles", self.recent_files)
        
        # Save editor settings
        if hasattr(self, 'zoom_spin'):
            settings.setValue("zoom", self.zoom_spin.value())
            
        # Save font size
        editor = self.editor_tabs.currentWidget()
        if editor:
            settings.setValue("fontSize", editor.editor.font().pointSize())
            
    def closeEvent(self, event):
        """Handle window close event."""
        # Check for unsaved changes
        if self.editor_tabs.has_unsaved_changes():
            reply = QMessageBox.question(
                self,
                "Save Changes",
                "There are unsaved changes. Do you want to save them?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Yes:
                if not self.save_all_files():
                    event.ignore()
                    return
                    
        # Save settings
        self.save_settings()
        event.accept()
        
    def save_all_files(self):
        """Save all open files."""
        for i in range(self.editor_tabs.count()):
            container = self.editor_tabs.widget(i)
            if container and container.editor.isModified():
                if not self.save_file():
                    return False
        return True
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.information(self, "About Casebook Editor", "Casebook Editor is a modern text editor.")
