#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tooltip Manager Module
Provides enhanced tooltip functionality for clipboard items.
"""

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect, QEvent
from PyQt6.QtGui import QFont, QPalette, QColor, QCursor

class ClipboardTooltip(QWidget):
    """Custom tooltip widget for clipboard items"""
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        
        # Set up appearance
        self.setWindowOpacity(0.95)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Create content label
        self.content_label = QLabel()
        self.content_label.setTextFormat(Qt.TextFormat.PlainText)
        self.content_label.setWordWrap(True)
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.content_label.setMaximumWidth(500)  # Limit width
        
        # Set font
        font = QFont()
        font.setPointSize(10)
        self.content_label.setFont(font)
        
        layout.addWidget(self.content_label)
        
        # Apply theme
        self.apply_theme()
        
        # Hide initially
        self.hide()
    
    def apply_theme(self):
        """Apply theme colors to tooltip"""
        # Get application palette
        app = QApplication.instance()
        palette = app.palette()
        
        # Set background color (slightly darker than tooltip color)
        bg_color = palette.color(QPalette.ColorRole.ToolTipBase)
        text_color = palette.color(QPalette.ColorRole.ToolTipText)
        
        # Create stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color.name()};
                color: {text_color.name()};
                border: 1px solid {text_color.name()};
                border-radius: 4px;
            }}
        """)
    
    def set_content(self, text, timestamp=None):
        """Set tooltip content"""
        # Truncate very long text
        max_length = 1000
        if len(text) > max_length:
            display_text = text[:max_length] + "..."
        else:
            display_text = text
            
        # Add timestamp if provided
        if timestamp:
            display_text = f"{display_text}\n\n{timestamp}"
            
        self.content_label.setText(display_text)
        self.adjustSize()  # Resize to fit content
    
    def show_at(self, pos, screen_rect=None):
        """Show tooltip at specified position"""
        self.adjustSize()  # Make sure size is updated
        
        # Get tooltip size
        size = self.sizeHint()
        
        # Adjust position to ensure tooltip is fully visible on screen
        if screen_rect:
            # Ensure tooltip doesn't go off right edge
            if pos.x() + size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - size.width())
                
            # Ensure tooltip doesn't go off bottom edge
            if pos.y() + size.height() > screen_rect.bottom():
                pos.setY(pos.y() - size.height() - 20)  # Show above cursor
                
            # Ensure tooltip doesn't go off left/top edges
            pos.setX(max(screen_rect.left(), pos.x()))
            pos.setY(max(screen_rect.top(), pos.y()))
        
        self.move(pos)
        self.show()


class TooltipManager:
    """Manager for custom tooltips on clipboard items"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.tooltip = ClipboardTooltip()
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.show_tooltip)
        
        self.current_item = None
        self.hover_delay = 500  # milliseconds
        
    def handle_hover(self, list_widget, item):
        """Handle mouse hover over list item"""
        # First hide any existing tooltip immediately
        self.tooltip.hide()
        
        # Cancel any pending timer
        self.hover_timer.stop()
        
        # Clear previous content to prevent flicker of old content
        self.tooltip.content_label.setText("")
        
        # Update current item
        self.current_item = item
        
        if item:
            # Start timer to show tooltip for new item
            self.hover_timer.start(self.hover_delay)
        else:
            # No item, make sure tooltip is hidden
            self.current_item = None
    
    def show_tooltip(self):
        """Show tooltip for current item"""
        if not self.current_item:
            return
            
        # Get item data
        item_id = self.current_item.data(Qt.ItemDataRole.UserRole)
        
        # Get clipboard item from storage
        if hasattr(self.parent, 'storage'):
            items = self.parent.storage.get_items()
            selected_item = None
            
            for item in items:
                if item.id == item_id:
                    selected_item = item
                    break
                    
            if selected_item and selected_item.content_type == "text":
                # Set tooltip content
                self.tooltip.set_content(
                    selected_item.content,
                    f"Copied: {selected_item.get_formatted_time()}"
                )
                
                # Get cursor position
                cursor_pos = QCursor.pos()
                
                # Get screen geometry
                screen = QApplication.screenAt(cursor_pos)
                if screen:
                    screen_rect = screen.geometry()
                else:
                    screen_rect = QApplication.primaryScreen().geometry()
                
                # Show tooltip slightly below and to the right of cursor
                tooltip_pos = QPoint(cursor_pos.x() + 10, cursor_pos.y() + 20)
                self.tooltip.show_at(tooltip_pos, screen_rect)
    
    def hide_tooltip(self):
        """Hide the tooltip"""
        self.hover_timer.stop()
        self.tooltip.hide()
        self.current_item = None 