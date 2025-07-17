"""
Main toolbar widget
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                            QFrame, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

class ToolbarWidget(QWidget):
    """Main application toolbar"""
    
    load_images_requested = pyqtSignal()
    export_requested = pyqtSignal()
    stitch_requested = pyqtSignal()
    reset_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the toolbar UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Load button
        self.load_btn = QPushButton("📁 Load Images")
        self.load_btn.setToolTip("Load tissue fragment images (Ctrl+O)")
        self.load_btn.clicked.connect(self.load_images_requested)
        layout.addWidget(self.load_btn)
        
        # Separator
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.VLine) # For a vertical line
        # Or use: separator1.setFrameShape(QFrame.Shape.HLine) for a horizontal line
        layout.addWidget(separator1)
        
        # Export button
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.setToolTip("Export composite image and metadata")
        self.export_btn.clicked.connect(self.export_requested)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        
        # Separator
        separator2 = QFrame()  # Create a QFrame instead of QSeparator
        separator2.setFrameShape(QFrame.Shape.VLine) # Set its shape to be a Vertical Line
        separator2.setFrameShadow(QFrame.Shadow.Sunken) # Optional: Adds a visual shadow
        layout.addWidget(separator2)
        
        # Stitch button
        self.stitch_btn = QPushButton("🔗 Rigid Stitch")
        self.stitch_btn.setToolTip("Perform rigid stitching refinement (Ctrl+S)")
        self.stitch_btn.clicked.connect(self.stitch_requested)
        self.stitch_btn.setEnabled(False)
        layout.addWidget(self.stitch_btn)
        
        # Reset button
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.setToolTip("Reset all transformations (Ctrl+R)")
        self.reset_btn.clicked.connect(self.reset_requested)
        self.reset_btn.setEnabled(False)
        layout.addWidget(self.reset_btn)
        
        # Spacer
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)
        
        # Status info
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #4a90e2; font-weight: bold;")
        layout.addWidget(self.status_label)
        
    def set_fragment_count(self, count: int):
        """Update the fragment count display"""
        if count == 0:
            self.status_label.setText("Ready")
            self.export_btn.setEnabled(False)
            self.stitch_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
        else:
            self.status_label.setText(f"{count} fragment{'s' if count != 1 else ''} loaded")
            self.export_btn.setEnabled(True)
            self.stitch_btn.setEnabled(count >= 2)
            self.reset_btn.setEnabled(True)
            
    def set_status(self, status: str):
        """Set the status message"""
        self.status_label.setText(status)