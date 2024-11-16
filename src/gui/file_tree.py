"""File tree widget for project navigation."""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QTreeView, QMenu,
    QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QStandardItemModel, QStandardItem

class ProjectTree(QTreeView):
    """Tree view showing project files."""
    
    fileActivated = pyqtSignal(str)  # Signal emitted when a file is activated
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Name'])
        self.setModel(self.model)
        self.root_path = None
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI."""
        # Set selection mode
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        
        # Set other properties
        self.setAnimated(True)
        self.setSortingEnabled(True)
        self.setIndentation(20)
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)
        
        # Connect signals
        self.doubleClicked.connect(self.on_double_click)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def set_root_path(self, path):
        """Set the root path for the tree."""
        if not os.path.exists(path):
            return
            
        self.root_path = path
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Name'])
        
        root_path = Path(path)
        root_item = self._create_tree_item(root_path)
        if root_item:
            self.model.appendRow(root_item)
            self.expandToDepth(0)
        
    def _create_tree_item(self, path):
        """Create a tree item for a path."""
        try:
            name = path.name or str(path)
            item = QStandardItem(name)
            item.setData(str(path), Qt.ItemDataRole.UserRole)
            
            if path.is_dir():
                # Add directories first
                dirs = []
                files = []
                for child in path.iterdir():
                    if child.name.startswith('.'):
                        continue
                    if child.is_dir():
                        dirs.append(child)
                    else:
                        files.append(child)
                        
                # Sort and add items
                for child in sorted(dirs, key=lambda x: x.name.lower()):
                    child_item = self._create_tree_item(child)
                    if child_item:
                        item.appendRow(child_item)
                        
                for child in sorted(files, key=lambda x: x.name.lower()):
                    child_item = self._create_tree_item(child)
                    if child_item:
                        item.appendRow(child_item)
                        
            return item
            
        except PermissionError:
            return None
        
    def get_item_path(self, index):
        """Get the file path for an item."""
        if not index.isValid():
            return None
        return self.model.data(index, Qt.ItemDataRole.UserRole)
        
    def on_double_click(self, index):
        """Handle double click on tree item."""
        path = self.get_item_path(index)
        if path and os.path.isfile(path):
            self.fileActivated.emit(path)
            
    def show_context_menu(self, position):
        """Show context menu for tree item."""
        index = self.indexAt(position)
        if not index.isValid():
            return
            
        path = self.get_item_path(index)
        if not path:
            return
            
        is_file = os.path.isfile(path)
        
        menu = QMenu()
        
        # Add actions based on item type
        if is_file:
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.fileActivated.emit(path))
            menu.addAction(open_action)
        
        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_item(index))
        menu.addAction(rename_action)
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(index))
        menu.addAction(delete_action)
        
        menu.exec(self.viewport().mapToGlobal(position))
        
    def rename_item(self, index):
        """Rename the selected item."""
        old_path = self.get_item_path(index)
        if not old_path:
            return
            
        old_name = os.path.basename(old_path)
        
        new_name, ok = QInputDialog.getText(
            self, "Rename", "New name:", text=old_name
        )
        
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            try:
                os.rename(old_path, new_path)
                # Update tree after rename
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not rename: {str(e)}")
                
    def delete_item(self, index):
        """Delete the selected item."""
        path = self.get_item_path(index)
        if not path:
            return
            
        name = os.path.basename(path)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    os.rmdir(path)
                # Update tree after delete
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete: {str(e)}")
                
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Delete:
            indexes = self.selectedIndexes()
            if indexes:
                self.delete_item(indexes[0])
        else:
            super().keyPressEvent(event)
            
    def refresh(self):
        """Refresh the tree view."""
        if self.root_path:
            self.set_root_path(self.root_path)
