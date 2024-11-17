"""Container widget for editor and additional components."""

from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt
from ..editor.editor import CasebookEditor

class EditorContainer(QWidget):
    """Container for editor and additional components."""
    
    def __init__(self, parent=None, grammar_manager=None):
        super().__init__(parent)
        self.file_path = None
        self.editor = CasebookEditor(self, grammar_manager)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add editor
        layout.addWidget(self.editor)
        
        # Set layout properties
        self.setLayout(layout)
        
    def set_file_path(self, path):
        """Set the file path and update editor settings."""
        self.file_path = path
        if path:
            # Update editor settings based on file type
            self.editor.setup_lexer(path)
            
    def get_file_path(self):
        """Get the current file path."""
        return self.file_path
