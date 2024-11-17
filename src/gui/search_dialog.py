"""Search and Replace dialog implementation."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QComboBox,
    QTabWidget, QWidget, QListWidget, QSplitter,
    QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
import re

class SearchDialog(QDialog):
    """Advanced search and replace dialog."""
    
    searchRequested = pyqtSignal(dict)  # Emits search parameters
    replaceRequested = pyqtSignal(dict)  # Emits replace parameters
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find and Replace")
        self.resize(600, 400)
        
        # Initialize settings
        self.settings = QSettings("Codeium", "Casebook Editor")
        self.search_history = self.settings.value("searchHistory", []) or []
        self.replace_history = self.settings.value("replaceHistory", []) or []
        
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_search_tab(), "Search")
        tab_widget.addTab(self.create_replace_tab(), "Replace")
        layout.addWidget(tab_widget)
        
    def create_search_tab(self):
        """Create the search tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QComboBox()
        self.search_input.setEditable(True)
        self.search_input.setMaxCount(20)
        self.search_input.addItems(self.search_history)
        self.search_input.setMinimumWidth(300)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Case sensitive")
        self.whole_word = QCheckBox("Whole word")
        self.regex = QCheckBox("Regular expression")
        self.multi_file = QCheckBox("Search in all files")
        
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_word)
        options_layout.addWidget(self.regex)
        options_layout.addWidget(self.multi_file)
        layout.addLayout(options_layout)
        
        # Splitter for results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemSelectionChanged.connect(self.on_result_selected)
        splitter.addWidget(self.results_list)
        
        # Preview
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        splitter.addWidget(self.preview)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find)
        button_layout.addWidget(find_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_search)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        return tab
        
    def create_replace_tab(self):
        """Create the replace tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.replace_search_input = QComboBox()
        self.replace_search_input.setEditable(True)
        self.replace_search_input.setMaxCount(20)
        self.replace_search_input.addItems(self.search_history)
        self.replace_search_input.setMinimumWidth(300)
        search_layout.addWidget(self.replace_search_input)
        layout.addLayout(search_layout)
        
        # Replace input
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QComboBox()
        self.replace_input.setEditable(True)
        self.replace_input.setMaxCount(20)
        self.replace_input.addItems(self.replace_history)
        self.replace_input.setMinimumWidth(300)
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Replace options
        options_layout = QHBoxLayout()
        self.replace_case_sensitive = QCheckBox("Case sensitive")
        self.replace_whole_word = QCheckBox("Whole word")
        self.replace_regex = QCheckBox("Regular expression")
        self.replace_multi_file = QCheckBox("Replace in all files")
        
        options_layout.addWidget(self.replace_case_sensitive)
        options_layout.addWidget(self.replace_whole_word)
        options_layout.addWidget(self.replace_regex)
        options_layout.addWidget(self.replace_multi_file)
        layout.addLayout(options_layout)
        
        # Splitter for results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results list
        self.replace_results_list = QListWidget()
        self.replace_results_list.itemSelectionChanged.connect(self.on_replace_result_selected)
        splitter.addWidget(self.replace_results_list)
        
        # Preview
        self.replace_preview = QTextEdit()
        self.replace_preview.setReadOnly(True)
        splitter.addWidget(self.replace_preview)
        
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview_replace)
        button_layout.addWidget(preview_button)
        
        replace_button = QPushButton("Replace")
        replace_button.clicked.connect(self.replace)
        button_layout.addWidget(replace_button)
        
        replace_all_button = QPushButton("Replace All")
        replace_all_button.clicked.connect(self.replace_all)
        button_layout.addWidget(replace_all_button)
        
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_replace)
        button_layout.addWidget(clear_button)
        
        layout.addLayout(button_layout)
        
        return tab
        
    def find(self):
        """Perform search operation."""
        search_text = self.search_input.currentText()
        if not search_text:
            return
            
        # Add to history if not already present
        if search_text not in self.search_history:
            self.search_history.insert(0, search_text)
            self.search_history = self.search_history[:20]  # Keep last 20
            self.search_input.clear()
            self.search_input.addItems(self.search_history)
            self.settings.setValue("searchHistory", self.search_history)
        
        # Prepare search parameters
        params = {
            'text': search_text,
            'case_sensitive': self.case_sensitive.isChecked(),
            'whole_word': self.whole_word.isChecked(),
            'regex': self.regex.isChecked(),
            'multi_file': self.multi_file.isChecked()
        }
        
        self.searchRequested.emit(params)
        
    def preview_replace(self):
        """Preview replace operation."""
        search_text = self.replace_search_input.currentText()
        replace_text = self.replace_input.currentText()
        
        if not search_text:
            return
            
        # Add to history if not already present
        if search_text not in self.search_history:
            self.search_history.insert(0, search_text)
            self.search_history = self.search_history[:20]
            self.replace_search_input.clear()
            self.replace_search_input.addItems(self.search_history)
            self.settings.setValue("searchHistory", self.search_history)
            
        if replace_text not in self.replace_history:
            self.replace_history.insert(0, replace_text)
            self.replace_history = self.replace_history[:20]
            self.replace_input.clear()
            self.replace_input.addItems(self.replace_history)
            self.settings.setValue("replaceHistory", self.replace_history)
        
        # Prepare replace parameters
        params = {
            'search_text': search_text,
            'replace_text': replace_text,
            'case_sensitive': self.replace_case_sensitive.isChecked(),
            'whole_word': self.replace_whole_word.isChecked(),
            'regex': self.replace_regex.isChecked(),
            'multi_file': self.replace_multi_file.isChecked(),
            'preview_only': True
        }
        
        self.replaceRequested.emit(params)
        
    def replace(self):
        """Perform replace operation on current selection."""
        params = self.get_replace_params()
        params['selected_only'] = True
        params['preview_only'] = False
        self.replaceRequested.emit(params)
        
    def replace_all(self):
        """Perform replace operation on all matches."""
        params = self.get_replace_params()
        params['selected_only'] = False
        params['preview_only'] = False
        
        # Confirm replace all
        reply = QMessageBox.question(
            self,
            "Replace All",
            "Are you sure you want to replace all occurrences?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.replaceRequested.emit(params)
        
    def get_replace_params(self):
        """Get replace parameters."""
        return {
            'search_text': self.replace_search_input.currentText(),
            'replace_text': self.replace_input.currentText(),
            'case_sensitive': self.replace_case_sensitive.isChecked(),
            'whole_word': self.replace_whole_word.isChecked(),
            'regex': self.replace_regex.isChecked(),
            'multi_file': self.replace_multi_file.isChecked()
        }
        
    def on_result_selected(self):
        """Handle search result selection."""
        item = self.results_list.currentItem()
        if item:
            self.preview.setText(item.data(Qt.ItemDataRole.UserRole))
            
    def on_replace_result_selected(self):
        """Handle replace result selection."""
        item = self.replace_results_list.currentItem()
        if item:
            self.replace_preview.setText(item.data(Qt.ItemDataRole.UserRole))
            
    def clear_search(self):
        """Clear search results."""
        self.search_input.clearEditText()
        self.results_list.clear()
        self.preview.clear()
        
    def clear_replace(self):
        """Clear replace results."""
        self.replace_search_input.clearEditText()
        self.replace_input.clearEditText()
        self.replace_results_list.clear()
        self.replace_preview.clear()
        
    def load_settings(self):
        """Load dialog settings."""
        geometry = self.settings.value("searchDialog/geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        self.case_sensitive.setChecked(self.settings.value("searchDialog/caseSensitive", False, type=bool))
        self.whole_word.setChecked(self.settings.value("searchDialog/wholeWord", False, type=bool))
        self.regex.setChecked(self.settings.value("searchDialog/regex", False, type=bool))
        self.multi_file.setChecked(self.settings.value("searchDialog/multiFile", False, type=bool))
        
    def save_settings(self):
        """Save dialog settings."""
        self.settings.setValue("searchDialog/geometry", self.saveGeometry())
        self.settings.setValue("searchDialog/caseSensitive", self.case_sensitive.isChecked())
        self.settings.setValue("searchDialog/wholeWord", self.whole_word.isChecked())
        self.settings.setValue("searchDialog/regex", self.regex.isChecked())
        self.settings.setValue("searchDialog/multiFile", self.multi_file.isChecked())
        
    def closeEvent(self, event):
        """Handle dialog close event."""
        self.save_settings()
        super().closeEvent(event)
