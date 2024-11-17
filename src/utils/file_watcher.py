"""File system watcher for monitoring file changes."""

import os
from PyQt6.QtCore import QObject, QFileSystemWatcher, pyqtSignal

class FileWatcher(QObject):
    """Watches files for external changes."""
    
    fileChanged = pyqtSignal(str)  # Signal emitted when a file changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher(self)
        self.watcher.fileChanged.connect(self._on_file_changed)
        self.watched_files = set()
        
    def watch_file(self, filepath):
        """Start watching a file."""
        if not filepath or not os.path.exists(filepath):
            return False
            
        # Add to watcher
        if filepath not in self.watched_files:
            self.watcher.addPath(filepath)
            self.watched_files.add(filepath)
        return True
        
    def unwatch_file(self, filepath):
        """Stop watching a file."""
        if filepath in self.watched_files:
            self.watcher.removePath(filepath)
            self.watched_files.remove(filepath)
            
    def _on_file_changed(self, filepath):
        """Handle file change event."""
        # Re-add the file to the watcher if it still exists
        # This is needed because some editors remove and recreate files when saving
        if os.path.exists(filepath):
            self.watcher.addPath(filepath)
            
        self.fileChanged.emit(filepath)
        
    def clear(self):
        """Stop watching all files."""
        if self.watched_files:
            self.watcher.removePaths(list(self.watched_files))
            self.watched_files.clear()
