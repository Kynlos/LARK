"""Main window implementation for the Casebook Editor."""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QMenuBar, QMenu, 
    QFileDialog, QMessageBox, QToolBar, QStatusBar
)
from PyQt6.QtGui import QAction, QKeySequence, QIcon
from PyQt6.QtCore import Qt, QSize

class MainWindow(QMainWindow):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.current_file = None
        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Casebook Editor")
        self.setGeometry(100, 100, 1024, 768)

        # Create central widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_tool_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_menu_bar(self):
        """Create the menu bar with all actions."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence(QKeySequence.StandardKey.New))
        new_action.setStatusTip("Create a new file")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open", self)
        open_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Open))
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Save))
        save_action.setStatusTip("Save the current file")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence(QKeySequence.StandardKey.SaveAs))
        save_as_action.setStatusTip("Save the current file with a new name")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Quit))
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Undo))
        undo_action.setStatusTip("Undo the last action")
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Redo))
        redo_action.setStatusTip("Redo the last undone action")
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Cut))
        cut_action.setStatusTip("Cut the selected text")
        cut_action.triggered.connect(self.editor.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Copy))
        copy_action.setStatusTip("Copy the selected text")
        copy_action.triggered.connect(self.editor.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence(QKeySequence.StandardKey.Paste))
        paste_action.setStatusTip("Paste text from the clipboard")
        paste_action.triggered.connect(self.editor.paste)
        edit_menu.addAction(paste_action)
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence(QKeySequence.StandardKey.SelectAll))
        select_all_action.setStatusTip("Select all text")
        select_all_action.triggered.connect(self.editor.selectAll)
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        toggle_line_numbers = QAction("Line &Numbers", self)
        toggle_line_numbers.setCheckable(True)
        toggle_line_numbers.setChecked(True)
        toggle_line_numbers.setStatusTip("Toggle line numbers")
        toggle_line_numbers.triggered.connect(self.toggle_line_numbers)
        view_menu.addAction(toggle_line_numbers)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("Show the application's About box")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_tool_bar(self):
        """Create the toolbar with common actions."""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Add actions (you can add icons later)
        toolbar.addAction("New", self.new_file)
        toolbar.addAction("Open", self.open_file)
        toolbar.addAction("Save", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction("Undo", self.editor.undo)
        toolbar.addAction("Redo", self.editor.redo)
        toolbar.addSeparator()
        toolbar.addAction("Cut", self.editor.cut)
        toolbar.addAction("Copy", self.editor.copy)
        toolbar.addAction("Paste", self.editor.paste)

    def new_file(self):
        """Create a new file."""
        if self.maybe_save():
            self.editor.clear()
            self.current_file = None
            self.setWindowTitle("Casebook Editor - Untitled")
            self.status_bar.showMessage("Created new file")

    def open_file(self):
        """Open an existing file."""
        if self.maybe_save():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "",
                "Casebook Files (*.case);;All Files (*.*)"
            )
            if filename:
                self.load_file(filename)

    def load_file(self, filename):
        """Load a file into the editor."""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                text = f.read()
            self.editor.setText(text)
            self.current_file = filename
            self.setWindowTitle(f"Casebook Editor - {os.path.basename(filename)}")
            self.status_bar.showMessage(f"Loaded {filename}")
            return True
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Could not load file {filename}:\n{str(e)}"
            )
            return False

    def save_file(self):
        """Save the current file."""
        if self.current_file:
            return self.save_file_as(self.current_file)
        return self.save_file_as()

    def save_file_as(self, filename=None):
        """Save the current file with a new name."""
        if not filename:
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "",
                "Casebook Files (*.case);;All Files (*.*)"
            )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.editor.text())
                self.current_file = filename
                self.setWindowTitle(f"Casebook Editor - {os.path.basename(filename)}")
                self.status_bar.showMessage(f"Saved {filename}")
                return True
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not save file {filename}:\n{str(e)}"
                )
        return False

    def maybe_save(self):
        """Check if we need to save changes."""
        if not self.editor.isModified():
            return True

        ret = QMessageBox.warning(
            self,
            "Casebook Editor",
            "The document has been modified.\nDo you want to save your changes?",
            QMessageBox.StandardButton.Save |
            QMessageBox.StandardButton.Discard |
            QMessageBox.StandardButton.Cancel
        )

        if ret == QMessageBox.StandardButton.Save:
            return self.save_file()
        elif ret == QMessageBox.StandardButton.Cancel:
            return False
        return True

    def toggle_line_numbers(self, checked):
        """Toggle the visibility of line numbers."""
        if checked:
            self.editor.setMarginWidth(0, 50)
        else:
            self.editor.setMarginWidth(0, 0)

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Casebook Editor",
            "Casebook Editor\n\n"
            "A sophisticated editor for the Casebook interactive narrative language.\n\n"
            "Features:\n"
            "- Syntax highlighting\n"
            "- Code folding\n"
            "- Auto-indentation\n"
            "- File operations\n"
            "- Customizable grammar"
        )

    def closeEvent(self, event):
        """Handle the window close event."""
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()
