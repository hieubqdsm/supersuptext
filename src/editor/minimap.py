"""
SuperSupText - Minimap Widget
A miniature preview of the code for quick navigation
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QRect, QTimer
from PySide6.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen, QBrush


class MiniMap(QWidget):
    """
    Minimap widget that shows a scaled down preview of the code.
    Click to navigate to that position in the editor.
    """
    
    # Signal emitted when user clicks on minimap
    positionClicked = Signal(int)  # line number
    
    def __init__(self, editor=None, parent=None):
        super().__init__(parent)
        self._editor = editor
        self._lines = []
        self._visible_start = 0
        self._visible_end = 0
        self._total_lines = 0
        self._line_height = 2
        self._char_width = 1
        self._dragging = False
        
        # Appearance
        self._bg_color = QColor("#1e1e1e")
        self._text_color = QColor("#808080")
        self._viewport_color = QColor("#ffffff")
        self._viewport_opacity = 30
        
        self.setFixedWidth(100)
        self.setMinimumHeight(100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Update timer
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._delayed_update)
        self._update_timer.setSingleShot(True)
        
        if editor:
            self.setEditor(editor)
    
    def setEditor(self, editor):
        """Set the editor to track."""
        self._editor = editor
        
        # Connect to editor signals
        if hasattr(editor, 'textChanged'):
            editor.textChanged.connect(self.scheduleUpdate)
        if hasattr(editor, 'cursorPositionChanged'):
            editor.cursorPositionChanged.connect(self.scheduleUpdate)
        
        self.updateContent()
    
    def scheduleUpdate(self, *args):
        """Schedule a delayed update to avoid too frequent repaints."""
        self._update_timer.start(100)
    
    def _delayed_update(self):
        """Perform the actual update."""
        self.updateContent()
    
    def updateContent(self):
        """Update the minimap content from the editor."""
        if not self._editor:
            return
        
        # Get editor content
        try:
            text = self._editor.text() if hasattr(self._editor, 'text') else ""
            self._lines = text.split('\n')
            self._total_lines = len(self._lines)
            
            # Get visible range from editor
            if hasattr(self._editor, 'firstVisibleLine'):
                self._visible_start = self._editor.firstVisibleLine()
                # Estimate visible lines based on editor height
                editor_height = self._editor.height()
                line_height = 16  # Approximate
                visible_count = max(1, editor_height // line_height)
                self._visible_end = min(self._visible_start + visible_count, self._total_lines)
            else:
                self._visible_start = 0
                self._visible_end = min(30, self._total_lines)
        except Exception:
            self._lines = []
            self._total_lines = 0
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the minimap."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        # Background
        painter.fillRect(self.rect(), self._bg_color)
        
        if not self._lines:
            return
        
        # Calculate scaling
        available_height = self.height()
        content_height = self._total_lines * self._line_height
        
        if content_height > available_height:
            scale = available_height / content_height
        else:
            scale = 1.0
        
        scaled_line_height = max(1, int(self._line_height * scale))
        
        # Draw lines
        painter.setPen(self._text_color)
        
        max_chars = (self.width() - 10) // self._char_width
        
        for i, line in enumerate(self._lines):
            if i * scaled_line_height > available_height:
                break
            
            y = int(i * scaled_line_height)
            
            if line.strip():
                # Draw a simplified representation of the line
                indent = len(line) - len(line.lstrip())
                content_length = min(len(line.rstrip()), max_chars)
                
                x = 5 + int(indent * self._char_width * 0.5)
                width = max(2, int((content_length - indent) * self._char_width * 0.5))
                
                painter.drawLine(x, y, x + width, y)
        
        # Draw viewport rectangle
        if self._total_lines > 0:
            viewport_y = int(self._visible_start * scaled_line_height)
            viewport_height = int((self._visible_end - self._visible_start) * scaled_line_height)
            viewport_height = max(10, viewport_height)
            
            viewport_color = QColor(self._viewport_color)
            viewport_color.setAlpha(self._viewport_opacity)
            
            painter.fillRect(0, viewport_y, self.width(), viewport_height, viewport_color)
            
            # Draw border
            border_color = QColor(self._viewport_color)
            border_color.setAlpha(60)
            painter.setPen(QPen(border_color, 1))
            painter.drawRect(0, viewport_y, self.width() - 1, viewport_height)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._navigate_to_position(event.position().y())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move while dragging."""
        if self._dragging:
            self._navigate_to_position(event.position().y())
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        self._dragging = False
    
    def _navigate_to_position(self, y):
        """Navigate to the line at the given y position."""
        if self._total_lines == 0:
            return
        
        available_height = self.height()
        content_height = self._total_lines * self._line_height
        
        if content_height > available_height:
            scale = available_height / content_height
        else:
            scale = 1.0
        
        scaled_line_height = max(1, self._line_height * scale)
        
        line = int(y / scaled_line_height)
        line = max(0, min(line, self._total_lines - 1))
        
        self.positionClicked.emit(line + 1)  # 1-indexed
    
    def setTheme(self, theme_name: str):
        """Set the minimap theme."""
        if theme_name == 'light':
            self._bg_color = QColor("#f3f3f3")
            self._text_color = QColor("#a0a0a0")
            self._viewport_color = QColor("#000000")
        else:
            self._bg_color = QColor("#1e1e1e")
            self._text_color = QColor("#808080")
            self._viewport_color = QColor("#ffffff")
        
        self.update()
    
    def setVisible(self, visible: bool):
        """Override to update on visibility change."""
        super().setVisible(visible)
        if visible:
            self.updateContent()
