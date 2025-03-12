#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Settings Dialog Module
Dialog for configuring application settings.
"""

import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QCheckBox,
    QPushButton, QFileDialog, QComboBox,
    QGroupBox, QTabWidget, QWidget, QApplication
)
from PyQt6.QtCore import Qt

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        """
        Initialize settings dialog
        
        Args:
            config_manager: ConfigManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.config = config_manager
        
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)
        
        # Create UI
        self.setup_ui()
        
        # Load current settings
        self.load_settings()
        
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        
        # Create tabs
        tabs = QTabWidget()
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Hotkey")
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("Press keys (e.g. ctrl+shift+q)")
        self.hotkey_label = QLabel("Current hotkey:")
        hotkey_layout.addRow(self.hotkey_label, self.hotkey_edit)
        
        # 添加說明標籤
        help_label = QLabel("Supported keys: ctrl, shift, alt + letter/number")
        help_label.setStyleSheet("color: gray;")
        hotkey_layout.addRow("", help_label)
        
        general_layout.addWidget(hotkey_group)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.startup_checkbox = QCheckBox("Start on system boot")
        startup_layout.addWidget(self.startup_checkbox)
        
        general_layout.addWidget(startup_group)
        
        # Theme settings
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        theme_layout.addRow("Theme:", self.theme_combo)
        
        general_layout.addWidget(theme_group)
        
        # Add general tab
        tabs.addTab(general_tab, "General")
        
        # Storage tab
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        # Storage path settings
        path_group = QGroupBox("Storage Location")
        path_layout = QHBoxLayout(path_group)
        
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_storage_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_button)
        
        storage_layout.addWidget(path_group)
        
        # History settings
        history_group = QGroupBox("History")
        history_layout = QFormLayout(history_group)
        
        self.max_items_spin = QSpinBox()
        self.max_items_spin.setMinimum(10)
        self.max_items_spin.setMaximum(1000)
        self.max_items_spin.setSingleStep(10)
        
        history_layout.addRow("Maximum items:", self.max_items_spin)
        
        storage_layout.addWidget(history_group)
        
        # Storage info
        info_group = QGroupBox("Storage Information")
        info_layout = QFormLayout(info_group)
        
        self.item_count_label = QLabel()
        self.total_size_label = QLabel()
        self.db_size_label = QLabel()
        
        info_layout.addRow("Items stored:", self.item_count_label)
        info_layout.addRow("Total content size:", self.total_size_label)
        info_layout.addRow("Database size:", self.db_size_label)
        
        storage_layout.addWidget(info_group)
        
        # Add storage tab
        tabs.addTab(storage_tab, "Storage")
        
        layout.addWidget(tabs)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def load_settings(self):
        """Load current settings"""
        # Load general settings
        self.hotkey_edit.setText(self.config.get_hotkey())
        self.startup_checkbox.setChecked(self.config.get_startup())
        
        theme = self.config.get_theme()
        theme_index = 0  # Default to system
        if theme == "light":
            theme_index = 1
        elif theme == "dark":
            theme_index = 2
        self.theme_combo.setCurrentIndex(theme_index)
        
        # Load storage settings
        self.path_edit.setText(self.config.get_storage_path())
        self.max_items_spin.setValue(self.config.get_max_items())
        
        # Load storage info
        self.update_storage_info()
        
    def update_storage_info(self):
        """Update storage information labels"""
        from storage_manager import StorageManager
        
        # Create temporary storage manager to get info
        storage = StorageManager(self.config.get_storage_path())
        info = storage.get_storage_info()
        
        self.item_count_label.setText(str(info["item_count"]))
        
        # Format sizes
        def format_size(size):
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            elif size < 1024 * 1024 * 1024:
                return f"{size / (1024 * 1024):.1f} MB"
            else:
                return f"{size / (1024 * 1024 * 1024):.1f} GB"
                
        self.total_size_label.setText(format_size(info["total_size"]))
        self.db_size_label.setText(format_size(info["db_size"]))
        
    def browse_storage_path(self):
        """Browse for storage path"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Storage Directory",
            self.path_edit.text()
        )
        
        if path:
            self.path_edit.setText(path)
            
    def accept(self):
        """Save settings and close dialog"""
        # 保存熱鍵設置
        new_hotkey = self.hotkey_edit.text()
        if new_hotkey != self.config.get_hotkey():
            self.config.set_hotkey(new_hotkey)
            # 更新全局熱鍵
            app = QApplication.instance()
            if hasattr(app, 'hotkey_manager'):
                app.hotkey_manager.register_hotkey(new_hotkey)
        
        # Save general settings
        self.config.set_startup(self.startup_checkbox.isChecked())
        
        theme_index = self.theme_combo.currentIndex()
        theme = "system"
        if theme_index == 1:
            theme = "light"
        elif theme_index == 2:
            theme = "dark"
        self.config.set_theme(theme)
        
        # Save storage settings
        self.config.set_storage_path(self.path_edit.text())
        self.config.set_max_items(self.max_items_spin.value())
        
        # Close dialog
        super().accept() 
