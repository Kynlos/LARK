"""Minimap widget showing code overview."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QScrollBar
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QTextLayout, QTextCharFormat,
    QSyntaxHighlighter, QPen, QFontMetrics
)

class Minimap(QWidget):
    """Widget showing a zoomed out view of the code."""
    
    scrolled = pyqtSignal(int)  # Signal emitted when minimap is scrolled
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor = None
        self.scroll_position = 0
        self.viewport_height = 0
        self.total_height = 0
        self.scale_factor = 0.15  # Scale factor for minimap
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI."""
        self.setMinimumWidth(100)
        self.setMaximumWidth(150)
        self.setSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Expanding
        )
        
    def set_editor(self, editor):
        """Set the editor to show in minimap."""
        self.editor = editor
        if editor:
            editor.textChanged.connect(self.update)
            editor.verticalScrollBar().valueChanged.connect(self.update_scroll_position)
            
    def update_scroll_position(self, value):
        """Update scroll position from editor."""
        if self.editor:
            self.scroll_position = value
            self.viewport_height = self.editor.viewport().height()
            self.total_height = self.editor.verticalScrollBar().maximum()
            self.update()
            
    def paintEvent(self, event):
        """Paint the minimap."""
        if not self.editor:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        background_rect = QRect(0, 0, self.width(), self.height())
        painter.fillRect(background_rect, QColor(39, 40, 34))  # Dark background
        
        # Calculate dimensions
        content_width = self.width() - 2  # Leave space for border
        content_height = self.height() - 2
        
        # Draw text content
        painter.setPen(QColor(248, 248, 242))  # Light text color
        font = self.editor.font()
        font.setPointSize(1)  # Very small font for minimap
        painter.setFont(font)
        
        metrics = QFontMetrics(font)
        line_height = metrics.height()
        
        # Calculate visible area
        if self.total_height > 0:
            visible_ratio = self.viewport_height / (self.total_height + self.viewport_height)
            scroll_ratio = self.scroll_position / (self.total_height + self.viewport_height)
            visible_height = int(content_height * visible_ratio)
            visible_y = int(content_height * scroll_ratio)
            
            # Draw visible area indicator
            visible_rect = QRect(1, visible_y + 1, content_width, visible_height)
            painter.fillRect(visible_rect, QColor(61, 61, 52, 100))  # Semi-transparent highlight
        
        # Draw text blocks
        y = 1
        line = 0
        while line < self.editor.lines():
            text = self.editor.text(line)
            if text.strip():  # Only draw non-empty lines
                text_rect = QRect(1, y, content_width, line_height)
                painter.drawText(
                    text_rect,
                    Qt.AlignmentFlag.AlignLeft,
                    text
                )
            y += line_height
            if y > self.height():
                break
            line += 1
            
        # Draw border
        border_rect = QRect(0, 0, self.width() - 1, self.height() - 1)
        painter.setPen(QPen(QColor(64, 64, 64)))
        painter.drawRect(border_rect)
        
    def mousePressEvent(self, event):
        """Handle mouse press for scrolling."""
        self.scroll_to_position(event.pos().y())
        
    def mouseMoveEvent(self, event):
        """Handle mouse drag for scrolling."""
        self.scroll_to_position(event.pos().y())
        
    def scroll_to_position(self, y):
        """Scroll editor to position based on minimap click."""
        if not self.editor or self.total_height <= 0:
            return
            
        # Calculate scroll position
        ratio = (y - 1) / (self.height() - 2)
        scroll_pos = int(ratio * self.total_height)
        
        # Update editor scroll position
        self.editor.verticalScrollBar().setValue(scroll_pos)
        
    def sizeHint(self):
        """Suggest size for the widget."""
        return QSize(120, super().sizeHint().height())
