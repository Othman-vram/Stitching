"""
Fragment list widget for selection and management
"""

from typing import List, Optional
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QListWidgetItem,
                            QHBoxLayout, QPushButton, QLabel, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

from ..core.fragment import Fragment

class FragmentListItem(QWidget):
    """Custom widget for fragment list items"""
    
    visibility_changed = pyqtSignal(str, bool)  # fragment_id, visible
    
    def __init__(self, fragment: Fragment):
        super().__init__()
        self.fragment = fragment
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the list item UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # Visibility checkbox
        self.visibility_checkbox = QCheckBox()
        self.visibility_checkbox.setChecked(self.fragment.visible)
        self.visibility_checkbox.stateChanged.connect(self.on_visibility_changed)
        layout.addWidget(self.visibility_checkbox)
        
        # Fragment thumbnail (placeholder)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(32, 32)
        self.thumbnail_label.setStyleSheet("border: 1px solid #555; background-color: #3d3d3d;")
        self.update_thumbnail()
        layout.addWidget(self.thumbnail_label)
        
        # Fragment info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(0)
        
        self.name_label = QLabel(self.fragment.name or f"Fragment {self.fragment.id[:8]}")
        self.name_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.name_label)
        
        size_text = f"{self.fragment.original_size[0]} × {self.fragment.original_size[1]}"
        self.size_label = QLabel(size_text)
        self.size_label.setStyleSheet("color: #aaa; font-size: 11px;")
        info_layout.addWidget(self.size_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
        
    def update_thumbnail(self):
        """Update the thumbnail display"""
        # Create a simple colored rectangle as thumbnail
        pixmap = QPixmap(30, 30)
        pixmap.fill(QColor(100, 100, 100))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(200, 200, 200))
        painter.drawRect(0, 0, 29, 29)
        painter.end()
        
        self.thumbnail_label.setPixmap(pixmap)
        
    def on_visibility_changed(self, state):
        """Handle visibility checkbox changes"""
        visible = state == Qt.CheckState.Checked
        self.visibility_changed.emit(self.fragment.id, visible)
        
    def set_selected(self, selected: bool):
        """Set the selection state of this item"""
        if selected:
            self.setStyleSheet("QWidget { background-color: #4a90e2; }")
        else:
            self.setStyleSheet("")
            
    def update_fragment_info(self, fragment: Fragment):
        """Update the fragment information"""
        self.fragment = fragment
        self.name_label.setText(fragment.name or f"Fragment {fragment.id[:8]}")
        
        size_text = f"{fragment.original_size[0]} × {fragment.original_size[1]}"
        self.size_label.setText(size_text)
        
        self.visibility_checkbox.blockSignals(True)
        self.visibility_checkbox.setChecked(fragment.visible)
        self.visibility_checkbox.blockSignals(False)

class FragmentListWidget(QWidget):
    """Widget for displaying and managing the list of fragments"""
    
    fragment_selected = pyqtSignal(str)  # fragment_id
    fragment_visibility_changed = pyqtSignal(str, bool)  # fragment_id, visible
    
    def __init__(self):
        super().__init__()
        self.fragments: List[Fragment] = []
        self.selected_fragment_id: Optional[str] = None
        self.fragment_items: dict = {}  # fragment_id -> (QListWidgetItem, FragmentListItem)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the fragment list UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Fragments")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #4a90e2;")
        header_layout.addWidget(header_label)
        
        self.count_label = QLabel("(0)")
        self.count_label.setStyleSheet("color: #aaa;")
        header_layout.addWidget(self.count_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Fragment list
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.show_all_btn = QPushButton("Show All")
        self.show_all_btn.clicked.connect(self.show_all_fragments)
        controls_layout.addWidget(self.show_all_btn)
        
        self.hide_all_btn = QPushButton("Hide All")
        self.hide_all_btn.clicked.connect(self.hide_all_fragments)
        controls_layout.addWidget(self.hide_all_btn)
        
        layout.addLayout(controls_layout)
        
    def update_fragments(self, fragments: List[Fragment]):
        """Update the fragment list"""
        self.fragments = fragments
        self.rebuild_list()
        self.count_label.setText(f"({len(fragments)})")
        
    def rebuild_list(self):
        """Rebuild the entire fragment list"""
        # Clear existing items
        self.list_widget.clear()
        self.fragment_items.clear()
        
        # Add fragments
        for fragment in self.fragments:
            self.add_fragment_item(fragment)
            
        # Restore selection
        if self.selected_fragment_id:
            self.set_selected_fragment(self.selected_fragment_id)
            
    def add_fragment_item(self, fragment: Fragment):
        """Add a single fragment item to the list"""
        # Create list item
        list_item = QListWidgetItem()
        list_item.setData(Qt.ItemDataRole.UserRole, fragment.id)
        
        # Create custom widget
        fragment_widget = FragmentListItem(fragment)
        fragment_widget.visibility_changed.connect(self.fragment_visibility_changed)
        
        # Add to list
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, fragment_widget)
        
        # Store reference
        self.fragment_items[fragment.id] = (list_item, fragment_widget)
        
        # Set item size
        list_item.setSizeHint(fragment_widget.sizeHint())
        
    def set_selected_fragment(self, fragment_id: Optional[str]):
        """Set the selected fragment"""
        # Clear previous selection
        if self.selected_fragment_id and self.selected_fragment_id in self.fragment_items:
            _, widget = self.fragment_items[self.selected_fragment_id]
            widget.set_selected(False)
            
        self.selected_fragment_id = fragment_id
        
        # Set new selection
        if fragment_id and fragment_id in self.fragment_items:
            list_item, widget = self.fragment_items[fragment_id]
            widget.set_selected(True)
            self.list_widget.setCurrentItem(list_item)
            
    def on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events"""
        fragment_id = item.data(Qt.ItemDataRole.UserRole)
        if fragment_id:
            self.fragment_selected.emit(fragment_id)
            
    def show_all_fragments(self):
        """Show all fragments"""
        for fragment in self.fragments:
            self.fragment_visibility_changed.emit(fragment.id, True)
            
    def hide_all_fragments(self):
        """Hide all fragments"""
        for fragment in self.fragments:
            self.fragment_visibility_changed.emit(fragment.id, False)
            
    def update_fragment_info(self, fragment: Fragment):
        """Update information for a specific fragment"""
        if fragment.id in self.fragment_items:
            _, widget = self.fragment_items[fragment.id]
            widget.update_fragment_info(fragment)