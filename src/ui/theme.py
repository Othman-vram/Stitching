"""
Application theme and styling
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

def apply_dark_theme(app: QApplication):
    """Apply dark theme to the application"""
    
    # Set dark palette
    palette = QPalette()
    
    # Window colors
    palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    
    # Base colors (input fields, etc.)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(55, 55, 55))
    
    # Text colors
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
    
    # Button colors
    palette.setColor(QPalette.ColorRole.Button, QColor(55, 55, 55))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    
    # Highlight colors
    palette.setColor(QPalette.ColorRole.Highlight, QColor(70, 130, 200))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
    
    app.setPalette(palette)
    
    # Additional stylesheet for fine-tuning
    stylesheet = """
    QMainWindow {
        background-color: #2d2d2d;
        color: #dcdcdc;
    }
    
    QMenuBar {
        background-color: #3d3d3d;
        color: #dcdcdc;
        border-bottom: 1px solid #555;
    }
    
    QMenuBar::item {
        background-color: transparent;
        padding: 4px 8px;
    }
    
    QMenuBar::item:selected {
        background-color: #4682b4;
    }
    
    QMenu {
        background-color: #3d3d3d;
        color: #dcdcdc;
        border: 1px solid #555;
    }
    
    QMenu::item:selected {
        background-color: #4682b4;
    }
    
    QStatusBar {
        background-color: #3d3d3d;
        color: #dcdcdc;
        border-top: 1px solid #555;
    }
    
    QToolBar {
        background-color: #3d3d3d;
        border: 1px solid #555;
        spacing: 2px;
    }
    
    QPushButton {
        background-color: #4d4d4d;
        border: 1px solid #666;
        padding: 6px 12px;
        border-radius: 3px;
        color: #dcdcdc;
    }
    
    QPushButton:hover {
        background-color: #5d5d5d;
        border-color: #777;
    }
    
    QPushButton:pressed {
        background-color: #3d3d3d;
    }
    
    QPushButton:disabled {
        background-color: #3d3d3d;
        color: #888;
        border-color: #555;
    }
    
    QListWidget {
        background-color: #2d2d2d;
        border: 1px solid #555;
        selection-background-color: #4682b4;
    }
    
    QListWidget::item {
        padding: 4px;
        border-bottom: 1px solid #444;
    }
    
    QListWidget::item:selected {
        background-color: #4682b4;
    }
    
    QGroupBox {
        font-weight: bold;
        border: 1px solid #555;
        border-radius: 3px;
        margin-top: 6px;
        padding-top: 6px;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 5px 0 5px;
    }
    
    QSpinBox, QDoubleSpinBox {
        background-color: #2d2d2d;
        border: 1px solid #555;
        padding: 2px;
        border-radius: 3px;
    }
    
    QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #4682b4;
    }
    
    QSlider::groove:horizontal {
        border: 1px solid #555;
        height: 6px;
        background: #2d2d2d;
        border-radius: 3px;
    }
    
    QSlider::handle:horizontal {
        background: #4682b4;
        border: 1px solid #555;
        width: 14px;
        margin: -4px 0;
        border-radius: 7px;
    }
    
    QSlider::handle:horizontal:hover {
        background: #5a9bd4;
    }
    
    QProgressBar {
        border: 1px solid #555;
        border-radius: 3px;
        text-align: center;
        background-color: #2d2d2d;
    }
    
    QProgressBar::chunk {
        background-color: #4682b4;
        border-radius: 2px;
    }
    
    QSplitter::handle {
        background-color: #555;
    }
    
    QSplitter::handle:horizontal {
        width: 2px;
    }
    
    QSplitter::handle:vertical {
        height: 2px;
    }
    """
    
    app.setStyleSheet(stylesheet)