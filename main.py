#!/usr/bin/env python3
"""
Tissue Fragment Arrangement and Rigid Stitching UI
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    #QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    #QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Tissue Fragment Stitching Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Scientific Imaging Lab")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Apply dark theme
    from src.ui.theme import apply_dark_theme
    apply_dark_theme(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()