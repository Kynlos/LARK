"""Quick file opener dialog."""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence

class QuickOpenDialog(QDialog):
    """Dialog for quickly opening files."""
    
    fileSelected = pyqtSignal(str)  # Signal emitted when a file is selected
    
    def __init__(self, recent_files=None, parent=None):
        super().__init__(parent)
        self.recent_files = recent_files or []
        self.matching_files = []
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("Quick Open")
        self.setModal(True)
        self.resize(500, 400)
        
        # Create layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type to search files...")
        self.search_box.textChanged.connect(self.update_results)
        layout.addWidget(self.search_box)
        
        # Create results list
        self.results_list = QListWidget()
        self.results_list.itemActivated.connect(self.on_item_activated)
        layout.addWidget(self.results_list)
        
        # Populate initial results
        self.update_results()
        
        # Set focus to search box
        self.search_box.setFocus()
        
    def update_results(self):
        """Update the results list based on search text."""
        self.results_list.clear()
        search_text = self.search_box.text().lower()
        
        # Filter files based on search text
        self.matching_files = []
        for filepath in self.recent_files:
            filename = os.path.basename(filepath)
            if search_text in filename.lower():
                self.matching_files.append(filepath)
                item = QListWidgetItem(f"{filename} - {filepath}")
                self.results_list.addItem(item)
                
        # Select first item if available
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)
            
    def on_item_activated(self, item):
        """Handle item activation."""
        index = self.results_list.currentRow()
        if 0 <= index < len(self.matching_files):
            self.fileSelected.emit(self.matching_files[index])
            self.accept()
            
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Return and self.results_list.currentItem():
            self.on_item_activated(self.results_list.currentItem())
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
