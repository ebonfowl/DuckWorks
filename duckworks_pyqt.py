"""
DuckWorks PyQt Framework - Modern GUI Components
Part of the DuckWorks Educational Automation Suite

This module provides PyQt6-based GUI components with professional styling
and consistent DuckWorks branding across all educational automation tools.

Author: DuckWorks Development Team
License: Educational Use
Version: 2.0.0 (PyQt6 Edition)
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from duckworks_framework import DuckWorksInfo

class DuckWorksStyle:
    """Professional styling system for DuckWorks PyQt applications"""
    
    # Modern color palette
    COLORS = {
        # Primary colors (duck-themed)
        'primary': '#2E86AB',      # Duck blue
        'primary_light': '#4A9BC7', 
        'primary_dark': '#1F5F7A',
        
        # Secondary colors
        'secondary': '#A23B72',    # Duck purple
        'accent': '#F18F01',       # Duck orange
        'success': '#28A745',      # Success green
        'warning': '#FFC107',      # Warning yellow
        'error': '#DC3545',        # Error red
        
        # Neutral colors
        'background': '#FFFFFF',   # Light background
        'surface': '#F8F9FA',      # Card surfaces
        'border': '#DEE2E6',       # Borders
        'text': '#212529',         # Primary text
        'text_secondary': '#6C757D', # Secondary text
        'text_muted': '#ADB5BD',   # Muted text
        
        # Dark theme
        'dark_background': '#1E1E1E',
        'dark_surface': '#2D2D2D',
        'dark_border': '#404040',
        'dark_text': '#FFFFFF',
        'dark_text_secondary': '#CCCCCC'
    }
    
    @classmethod
    def get_stylesheet(cls, theme='light'):
        """Get complete stylesheet for DuckWorks applications"""
        
        if theme == 'dark':
            return cls._get_dark_stylesheet()
        else:
            return cls._get_light_stylesheet()
    
    @classmethod
    def _get_light_stylesheet(cls):
        """Light theme stylesheet"""
        return f"""
        /* Main Application Window */
        QMainWindow {{
            background-color: {cls.COLORS['background']};
            color: {cls.COLORS['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 9pt;
        }}
        
        /* Cards and Panels */
        QFrame.card {{
            background-color: {cls.COLORS['surface']};
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            padding: 16px;
            margin: 8px;
        }}
        
        /* Primary Buttons */
        QPushButton.primary {{
            background-color: {cls.COLORS['primary']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 32px;
        }}
        
        QPushButton.primary:hover {{
            background-color: {cls.COLORS['primary_light']};
        }}
        
        QPushButton.primary:pressed {{
            background-color: {cls.COLORS['primary_dark']};
        }}
        
        QPushButton.primary:disabled {{
            background-color: {cls.COLORS['text_muted']};
        }}
        
        /* Secondary Buttons */
        QPushButton.secondary {{
            background-color: transparent;
            color: {cls.COLORS['primary']};
            border: 2px solid {cls.COLORS['primary']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            min-height: 32px;
        }}
        
        QPushButton.secondary:hover {{
            background-color: {cls.COLORS['primary']};
            color: white;
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QComboBox {{
            background-color: white;
            border: 2px solid {cls.COLORS['border']};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 9pt;
            min-height: 20px;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {cls.COLORS['primary']};
            outline: none;
        }}
        
        /* Progress Bars */
        QProgressBar {{
            background-color: {cls.COLORS['border']};
            border: none;
            border-radius: 8px;
            height: 16px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {cls.COLORS['primary']};
            border-radius: 8px;
        }}
        
        /* Labels */
        QLabel.title {{
            font-size: 18pt;
            font-weight: 600;
            color: {cls.COLORS['text']};
            margin-bottom: 8px;
        }}
        
        QLabel.heading {{
            font-size: 12pt;
            font-weight: 500;
            color: {cls.COLORS['text']};
            margin-bottom: 4px;
        }}
        
        QLabel.muted {{
            color: {cls.COLORS['text_muted']};
            font-size: 8pt;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {cls.COLORS['border']};
            border-radius: 8px;
            background-color: {cls.COLORS['surface']};
        }}
        
        QTabBar::tab {{
            background-color: {cls.COLORS['background']};
            border: 1px solid {cls.COLORS['border']};
            padding: 8px 16px;
            margin-right: 2px;
            border-radius: 6px 6px 0 0;
        }}
        
        QTabBar::tab:selected {{
            background-color: {cls.COLORS['primary']};
            color: white;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: 500;
            border: 2px solid {cls.COLORS['border']};
            border-radius: 8px;
            margin-top: 8px;
            padding-top: 16px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 16px;
            padding: 0 8px 0 8px;
            background-color: {cls.COLORS['background']};
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {cls.COLORS['surface']};
            border-top: 1px solid {cls.COLORS['border']};
            padding: 4px;
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        
        QScrollBar:vertical {{
            background-color: {cls.COLORS['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {cls.COLORS['text_muted']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {cls.COLORS['primary']};
        }}
        """
    
    @classmethod
    def _get_dark_stylesheet(cls):
        """Dark theme stylesheet - placeholder for future implementation"""
        # For now, return light theme
        # TODO: Implement full dark theme
        return cls._get_light_stylesheet()

class DuckWorksIcon:
    """Icon management for DuckWorks applications"""
    
    @staticmethod
    def get_duck_icon():
        """Get the main duck icon"""
        icon_path = Path("assets/icons8-flying-duck-48.png")
        if icon_path.exists():
            return QIcon(str(icon_path))
        else:
            # Create a simple duck emoji icon as fallback
            pixmap = QPixmap(48, 48)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setFont(QFont("Arial", 32))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🦆")
            painter.end()
            return QIcon(pixmap)
    
    @staticmethod
    def get_themed_icon(name, color=None):
        """Get themed icons for common actions"""
        if color is None:
            color = DuckWorksStyle.COLORS['primary']
            
        # Create simple colored icons for common actions
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor(color))
        pen.setWidth(2)
        painter.setPen(pen)
        
        if name == "folder":
            painter.drawRect(4, 8, 16, 12)
            painter.drawRect(4, 6, 6, 2)
        elif name == "file":
            painter.drawRect(6, 4, 12, 16)
            painter.drawLine(6, 8, 15, 8)
            painter.drawLine(6, 12, 15, 12)
        elif name == "settings":
            center = QPoint(12, 12)
            painter.drawEllipse(center, 6, 6)
            painter.drawEllipse(center, 3, 3)
        elif name == "play":
            points = [QPoint(8, 6), QPoint(8, 18), QPoint(18, 12)]
            painter.drawPolygon(points)
        elif name == "check":
            painter.drawLine(6, 12, 10, 16)
            painter.drawLine(10, 16, 18, 8)
        
        painter.end()
        return QIcon(pixmap)

class DuckWorksCard(QFrame):
    """Modern card component for DuckWorks applications"""
    
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "card")
        self.init_ui(title)
    
    def init_ui(self, title):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        if title:
            title_label = QLabel(title)
            title_label.setProperty("class", "heading")
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
    
    def add_widget(self, widget):
        """Add widget to card content"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """Add layout to card content"""
        self.content_layout.addLayout(layout)

class DuckWorksButton(QPushButton):
    """Enhanced button with DuckWorks styling"""
    
    def __init__(self, text, style="primary", icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setProperty("class", style)
        
        if icon_name:
            self.setIcon(DuckWorksIcon.get_themed_icon(icon_name))
        
        # Add subtle animations
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)
        
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(150)
    
    def enterEvent(self, event):
        """Subtle hover animation"""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.9)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Restore on leave"""
        self.animation.setStartValue(0.9)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().leaveEvent(event)

class DuckWorksProgressBar(QProgressBar):
    """Enhanced progress bar with smooth animations"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setFormat("%p% - %v/%m")
        
        # Animation for smooth progress updates
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def animate_to_value(self, value):
        """Smoothly animate to new value"""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()
    
    def set_status_text(self, text):
        """Update progress text"""
        self.setFormat(f"{text} - %p%")

class DuckWorksMainWindow(QMainWindow):
    """Base main window class for DuckWorks applications"""
    
    def __init__(self, tool_name, parent=None):
        super().__init__(parent)
        self.tool_name = tool_name
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main window UI"""
        # Set window properties
        tool_info = DuckWorksInfo.TOOLS.get(self.tool_name, {})
        title = f"{self.tool_name} | DuckWorks Educational Suite"
        self.setWindowTitle(title)
        self.setMinimumSize(1000, 700)
        
        # Set duck icon
        self.setWindowIcon(DuckWorksIcon.get_duck_icon())
        
        # Apply DuckWorks stylesheet
        self.setStyleSheet(DuckWorksStyle.get_stylesheet())
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"{self.tool_name} Ready - DuckWorks Educational Automation")
    
    def show_duck_message(self, title, message, icon_type="information"):
        """Show a DuckWorks-branded message box"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{title}")
        msg_box.setText(message)
        msg_box.setWindowIcon(DuckWorksIcon.get_duck_icon())
        
        if icon_type == "information":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif icon_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif icon_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        
        return msg_box.exec()

# Test the framework if run directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create test window
    window = DuckWorksMainWindow("DuckGrade")
    
    # Add some test content
    layout = QVBoxLayout(window.central_widget)
    
    # Title
    title = QLabel("🦆 DuckWorks PyQt6 Framework Demo")
    title.setProperty("class", "title")
    layout.addWidget(title)
    
    # Test card
    card = DuckWorksCard("Test Card")
    card.add_widget(QLabel("This is a modern DuckWorks card component!"))
    
    button_layout = QHBoxLayout()
    primary_btn = DuckWorksButton("Primary Action", "primary", "play")
    secondary_btn = DuckWorksButton("Secondary Action", "secondary", "settings")
    button_layout.addWidget(primary_btn)
    button_layout.addWidget(secondary_btn)
    card.add_layout(button_layout)
    
    layout.addWidget(card)
    
    # Test progress bar
    progress_card = DuckWorksCard("Progress Demo")
    progress = DuckWorksProgressBar()
    progress.setRange(0, 100)
    progress.animate_to_value(75)
    progress.set_status_text("Processing files")
    progress_card.add_widget(progress)
    layout.addWidget(progress_card)
    
    layout.addStretch()
    
    # Show window
    window.show()
    
    # Test message box
    def show_demo_message():
        window.show_duck_message("Demo", "This is a DuckWorks message box!")
    
    primary_btn.clicked.connect(show_demo_message)
    
    sys.exit(app.exec())
