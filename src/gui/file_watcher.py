"""File system watcher for detecting external changes."""

import os
from PyQt6.QtCore import QFileSystemWatcher, QObject, pyqtSignal

class FileWatcher(QObject):
    """Watches files for external changes."""
    
    fileChanged = pyqtSignal(str)  # Signal emitted when a file changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self.on_file_changed)
        self.watched_files = set()
        
    def watch_file(self, filepath):
        """Start watching a file."""
        if filepath and os.path.exists(filepath):
            self.watcher.addPath(filepath)
            self.watched_files.add(filepath)
            
    def unwatch_file(self, filepath):
        """Stop watching a file."""
        if filepath in self.watched_files:
            self.watcher.removePath(filepath)
            self.watched_files.remove(filepath)
            
    def on_file_changed(self, filepath):
        """Handle file change event."""
        # Re-add the file to the watcher if it still exists
        # (needed because some editors save by deleting and recreating the file)
        if os.path.exists(filepath):
            self.watcher.addPath(filepath)
            self.fileChanged.emit(filepath)
