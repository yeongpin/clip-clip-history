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
    QGroupBox, QTabWidget, QWidget, QApplication, QTextBrowser
)
from PyQt6.QtCore import Qt
from utils.theme_manager import ThemeManager
import webbrowser
import sys

class SettingsDialog(QDialog):
    def __init__(self, config_manager, parent=None):
        """
        Initialize settings dialog
        
        Args:
            config_manager: ConfigManager instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        # directly use SettingsConfig
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
        
        # modifier checkbox
        modifier_layout = QHBoxLayout()
        self.shift_check = QCheckBox("Shift")
        self.ctrl_check = QCheckBox("Ctrl")
        self.alt_check = QCheckBox("Alt")
        self.win_check = QCheckBox("Win")
        
        modifier_layout.addWidget(self.shift_check)
        modifier_layout.addWidget(self.ctrl_check)
        modifier_layout.addWidget(self.alt_check)
        modifier_layout.addWidget(self.win_check)
        
        # key input box
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Key:"))
        self.key_edit = QLineEdit()
        
        # Add key press event handler
        self.key_edit.keyPressEvent = self.handle_key_press
        self.key_edit.setReadOnly(True)  # Make it read-only to handle input manually
        
        key_layout.addWidget(self.key_edit)
        
        hotkey_layout.addLayout(modifier_layout)
        hotkey_layout.addLayout(key_layout)
        
        # add help label
        help_label = QLabel("Recommended: Use function keys (F1-F12) or special keys\n"
                           "to avoid blocking normal keyboard input.")
        help_label.setStyleSheet("color: gray;")
        hotkey_layout.addWidget(help_label)
        
        general_layout.addWidget(hotkey_group)
        
        # Startup settings
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.startup_checkbox = QCheckBox("Start on system boot")
        startup_layout.addWidget(self.startup_checkbox)
        
        # add close behavior settings
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
        
        # add all available themes
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
        
        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)
        
        # Load version from .env
        version = self.load_version()

        author = self.load_author()
        project_url = self.load_project_url()
        
        # App info
        info_text = f"""
        <h2>ClipClip History</h2>
        <p>Version: {version}</p>
        <p>A lightweight clipboard history manager.</p>
        <br>
        <p><b>Author:</b> {author}</p>
        <p><b>GitHub:</b> <a href="{project_url}">{project_url}</a></p>
        """
        
        info_label = QLabel(info_text)
        info_label.setOpenExternalLinks(True)
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        about_layout.addWidget(info_label)

        github_button = QPushButton("GitHub")
        github_button.clicked.connect(self.open_github)
        about_layout.addWidget(github_button)
        
        # Check for updates button
        update_button = QPushButton("Check for Updates")
        update_button.clicked.connect(self.check_updates)
        about_layout.addWidget(update_button)
        about_layout.addStretch()
        
        tabs.addTab(about_tab, "About")
        
        # Changelog tab
        changelog_tab = QWidget()
        changelog_layout = QVBoxLayout(changelog_tab)
        
        changelog_browser = QTextBrowser()
        changelog_browser.setOpenExternalLinks(True)
        
        # Load changelog content
        changelog_content = self.load_changelog()
        changelog_browser.setMarkdown(changelog_content)
        
        changelog_layout.addWidget(changelog_browser)
        
        tabs.addTab(changelog_tab, "Changelog")
        
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
        # load hotkey settings
        current_hotkey = self.config.get_hotkey()
        modifiers = current_hotkey.lower().split("+")
        
        # set modifier status
        self.shift_check.setChecked("shift" in modifiers)
        self.ctrl_check.setChecked("ctrl" in modifiers)
        self.alt_check.setChecked("alt" in modifiers)
        self.win_check.setChecked("win" in modifiers)
        
        # set main key
        key = modifiers[-1] if modifiers else ""
        self.key_edit.setText(key.upper())
        
        # Load general settings
        self.startup_checkbox.setChecked(self.config.get_startup())
        
        # load close behavior settings
        self.minimize_to_tray.setChecked(self.config.get_minimize_to_tray())
        
        # set current theme
        current_theme = self.config.get_theme()
        # find theme index in combo box
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
        # build hotkey string
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
        
        # save hotkey settings
        if new_hotkey != self.config.get_hotkey():
            self.config.set_hotkey(new_hotkey)
            # update global hotkey
            app = QApplication.instance()
            if hasattr(app, 'hotkey_manager'):
                app.hotkey_manager.register_hotkey(new_hotkey)
        
        # Save general settings
        self.config.set_startup(self.startup_checkbox.isChecked())
        
        # apply theme
        theme_text = self.theme_combo.currentText()  # no convert to lower
        print(f"Selected theme: {theme_text}")
        self.config.set_theme(theme_text.lower())  # save as lower
        ThemeManager.apply_theme(theme_text.lower())
        
        # Save storage settings
        self.config.set_storage_path(self.path_edit.text())
        self.config.set_max_items(self.max_items_spin.value())
        
        # Save close behavior settings
        self.config.set_minimize_to_tray(self.minimize_to_tray.isChecked())
        
        # Close dialog
        super().accept() 

    def load_author(self):
        """Load author from .env file"""
        try:
            env_path = self.get_resource_path('.env')
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('author'):
                        return line.split('=')[1].strip()
        except Exception as e:
            print(f"Error loading author: {e}")
        return "Unknown"
    
    def load_project_url(self):
        """Load project URL from .env file"""
        try:
            env_path = self.get_resource_path('.env')
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('project_url'):
                        return line.split('=')[1].strip()
        except Exception as e:
            print(f"Error loading project URL: {e}")
            return "Unknown"

    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

    def load_version(self):
        """Load version from .env file"""
        try:
            env_path = self.get_resource_path('.env')
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('version'):
                        return line.split('=')[1].strip()
        except Exception as e:
            print(f"Error loading version: {e}")
        return "Unknown"

    def load_changelog(self):
        """Load changelog from CHANGELOG.md"""
        try:
            changelog_path = self.get_resource_path('CHANGELOG.md')
            with open(changelog_path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading changelog: {e}")
            return "Failed to load changelog"

    def check_updates(self):
        """Check for updates"""
        # TODO: Implement update checking
        pass 

    def open_github(self):
        """Open GitHub page"""
        webbrowser.open(self.load_project_url())

    def handle_key_press(self, event):
        """Handle key press in key edit box"""
        key = None
        
        # Handle function keys
        if Qt.Key.Key_F1 <= event.key() <= Qt.Key.Key_F12:
            key = f"F{event.key() - Qt.Key.Key_F1 + 1}"
        else:
            # Handle normal keys
            key = event.text().upper()
        
        # Update text if we have a valid key
        if key:
            self.key_edit.setText(key)
        elif event.key() in (Qt.Key.Key_Backspace, Qt.Key.Key_Delete):
            self.key_edit.clear()
