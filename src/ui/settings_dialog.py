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
from utils.theme_manager import ThemeManager

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        """
        Initialize settings dialog
        
        Args:
            config_manager: ConfigManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # 直接使用 SettingsConfig
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
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        # 修飾鍵複選框
        modifier_layout = QHBoxLayout()
        self.shift_check = QCheckBox("Shift")
        self.ctrl_check = QCheckBox("Ctrl")
        self.alt_check = QCheckBox("Alt")
        self.win_check = QCheckBox("Win")
        
        modifier_layout.addWidget(self.shift_check)
        modifier_layout.addWidget(self.ctrl_check)
        modifier_layout.addWidget(self.alt_check)
        modifier_layout.addWidget(self.win_check)
        
        # 按鍵輸入框
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_edit = QLineEdit()
        self.key_edit.setMaxLength(1)  # 限制只能輸入一個字符
        key_layout.addWidget(self.key_edit)
        
        hotkey_layout.addLayout(modifier_layout)
        hotkey_layout.addLayout(key_layout)
        
        # 添加說明標籤
        help_label = QLabel("Select modifiers and enter a letter or number")
        help_label.setStyleSheet("color: gray;")
        hotkey_layout.addWidget(help_label)
        
        general_layout.addWidget(hotkey_group)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.startup_checkbox = QCheckBox("Start on system boot")
        startup_layout.addWidget(self.startup_checkbox)
        
        # 添加關閉行為設置
        close_group = QGroupBox("Close Button Behavior")
        close_layout = QVBoxLayout(close_group)
        
        self.minimize_to_tray = QCheckBox("Minimize to tray when clicking close button")
        self.minimize_to_tray.setToolTip("If unchecked, the application will exit when clicking close")
        close_layout.addWidget(self.minimize_to_tray)
        
        general_layout.addWidget(startup_group)
        general_layout.addWidget(close_group)
        general_layout.addStretch()
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("System")
        
        # 添加所有可用主題
        available_themes = ThemeManager.get_available_themes()
        for theme_name in available_themes.keys():
            self.theme_combo.addItem(theme_name.title())
        
        theme_layout.addWidget(self.theme_combo)
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
        # 載入熱鍵設置
        current_hotkey = self.config.get_hotkey()
        modifiers = current_hotkey.lower().split("+")
        
        # 設置修飾鍵狀態
        self.shift_check.setChecked("shift" in modifiers)
        self.ctrl_check.setChecked("ctrl" in modifiers)
        self.alt_check.setChecked("alt" in modifiers)
        self.win_check.setChecked("win" in modifiers)
        
        # 設置主鍵
        key = modifiers[-1] if modifiers else ""
        self.key_edit.setText(key.upper())
        
        # Load general settings
        self.startup_checkbox.setChecked(self.config.get_startup())
        
        # 加載關閉行為設置
        self.minimize_to_tray.setChecked(self.config.get_minimize_to_tray())
        
        # 設置當前主題
        current_theme = self.config.get_theme()
        # 查找主題在下拉列表中的索引
        index = self.theme_combo.findText(current_theme.title())
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
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
        # 構建熱鍵字符串
        modifiers = []
        if self.shift_check.isChecked():
            modifiers.append("shift")
        if self.ctrl_check.isChecked():
            modifiers.append("ctrl")
        if self.alt_check.isChecked():
            modifiers.append("alt")
        if self.win_check.isChecked():
            modifiers.append("win")
            
        key = self.key_edit.text().lower()
        if key:
            modifiers.append(key)
            
        new_hotkey = "+".join(modifiers)
        
        # 保存熱鍵設置
        if new_hotkey != self.config.get_hotkey():
            self.config.set_hotkey(new_hotkey)
            # 更新全局熱鍵
            app = QApplication.instance()
            if hasattr(app, 'hotkey_manager'):
                app.hotkey_manager.register_hotkey(new_hotkey)
        
        # Save general settings
        self.config.set_startup(self.startup_checkbox.isChecked())
        
        # 應用主題
        theme_text = self.theme_combo.currentText()  # 不要轉換為小寫
        print(f"Selected theme: {theme_text}")
        self.config.set_theme(theme_text.lower())  # 保存時轉換為小寫
        ThemeManager.apply_theme(theme_text.lower())
        
        # Save storage settings
        self.config.set_storage_path(self.path_edit.text())
        self.config.set_max_items(self.max_items_spin.value())
        
        # Save close behavior settings
        self.config.set_minimize_to_tray(self.minimize_to_tray.isChecked())
        
        # Close dialog
        super().accept() 
