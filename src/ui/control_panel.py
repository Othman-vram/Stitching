"""
Control panel for fragment manipulation
"""

from typing import Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QPushButton, QLabel, QSpinBox, QDoubleSpinBox,
                            QSlider, QCheckBox, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon

from ..core.fragment import Fragment

class ControlPanel(QWidget):
    """Control panel for fragment transformation and properties"""
    
    transform_requested = pyqtSignal(str, str, object)  # fragment_id, transform_type, value
    reset_transform_requested = pyqtSignal(str)  # fragment_id
    
    def __init__(self):
        super().__init__()
        self.current_fragment: Optional[Fragment] = None
        self.setup_ui()
        self.update_controls()
        
    def setup_ui(self):
        """Setup the control panel UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Fragment info group
        self.info_group = QGroupBox("Fragment Information")
        self.setup_info_group()
        layout.addWidget(self.info_group)
        
        # Transform group
        self.transform_group = QGroupBox("Transformations")
        self.setup_transform_group()
        layout.addWidget(self.transform_group)
        
        # Position group
        self.position_group = QGroupBox("Position")
        self.setup_position_group()
        layout.addWidget(self.position_group)
        
        # Display group
        self.display_group = QGroupBox("Display")
        self.setup_display_group()
        layout.addWidget(self.display_group)
        
        # Add stretch to push everything to top
        layout.addStretch()
        
    def setup_info_group(self):
        """Setup fragment information display"""
        layout = QVBoxLayout(self.info_group)
        
        self.name_label = QLabel("No fragment selected")
        self.name_label.setStyleSheet("font-weight: bold; color: #4a90e2;")
        layout.addWidget(self.name_label)
        
        self.size_label = QLabel("Size: -")
        layout.addWidget(self.size_label)
        
        self.file_label = QLabel("File: -")
        self.file_label.setWordWrap(True)
        layout.addWidget(self.file_label)
        
    def setup_transform_group(self):
        """Setup transformation controls"""
        layout = QGridLayout(self.transform_group)
        
        # Rotation controls
        layout.addWidget(QLabel("Rotation:"), 0, 0)
        
        rotation_layout = QHBoxLayout()
        self.rotate_ccw_btn = QPushButton("↺ 90°")
        self.rotate_ccw_btn.setToolTip("Rotate counter-clockwise")
        self.rotate_ccw_btn.clicked.connect(lambda: self.request_transform('rotate_ccw'))
        rotation_layout.addWidget(self.rotate_ccw_btn)
        
        self.rotate_cw_btn = QPushButton("↻ 90°")
        self.rotate_cw_btn.setToolTip("Rotate clockwise")
        self.rotate_cw_btn.clicked.connect(lambda: self.request_transform('rotate_cw'))
        rotation_layout.addWidget(self.rotate_cw_btn)
        
        layout.addLayout(rotation_layout, 0, 1)
        
        # Free rotation control
        layout.addWidget(QLabel("Angle:"), 1, 0)
        
        angle_layout = QHBoxLayout()
        self.angle_spinbox = QDoubleSpinBox()
        self.angle_spinbox.setRange(-360.0, 360.0)
        self.angle_spinbox.setDecimals(1)
        self.angle_spinbox.setSuffix("°")
        self.angle_spinbox.valueChanged.connect(self.on_angle_changed)
        angle_layout.addWidget(self.angle_spinbox)
        
        # Quick angle buttons
        angle_45_btn = QPushButton("45°")
        angle_45_btn.setToolTip("Rotate 45 degrees")
        angle_45_btn.clicked.connect(lambda: self.request_transform('rotate_angle', 45))
        angle_layout.addWidget(angle_45_btn)
        
        angle_neg45_btn = QPushButton("-45°")
        angle_neg45_btn.setToolTip("Rotate -45 degrees")
        angle_neg45_btn.clicked.connect(lambda: self.request_transform('rotate_angle', -45))
        angle_layout.addWidget(angle_neg45_btn)
        
        layout.addLayout(angle_layout, 1, 1)
        
        # Flip controls
        layout.addWidget(QLabel("Flip:"), 2, 0)
        
        flip_layout = QHBoxLayout()
        self.flip_h_btn = QPushButton("↔ Horizontal")
        self.flip_h_btn.setToolTip("Flip horizontally")
        self.flip_h_btn.clicked.connect(lambda: self.request_transform('flip_horizontal'))
        flip_layout.addWidget(self.flip_h_btn)
        
        self.flip_v_btn = QPushButton("↕ Vertical")
        self.flip_v_btn.setToolTip("Flip vertically")
        self.flip_v_btn.clicked.connect(lambda: self.request_transform('flip_vertical'))
        flip_layout.addWidget(self.flip_v_btn)
        
        layout.addLayout(flip_layout, 2, 1)
        
        # Reset button
        self.reset_btn = QPushButton("Reset All Transforms")
        self.reset_btn.setStyleSheet("QPushButton { background-color: #d32f2f; }")
        self.reset_btn.clicked.connect(self.request_reset)
        layout.addWidget(self.reset_btn, 3, 0, 1, 2)
        
    def setup_position_group(self):
        """Setup position controls"""
        layout = QGridLayout(self.position_group)
        
        # X position
        layout.addWidget(QLabel("X:"), 0, 0)
        self.x_spinbox = QDoubleSpinBox()
        self.x_spinbox.setRange(-999999, 999999)
        self.x_spinbox.setDecimals(1)
        self.x_spinbox.valueChanged.connect(self.on_position_changed)
        layout.addWidget(self.x_spinbox, 0, 1)
        
        # Y position
        layout.addWidget(QLabel("Y:"), 1, 0)
        self.y_spinbox = QDoubleSpinBox()
        self.y_spinbox.setRange(-999999, 999999)
        self.y_spinbox.setDecimals(1)
        self.y_spinbox.valueChanged.connect(self.on_position_changed)
        layout.addWidget(self.y_spinbox, 1, 1)
        
        # Translation buttons
        translation_layout = QGridLayout()
        
        # Up
        up_btn = QPushButton("↑")
        up_btn.clicked.connect(lambda: self.request_transform('translate', (0, -10)))
        translation_layout.addWidget(up_btn, 0, 1)
        
        # Left, Center, Right
        left_btn = QPushButton("←")
        left_btn.clicked.connect(lambda: self.request_transform('translate', (-10, 0)))
        translation_layout.addWidget(left_btn, 1, 0)
        
        center_btn = QPushButton("⌂")
        center_btn.setToolTip("Center fragment")
        center_btn.clicked.connect(lambda: self.request_transform('translate', (0, 0)))
        translation_layout.addWidget(center_btn, 1, 1)
        
        right_btn = QPushButton("→")
        right_btn.clicked.connect(lambda: self.request_transform('translate', (10, 0)))
        translation_layout.addWidget(right_btn, 1, 2)
        
        # Down
        down_btn = QPushButton("↓")
        down_btn.clicked.connect(lambda: self.request_transform('translate', (0, 10)))
        translation_layout.addWidget(down_btn, 2, 1)
        
        layout.addLayout(translation_layout, 2, 0, 1, 2)
        
    def setup_display_group(self):
        """Setup display controls"""
        layout = QVBoxLayout(self.display_group)
        
        # Visibility checkbox
        self.visible_checkbox = QCheckBox("Visible")
        self.visible_checkbox.stateChanged.connect(self.on_visibility_changed)
        layout.addWidget(self.visible_checkbox)
        
        # Opacity slider
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(QLabel("Opacity:"))
        
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.on_opacity_changed)
        opacity_layout.addWidget(self.opacity_slider)
        
        self.opacity_label = QLabel("100%")
        self.opacity_label.setMinimumWidth(40)
        opacity_layout.addWidget(self.opacity_label)
        
        layout.addLayout(opacity_layout)
        
    def set_selected_fragment(self, fragment: Optional[Fragment]):
        """Set the currently selected fragment"""
        self.current_fragment = fragment
        self.update_controls()
        
    def update_controls(self):
        """Update control states based on current fragment"""
        has_fragment = self.current_fragment is not None
        
        # Enable/disable controls
        self.transform_group.setEnabled(has_fragment)
        self.position_group.setEnabled(has_fragment)
        self.display_group.setEnabled(has_fragment)
        
        if not has_fragment:
            self.name_label.setText("No fragment selected")
            self.size_label.setText("Size: -")
            self.file_label.setText("File: -")
            return
            
        fragment = self.current_fragment
        
        # Update info
        self.name_label.setText(fragment.name or f"Fragment {fragment.id[:8]}")
        self.size_label.setText(f"Size: {fragment.original_size[0]} × {fragment.original_size[1]}")
        self.file_label.setText(f"File: {fragment.file_path}")
        
        # Update position controls (block signals to prevent recursion)
        self.x_spinbox.blockSignals(True)
        self.y_spinbox.blockSignals(True)
        self.x_spinbox.setValue(fragment.x)
        self.y_spinbox.setValue(fragment.y)
        self.x_spinbox.blockSignals(False)
        self.y_spinbox.blockSignals(False)
        
        # Update angle control
        self.angle_spinbox.blockSignals(True)
        self.angle_spinbox.setValue(fragment.rotation)
        self.angle_spinbox.blockSignals(False)
        
        # Update display controls
        self.visible_checkbox.blockSignals(True)
        self.visible_checkbox.setChecked(fragment.visible)
        self.visible_checkbox.blockSignals(False)
        
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(int(fragment.opacity * 100))
        self.opacity_label.setText(f"{int(fragment.opacity * 100)}%")
        self.opacity_slider.blockSignals(False)
        
        # Update transform button states
        self.update_transform_button_states()
        
    def update_transform_button_states(self):
        """Update the visual state of transform buttons"""
        if not self.current_fragment:
            return
            
        fragment = self.current_fragment
        
        # Update flip button styles based on current state
        if fragment.flip_horizontal:
            self.flip_h_btn.setStyleSheet("QPushButton { background-color: #4a90e2; }")
        else:
            self.flip_h_btn.setStyleSheet("")
            
        if fragment.flip_vertical:
            self.flip_v_btn.setStyleSheet("QPushButton { background-color: #4a90e2; }")
        else:
            self.flip_v_btn.setStyleSheet("")
            
    def request_transform(self, transform_type: str, value=None):
        """Request a transformation for the current fragment"""
        if self.current_fragment:
            self.transform_requested.emit(self.current_fragment.id, transform_type, value)
            
    def request_reset(self):
        """Request reset of current fragment transforms"""
        if self.current_fragment:
            self.reset_transform_requested.emit(self.current_fragment.id)
            
    def on_position_changed(self):
        """Handle position spinbox changes"""
        if self.current_fragment:
            new_x = self.x_spinbox.value()
            new_y = self.y_spinbox.value()
            self.request_transform('translate', (new_x - self.current_fragment.x, 
                                               new_y - self.current_fragment.y))
            
    def on_visibility_changed(self, state):
        """Handle visibility checkbox changes"""
        if self.current_fragment:
            visible = state == Qt.CheckState.Checked.value
            self.current_fragment.visible = visible
            
    def on_opacity_changed(self, value):
        """Handle opacity slider changes"""
        if self.current_fragment:
            opacity = value / 100.0
            self.current_fragment.opacity = opacity
            self.opacity_label.setText(f"{value}%")
            
    def on_angle_changed(self):
        """Handle angle spinbox changes"""
        if self.current_fragment:
            new_angle = self.angle_spinbox.value()
            self.request_transform('set_rotation', new_angle)