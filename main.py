"""Main entry point for the Casebook Editor."""

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.grammar import GrammarManager
from src.gui import EnhancedWindow

def main():
    """Main entry point."""
    # Create application
    app = QApplication(sys.argv)
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Set up grammar manager
    grammar_manager = GrammarManager()
    override_path = Path(__file__).parent / 'casebook.override.lark'
    grammar_manager.load_override_grammar(str(override_path))
    
    # Create main window
    window = EnhancedWindow(grammar_manager)
    window.show()
    
    # Create initial editor
    container, editor = window.editor_tabs.create_editor()
    window.editor_tabs.addTab(container, "Untitled")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
