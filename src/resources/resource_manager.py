"""Resource manager for the application."""

import os
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import Qt
from PyQt6.QtSvg import QSvgRenderer

class ResourceManager:
    """Manages application resources like icons."""
    
    def __init__(self):
        self.resource_dir = Path(__file__).parent
        self.icon_dir = self.resource_dir / 'icons'
        self.icons = {}
        self._load_icons()
    
    def _load_icons(self):
        """Load all icons from the icons directory."""
        if not self.icon_dir.exists():
            return
            
        for icon_file in self.icon_dir.glob('*.svg'):
            name = icon_file.stem
            icon = QIcon()
            
            # Load SVG file
            renderer = QSvgRenderer(str(icon_file))
            pixmap = QPixmap(16, 16)  # Size for toolbar icons
            pixmap.fill(Qt.GlobalColor.transparent)
            
            # Render SVG to pixmap
            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()
            
            # Add pixmap to icon
            icon.addPixmap(pixmap)
            self.icons[name] = icon
        
        for icon_file in self.icon_dir.glob('*.png'):
            name = icon_file.stem
            icon = QIcon(str(icon_file))
            # Enable automatic color inversion for dark theme
            icon.setIsMask(True)
            self.icons[name] = icon
    
    def get_icon(self, name):
        """Get an icon by name."""
        return self.icons.get(name)

    def get_all_icons(self):
        """Get all loaded icons."""
        return dict(self.icons)
