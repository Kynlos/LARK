"""Enhanced main window implementation."""

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QToolBar, QStatusBar,
    QLabel, QSpinBox, QComboBox, QHBoxLayout, QSplitter,
    QLineEdit, QDialog, QListWidget, QListWidgetItem,
    QDialogButtonBox, QProgressDialog
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QSettings
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont
from .file_tree import ProjectTree
from .editor_tabs import EditorTabs
from .search_dialog import SearchDialog
from .search_manager import SearchManager
from ..resources.resource_manager import ResourceManager
from ..utils.export_manager import ExportManager
from threading import Thread

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
        self.setObjectName("mainWindow")  # Set object name for QSettings
        
        # Initialize managers
        self.grammar_manager = grammar_manager
        self.resource_manager = ResourceManager()
        self.export_manager = ExportManager(self)
        
        # Initialize editor components
        self.editor_tabs = EditorTabs(self, grammar_manager, self)
        self.project_tree = ProjectTree(self)
        self.project_tree.fileActivated.connect(self.open_file)
        
        # Initialize search components
        self.search_dialog = None
        self.search_manager = None
        
        # Initialize state
        self.current_file = None
        self.recent_files = []
        
        # Create UI components first
        self.zoom_spin = QSpinBox()
        
        # Initialize UI
        self.setup_ui()
        self.setup_actions()
        self.setup_menus()
        self.setup_status_bar()
        
        # Connect signals
        self.editor_tabs.currentFileChanged.connect(self.on_current_file_changed)
        
        # Load settings
        self.load_settings()
        self.load_recent_files()
        
        # Set window properties
        self.setWindowTitle("Casebook Editor")
        self.setMinimumSize(800, 600)
        
    def setup_ui(self):
        """Initialize the user interface."""
        self.setGeometry(100, 100, 1024, 768)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create quick action container
        quick_action_container = QWidget()
        quick_action_container.setVisible(False)
        quick_action_layout = QVBoxLayout(quick_action_container)
        quick_action_layout.setContentsMargins(5, 5, 5, 5)
        quick_action_layout.setSpacing(0)
        self.quick_action_container = quick_action_container
        layout.addWidget(quick_action_container)
        
        # Create quick action bar
        self.quick_action_bar = QLineEdit()
        self.quick_action_bar.setPlaceholderText("Type to search files (Ctrl+P)")
        self.quick_action_bar.textChanged.connect(self.on_quick_action_text_changed)
        self.quick_action_bar.returnPressed.connect(self.handle_quick_action_select)
        self.quick_action_bar.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 3px;
                margin: 0;
                background: #f5f5f5;
                font-size: 14px;
            }
        """)
        quick_action_layout.addWidget(self.quick_action_bar)
        
        # Create results list
        self.quick_action_list = QListWidget()
        self.quick_action_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-top: none;
                border-radius: 0 0 3px 3px;
                background: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #e0e0e0;
                color: #000000;
            }
        """)
        self.quick_action_list.itemDoubleClicked.connect(self.handle_quick_action_select)
        self.quick_action_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.quick_action_list.setMaximumHeight(300)
        quick_action_layout.addWidget(self.quick_action_list)
        
        # Create editor container
        editor_container = QWidget()
        editor_layout = QHBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(editor_container)
        
        # Create splitter for tree and editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        editor_layout.addWidget(splitter)
        
        # Add file tree and editor tabs
        splitter.addWidget(self.project_tree)
        splitter.addWidget(self.editor_tabs)
        
        # Set splitter sizes (30% tree, 70% editor)
        splitter.setSizes([300, 700])
        
        # Set initial file tree root to current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
        self.project_tree.set_root_path(project_root)
        
    def setup_actions(self):
        """Set up the application's actions."""
        # File actions
        self.new_action = self.create_action("&New", "Create a new file", QKeySequence.StandardKey.New, "new.png")
        self.new_action.triggered.connect(self.new_file)
        
        self.open_action = self.create_action("&Open", "Open a file", QKeySequence.StandardKey.Open, "open.png")
        self.open_action.triggered.connect(self.open_file)
        
        self.quick_open_action = self.create_action("Quick &Open", "Quickly open a file", "Ctrl+P", "open.png")
        self.quick_open_action.triggered.connect(self.quick_open)
        
        # Recent files submenu
        self.recent_menu = QMenu("Recent Files")
        self.update_recent_menu()
        
        self.save_action = self.create_action("&Save", "Save the current file", QKeySequence.StandardKey.Save, "save.png")
        self.save_action.triggered.connect(self.save_file)
        
        self.save_as_action = self.create_action("Save &As", "Save as a new file", QKeySequence.StandardKey.SaveAs, "save.png")
        self.save_as_action.triggered.connect(self.save_file_as)
        
        self.exit_action = self.create_action("&Exit", "Exit the application", QKeySequence.StandardKey.Quit, "exit.png")
        self.exit_action.triggered.connect(self.close)
        
        # Edit actions
        self.cut_action = self.create_action("Cu&t", "Cut selection", QKeySequence.StandardKey.Cut, "cut.png")
        self.cut_action.triggered.connect(self.cut)
        
        self.copy_action = self.create_action("&Copy", "Copy selection", QKeySequence.StandardKey.Copy, "copy.png")
        self.copy_action.triggered.connect(self.copy)
        
        self.paste_action = self.create_action("&Paste", "Paste clipboard content", QKeySequence.StandardKey.Paste, "paste.png")
        self.paste_action.triggered.connect(self.paste)
        
        self.undo_action = self.create_action("&Undo", "Undo last action", QKeySequence.StandardKey.Undo, "undo.png")
        self.undo_action.triggered.connect(self.undo)
        
        self.redo_action = self.create_action("&Redo", "Redo last action", QKeySequence.StandardKey.Redo, "redo.png")
        self.redo_action.triggered.connect(self.redo)
        
        # Search actions
        self.find_action = self.create_action("&Find...", "Find text", QKeySequence.StandardKey.Find, "find.png")
        self.find_action.triggered.connect(self.show_find_dialog)
        
        self.replace_action = self.create_action("R&eplace...", "Replace text", QKeySequence.StandardKey.Replace, "replace.png")
        self.replace_action.triggered.connect(self.show_replace_dialog)
        
        # View actions
        self.zoom_in_action = self.create_action("Zoom &In", "Increase font size", QKeySequence.StandardKey.ZoomIn, "zoom-in.png")
        self.zoom_in_action.triggered.connect(self.zoom_in)
        
        self.zoom_out_action = self.create_action("Zoom &Out", "Decrease font size", QKeySequence.StandardKey.ZoomOut, "zoom-out.png")
        self.zoom_out_action.triggered.connect(self.zoom_out)
        
    def setup_menus(self):
        """Set up the application's menus."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.quick_open_action)
        file_menu.addMenu(self.recent_menu)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        
        # Export/Import submenu
        export_menu = file_menu.addMenu("Export/Import")
        
        # Export actions
        export_menu.addAction(self.create_action(
            "Export Project...",
            "Export project as ZIP",
            None,
            "export.png",
            self.export_project
        ))
        
        export_menu.addAction(self.create_action(
            "Export Settings...",
            "Export application settings",
            None,
            "settings.png",
            self.export_settings
        ))
        
        export_menu.addSeparator()
        
        # Import actions
        export_menu.addAction(self.create_action(
            "Import Project...",
            "Import project from ZIP",
            None,
            "import.png",
            self.import_project
        ))
        
        export_menu.addAction(self.create_action(
            "Import Settings...",
            "Import application settings",
            None,
            "settings.png",
            self.import_settings
        ))
        
        export_menu.addSeparator()
        
        # Export current file submenu
        export_file_menu = export_menu.addMenu("Export Current File As...")
        export_file_menu.addAction(self.create_action(
            "Plain Text...",
            "Export as .txt file",
            None,
            None,
            lambda: self.export_current_file('txt')
        ))
        export_file_menu.addAction(self.create_action(
            "HTML...",
            "Export as .html file",
            None,
            None,
            lambda: self.export_current_file('html')
        ))
        export_file_menu.addAction(self.create_action(
            "Markdown...",
            "Export as .md file",
            None,
            None,
            lambda: self.export_current_file('md')
        ))
        export_file_menu.addAction(self.create_action(
            "PDF...",
            "Export as .pdf file",
            None,
            None,
            lambda: self.export_current_file('pdf')
        ))
        
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.replace_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        view_menu.addAction(self.zoom_in_action)
        view_menu.addAction(self.zoom_out_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", "About Casebook Editor", None, "about.png")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Create the status bar with file and editor information."""
        self.status_widget = StatusWidget()
        self.statusBar().addPermanentWidget(self.status_widget)
        
    def create_tool_bar(self):
        """Create the main toolbar."""
        toolbar = QToolBar()
        toolbar.setObjectName("mainToolBar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        
        # Add actions
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.cut_action)
        toolbar.addAction(self.copy_action)
        toolbar.addAction(self.paste_action)
        toolbar.addSeparator()
        toolbar.addAction(self.undo_action)
        toolbar.addAction(self.redo_action)
        toolbar.addSeparator()
        toolbar.addAction(self.find_action)
        toolbar.addAction(self.replace_action)
        
        # Add zoom controls
        toolbar.addSeparator()
        toolbar.addAction(self.zoom_out_action)
        
        # Configure zoom spinbox
        self.zoom_spin.setMinimum(50)
        self.zoom_spin.setMaximum(200)
        self.zoom_spin.setValue(100)
        self.zoom_spin.setSuffix("%")
        self.zoom_spin.setFixedWidth(70)
        self.zoom_spin.valueChanged.connect(self.zoom_changed)
        toolbar.addWidget(self.zoom_spin)
        
        toolbar.addAction(self.zoom_in_action)
        
        self.addToolBar(toolbar)
        return toolbar
        
    def create_action(self, text, status_tip=None, shortcut=None, icon=None, slot=None):
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
        if slot:
            action.triggered.connect(slot)
        return action
        
    def update_window_title(self):
        """Update the window title with current file."""
        current = self.editor_tabs.currentWidget()
        if current:
            filepath = current.get_file_path()
            if filepath:
                title = f"{os.path.basename(filepath)} - Casebook Editor"
            else:
                title = "Untitled - Casebook Editor"
        else:
            title = "Casebook Editor"
            
        self.setWindowTitle(title)
        
    def on_current_file_changed(self, filepath):
        """Handle current file change."""
        self.update_window_title()
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
        filepath, _ = QFileDialog.getSaveFileName(
            self, "New File", "",
            "Casebook Files (*.case);;Python Files (*.py);;All Files (*.*)"
        )
        
        if filepath:
            # Create new editor with appropriate lexer
            container, editor = self.editor_tabs.create_editor(filepath)
            
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
            
    def open_file(self, filepath=None):
        """Open a file in the editor."""
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(
                self, "Open File", "",
                "Casebook Files (*.case);;All Files (*.*)"
            )
            
        if not filepath:
            return
            
        if not os.path.exists(filepath):
            QMessageBox.warning(
                self,
                "File Not Found",
                f"Could not find file:\n{filepath}"
            )
            return
            
        try:
            editor = self.editor_tabs.open_file(filepath)
            if editor:
                self.add_recent_file(filepath)
                self.update_window_title()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Opening File",
                f"Could not open file: {filepath}\n\nError: {str(e)}"
            )
            
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
        self.quick_action_container.setVisible(True)
        self.quick_action_bar.setFocus()
        self.quick_action_bar.clear()
        self.quick_action_list.clear()
        
    def on_quick_action_text_changed(self, text):
        """Handle quick action text changes."""
        self.quick_action_list.clear()
        
        if not text.strip():
            return
            
        # Search for files
        matching_files = []
        root_dir = self.project_tree.root_path
        search_text = text.lower()
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if search_text in file.lower():
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    
                    # Create item with relative path
                    item = QListWidgetItem(rel_path)
                    item.setData(Qt.ItemDataRole.UserRole, full_path)
                    
                    # Add icon based on file type
                    # TODO: Add file type icons
                    
                    self.quick_action_list.addItem(item)
                    
                    # Limit to first 50 matches for performance
                    if self.quick_action_list.count() >= 50:
                        return
        
        # Select first item if there are results
        if self.quick_action_list.count() > 0:
            self.quick_action_list.setCurrentRow(0)
            
    def handle_quick_action_select(self):
        """Handle quick action selection."""
        current_item = self.quick_action_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.ItemDataRole.UserRole)
            self.quick_action_container.setVisible(False)
            self.open_file(file_path)
        else:
            self.quick_action_container.setVisible(False)
            
    def keyPressEvent(self, event):
        """Handle key press events."""
        if self.quick_action_container.isVisible():
            if event.key() == Qt.Key.Key_Escape:
                self.quick_action_container.setVisible(False)
            elif event.key() == Qt.Key.Key_Up:
                current_row = self.quick_action_list.currentRow()
                if current_row > 0:
                    self.quick_action_list.setCurrentRow(current_row - 1)
                event.accept()
            elif event.key() == Qt.Key.Key_Down:
                current_row = self.quick_action_list.currentRow()
                if current_row < self.quick_action_list.count() - 1:
                    self.quick_action_list.setCurrentRow(current_row + 1)
                event.accept()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)
            
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
        """Update edit action states."""
        has_editor = False
        container = self.editor_tabs.currentWidget()
        if container:
            has_editor = True
            editor = container.editor
            
        # Update edit actions
        self.undo_action.setEnabled(has_editor and editor.isUndoAvailable())
        self.redo_action.setEnabled(has_editor and editor.isRedoAvailable())
        self.cut_action.setEnabled(has_editor and editor.hasSelectedText())
        self.copy_action.setEnabled(has_editor and editor.hasSelectedText())
        self.paste_action.setEnabled(has_editor)

    def load_settings(self):
        """Load application settings."""
        settings = QSettings('Codeium', 'Casebook Editor')
        
        # Window geometry
        geometry = settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
            
        # Window state
        state = settings.value('windowState')
        if state:
            self.restoreState(state)
            
        # Recent files
        recent_files = settings.value('recentFiles', [])
        if recent_files:
            self.recent_files = recent_files
            self.update_recent_menu()
            
        # Font size
        font_size = settings.value('fontSize', 10, type=int)
        if font_size and hasattr(self, 'editor_tabs'):
            self.editor_tabs.update_font_size(font_size)
            
        # Toolbar visibility
        toolbar_visible = settings.value('toolbarVisible', True, type=bool)
        if hasattr(self, 'toolbar') and self.toolbar:
            self.toolbar.setVisible(toolbar_visible)
            
    def save_settings(self):
        """Save application settings."""
        settings = QSettings('Codeium', 'Casebook Editor')
        
        # Window geometry and state
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        
        # Recent files
        settings.setValue('recentFiles', self.recent_files)
        
        # Font size
        if hasattr(self, 'editor_tabs'):
            current = self.editor_tabs.currentWidget()
            if current and current.editor:
                font_size = current.editor.font().pointSize()
                settings.setValue('fontSize', font_size)
            
        # Toolbar visibility
        if hasattr(self, 'toolbar') and self.toolbar:
            settings.setValue('toolbarVisible', self.toolbar.isVisible())
            
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

    def show_find_dialog(self):
        """Show the find dialog."""
        if not self.search_dialog:
            self.search_dialog = SearchDialog(self)
            self.search_manager = SearchManager(self.editor_tabs)
            
            # Connect signals
            self.search_dialog.searchRequested.connect(
                lambda params: self.search_manager.search(params, self.search_dialog)
            )
            self.search_dialog.replaceRequested.connect(
                lambda params: self.handle_replace(params)
            )
            
        self.search_dialog.show()
        self.search_dialog.activateWindow()
        self.search_dialog.raise_()
        
    def show_replace_dialog(self):
        """Show the replace dialog."""
        if not self.search_dialog:
            self.show_find_dialog()
        self.search_dialog.show()
        self.search_dialog.activateWindow()
        self.search_dialog.raise_()
        # Switch to replace tab
        self.search_dialog.setCurrentIndex(1)
        
    def handle_replace(self, params):
        """Handle replace operations."""
        if not self.search_manager:
            return
            
        if params.get('preview_only'):
            self.search_manager.preview_replace(params, self.search_dialog)
        else:
            count = self.search_manager.replace_all(params)
            if count > 0:
                self.statusBar().showMessage(f"Replaced {count} occurrence{'s' if count > 1 else ''}")
            else:
                self.statusBar().showMessage("No replacements made")

    def export_project(self):
        """Export the entire project."""
        try:
            project_path = self.project_tree.root_path
            if not project_path:
                QMessageBox.warning(self, "Export Error", "No project directory selected.")
                return
                
            # Show progress dialog
            self.progress_dialog = QProgressDialog("Exporting project...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)
            
            # Start export
            self.export_manager.export_project(project_path)
            # Connect to worker's signals after it's created
            self.export_manager.worker.finished.connect(self.on_export_finished)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            
    def export_current_file(self, export_format):
        """Export current file in specified format."""
        try:
            current_file = self.editor_tabs.get_current_file()
            if not current_file:
                QMessageBox.warning(self, "Export Error", "No file is currently open.")
                return
                
            # Get save path from user
            file_formats = {
                'txt': ('Text Files', '*.txt'),
                'html': ('HTML Files', '*.html'),
                'md': ('Markdown Files', '*.md'),
                'pdf': ('PDF Files', '*.pdf')
            }
            
            format_info = file_formats.get(export_format, ('All Files', '*.*'))
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"Export as {export_format.upper()}",
                os.path.splitext(current_file)[0] + f".{export_format}",
                f"{format_info[0]} (*.{export_format})"
            )
            
            if not file_path:
                return
                
            # Show progress dialog for larger files
            self.progress_dialog = QProgressDialog(f"Exporting to {export_format.upper()}...", "Cancel", 0, 100, self)
            self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setValue(0)
            
            # Start export
            self.export_manager.export_file(current_file, export_format, file_path)
            # Connect to worker's signals after it's created
            self.export_manager.worker.finished.connect(self.on_export_finished)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            
    def on_export_finished(self, success, path, error):
        """Handle export completion."""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            delattr(self, 'progress_dialog')
            
        if success:
            QMessageBox.information(
                self,
                "Export Successful",
                f"File exported to:\n{path}"
            )
        else:
            QMessageBox.critical(self, "Export Error", error)
            
    def import_project(self):
        """Import a project from backup."""
        zip_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Project",
            "",
            "ZIP Files (*.zip)"
        )
        
        if not zip_path:
            return
            
        target_dir, _ = QFileDialog.getSaveFileName(
            self,
            "Select Import Location",
            "",
            "Directory"
        )
        
        if not target_dir:
            return
            
        try:
            imported_path = self.export_manager.import_project(zip_path, target_dir)
            QMessageBox.information(
                self,
                "Import Successful",
                f"Project imported to:\n{imported_path}"
            )
            
            # Ask if user wants to open the imported project
            reply = QMessageBox.question(
                self,
                "Open Project",
                "Would you like to open the imported project?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.project_tree.set_root_path(imported_path)
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))
            
    def export_settings(self):
        """Export application settings."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Settings",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            self.export_manager.export_settings(file_path)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Settings exported to:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))
            
    def import_settings(self):
        """Import application settings."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Settings",
            "",
            "JSON Files (*.json)"
        )
        
        if not file_path:
            return
            
        try:
            self.export_manager.import_settings(file_path)
            QMessageBox.information(
                self,
                "Import Successful",
                "Settings imported successfully.\nSome changes may require a restart."
            )
        except Exception as e:
            QMessageBox.critical(self, "Import Error", str(e))
