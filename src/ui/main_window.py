#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window Module
The main application window for the clipboard history manager.
"""

import os
import sys
import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QListWidget, QListWidgetItem, QMenu,
    QSystemTrayIcon, QLabel, QTabWidget, QDialog,
    QMessageBox, QApplication, QStyle, QSplitter, QTextEdit,
    QCalendarWidget, QComboBox, QLineEdit
)
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction, QColor
from PyQt6.QtCore import Qt, QSize, QBuffer, QByteArray, QIODevice, QMetaObject, Q_ARG, pyqtSignal, QUrl, QMimeData, QTimer
from datetime import datetime, timedelta

from ui.settings_dialog import SettingsDialog
from models.clipboard_item import ClipboardItem
from ui.filter_tab import FilterTab

class MainWindow(QMainWindow):
    def __init__(self, storage_manager, config_manager):
        """
        Initialize main window
        
        Args:
            storage_manager: StorageManager instance
            config_manager: ConfigManager instance
        """
        super().__init__()
        
        self.storage = storage_manager
        self.config = config_manager
        self.clipboard = QApplication.clipboard()
        
        self.setWindowTitle("ClipClip History" + " " + self.get_version())
        self.setMinimumSize(600, 400)
        
        # set window flags
        self.setWindowFlags(
            Qt.WindowType.Window |  # general window
            Qt.WindowType.WindowStaysOnTopHint |  # stay on top
            Qt.WindowType.WindowCloseButtonHint |  # close button
            Qt.WindowType.WindowMinimizeButtonHint  # minimize button
        )
        
        # set focus policy
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Create system tray icon
        self.setup_tray_icon()
        
        # Create UI
        self.setup_ui()
        
        # Load initial items
        self.load_clipboard_items()
        
        # connect clipboard monitor signal
        if hasattr(QApplication, 'clipboard_monitor'):
            QApplication.clipboard_monitor.item_added_signal.connect(self.load_clipboard_items)
        
        # Show window initially
        self.show()

    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)

    def get_version(self):
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
        
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # History tab
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "All History")
        
        # Filter tab
        self.filter_tab = FilterTab(self)
        self.tabs.addTab(self.filter_tab, "Filter")
        
        main_layout.addWidget(self.tabs)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("Clear History")
        self.clear_button.clicked.connect(self.clear_history)
        
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(button_layout)
        
    def setup_history_tab(self):
        """Setup the history tab"""
        layout = QVBoxLayout(self.history_tab)
        
        # add search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)  # bottom spacing
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords to search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # clear search button
        clear_button = QPushButton("Clear")
        clear_button.setFixedWidth(60)
        clear_button.clicked.connect(lambda: self.search_input.clear())
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(clear_button)
        
        layout.addLayout(search_layout)
        
        # Create list widget for clipboard items
        self.items_list = QListWidget()
        self.items_list.setIconSize(QSize(40, 40))
        self.items_list.setAlternatingRowColors(True)
        self.items_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.items_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.items_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # set auto adjust size
        self.items_list.setWordWrap(True)
        self.items_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        layout.addWidget(self.items_list)
        
    def setup_tray_icon(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Get correct path to icon file
        current_dir = os.path.dirname(os.path.dirname(__file__))  # go up one level to src
        icon_path = os.path.join(current_dir, "resources", "clip_clip_icon.svg")
        
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")
            # Use system default icon
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        
        self.tray_icon.setToolTip("ClipClip History")
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # Show the tray icon
        self.tray_icon.show()
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_visibility()
            
    def toggle_visibility(self):
        """Toggle window visibility"""
        print("Toggle visibility called")
        try:
            if self.isVisible():
                print("Hiding window")
                self.hide()
            else:
                print("Showing window")
                self.show()
                self.activateWindow()
                self.raise_()
                # force window to the front
                self.setWindowState((self.windowState() & ~Qt.WindowState.WindowMinimized) | Qt.WindowState.WindowActive)
                # set focus
                self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
                # delay setting focus to ensure window is fully displayed
                QTimer.singleShot(100, lambda: self.setFocus(Qt.FocusReason.ActiveWindowFocusReason))
        except Exception as e:
            print(f"Error in toggle_visibility: {e}")
            
            
    def load_clipboard_items(self):
        """Load clipboard items from storage"""
        items = self.storage.get_items()
        self._populate_items_list(self.items_list, items)

        current_filter = self.filter_tab.filter_combo.currentIndex()
        if current_filter == 0:  # Last 30 days
            self.filter_tab.filter_items(30)
        elif current_filter == 1:  # Last 7 days
            self.filter_tab.filter_items(7)
        elif current_filter == 2:  # Today
            self.filter_tab.filter_items(1)
        elif current_filter == 3:  # Custom date
            selected_date = self.filter_tab.calendar.selectedDate()
            self.filter_tab.filter_items_by_date(selected_date.toPyDate())

        
    def show_context_menu(self, position):
        """Show context menu for clipboard items"""
        item = self.items_list.itemAt(position)
        if not item:
            return
            
        # Get item ID
        item_id = item.data(Qt.ItemDataRole.UserRole)
        
        # get item
        items = self.storage.get_items()
        selected_item = None
        for i in items:
            if i.id == item_id:
                selected_item = i
                break
                
        if not selected_item or selected_item.content_type != "text":
            return
        
        # Create context menu
        context_menu = QMenu()
        
        # Add pin/unpin option
        if selected_item.pinned:
            pin_action = QAction("Unpin", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item_id, False))
        else:
            pin_action = QAction("Pin", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item_id, True))
        
        view_action = QAction("View", self)
        view_action.triggered.connect(lambda: self.view_clipboard_item(selected_item))
        
        use_action = QAction("Copy", self)
        use_action.triggered.connect(lambda: self.use_clipboard_item(item))
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_clipboard_item(item_id))
        
        context_menu.addAction(pin_action)
        context_menu.addSeparator()
        context_menu.addAction(view_action)
        context_menu.addAction(use_action)
        context_menu.addAction(delete_action)
        
        # Show the menu
        context_menu.exec(self.items_list.mapToGlobal(position))
        
    def view_clipboard_item(self, item):
        """View full content of a clipboard item"""
        dialog = QDialog(self)
        dialog.setWindowTitle("View Content")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # add time label
        time_label = QLabel(f"Copied at: {item.get_formatted_time()}")
        layout.addWidget(time_label)
        
        # create text display area
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(item.content)
        layout.addWidget(text_edit)
        
        # create button layout
        button_layout = QHBoxLayout()
        
        # add copy button
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(lambda: self.copy_from_dialog(item))
        
        # add close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
        
    def copy_from_dialog(self, item):
        """Copy content from view dialog"""
        try:
            # set ignore flag
            if hasattr(QApplication.instance(), 'clipboard_monitor'):
                QApplication.instance().clipboard_monitor.ignore_next_change = True
            
            # copy to clipboard
            self.clipboard.setText(item.content)
            
            # get the button that sent the signal (copy_button)
            copy_button = self.sender()
            if copy_button:
                # temporarily change button text
                copy_button.setText("Copied!")
                # disable button to prevent duplicate clicks
                copy_button.setEnabled(False)
            
            # show notification
            self.tray_icon.showMessage(
                "Clipboard History",
                "Text copied to clipboard",
                QSystemTrayIcon.MessageIcon.Information,
                1000  # show for 1 second
            )
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            QMessageBox.warning(self, "Copy Error", f"Failed to copy item: {str(e)}")
        
    def use_clipboard_item(self, item):
        """Use a clipboard item (copy to clipboard)"""
        # Get item ID
        item_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Get all items
        items = self.storage.get_items()
        
        # Find the selected item
        selected_item = None
        for i in items:
            if i.id == item_id:
                selected_item = i
                break
                
        if not selected_item:
            return
            
        try:
            # only process text
            if selected_item.content_type == "text":
                print(f"Copying text: {selected_item.content[:30]}...")
                # set ignore flag
                if hasattr(QApplication.instance(), 'clipboard_monitor'):
                    QApplication.instance().clipboard_monitor.ignore_next_change = True
                # copy to clipboard
                self.clipboard.setText(selected_item.content)
            else:
                print(f"Skipping non-text item: {selected_item.content_type}")
                return
            
            # ensure clipboard data is set
            print(f"Clipboard text after copy: {self.clipboard.text()}")
            
            # Show notification
            self.tray_icon.showMessage(
                "Clipboard History",
                "Copied text to clipboard",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            QMessageBox.warning(self, "Copy Error", f"Failed to copy item: {str(e)}")
        
    def delete_clipboard_item(self, item_id):
        """Delete a clipboard item"""
        show_confirmation = QMessageBox.question(
            self,
            "Delete Item",
            "Are you sure you want to delete this item?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if show_confirmation == QMessageBox.StandardButton.Yes:
            # Delete from storage
            self.storage.delete_item(item_id)
            # Reload items
            self.load_clipboard_items()
        else:
            return
        
    def clear_history(self):
        """Clear all clipboard history"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self, 
            "Clear History", 
            "Are you sure you want to clear all clipboard history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Clear storage
            self.storage.clear_history()
            
            # Reload items
            self.load_clipboard_items()
            
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog(self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reload items if settings changed
            self.load_clipboard_items()
            
    def quit_application(self):
        """Quit the application"""
        QApplication.quit()
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.config.get_minimize_to_tray():
            event.ignore()
            self.hide()
        else:
            event.accept()
            QApplication.quit()
        
    def on_item_double_clicked(self, item):
        """Handle double click on item"""
        # Get item ID
        item_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Get all items
        items = self.storage.get_items()
        
        # Find the selected item
        selected_item = None
        for i in items:
            if i.id == item_id:
                selected_item = i
                break
            
        if selected_item:
            self.view_clipboard_item(selected_item)

    def show_context_menu_at_pos(self, list_widget, global_pos):
        """Show context menu at the specified global position"""
        item = list_widget.itemAt(list_widget.mapFromGlobal(global_pos))
        if not item:
            return
        
        # Get item ID
        item_id = item.data(Qt.ItemDataRole.UserRole)
        
        # get item
        items = self.storage.get_items()
        selected_item = None
        for i in items:
            if i.id == item_id:
                selected_item = i
                break
            
        if not selected_item or selected_item.content_type != "text":
            return
        
        # Create context menu
        context_menu = QMenu()

        # Add pin/unpin option
        if selected_item.pinned:
            pin_action = QAction("Unpin", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item_id, False))
        else:
            pin_action = QAction("Pin", self)
            pin_action.triggered.connect(lambda: self.toggle_pin_item(item_id, True))
        
        
        view_action = QAction("View", self)
        view_action.triggered.connect(lambda: self.view_clipboard_item(selected_item))
        
        use_action = QAction("Copy", self)
        use_action.triggered.connect(lambda: self.use_clipboard_item(item))
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_clipboard_item(item_id))
        
        context_menu.addAction(pin_action)
        context_menu.addSeparator()
        context_menu.addAction(view_action)
        context_menu.addAction(use_action)
        context_menu.addAction(delete_action)
        
        # show in the correct position
        context_menu.exec(global_pos)

    def on_search_changed(self, text):
        """Handle search text change"""
        items = self.storage.get_items()
        self.items_list.clear()
        
        # if search text is empty, show all items
        if not text:
            self._populate_items_list(self.items_list, items)
            return
        
        # filter items
        search_text = text.lower()
        filtered_items = [
            item for item in items
            if item.content_type == "text" and search_text in item.content.lower()
        ]
        
        self._populate_items_list(self.items_list, filtered_items)

    def toggle_pin_item(self, item_id, pinned):
        """Toggle pin status of an item"""
        self.storage.toggle_pin_item(item_id, pinned)
        
        # Refresh both main list and filter tab list
        self.load_clipboard_items()


    def _populate_items_list(self, list_widget, items):
        """Populate list widget with items"""
        list_widget.clear()
        
        # Separate pinned and unpinned items
        pinned_items = [item for item in items if item.pinned]
        unpinned_items = [item for item in items if not item.pinned]
        
        # Sort both lists by timestamp (newest first)
        pinned_items.sort(key=lambda x: x.timestamp, reverse=True)
        unpinned_items.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Add pinned items first
        for item in pinned_items:
            self._add_item_to_list(list_widget, item)
        
        # Add unpinned items
        for item in unpinned_items:
            self._add_item_to_list(list_widget, item)

    def _add_item_to_list(self, list_widget, item):
        """Add a single item to the list widget"""
        if item.content_type != "text":
            return
        
        list_item = QListWidgetItem()
        
        # Set icon
        icon = QIcon.fromTheme("edit-copy")
        if icon.isNull():
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        list_item.setIcon(icon)
        
        # Get list width for text processing
        list_width = list_widget.viewport().width()
        max_text_width = list_width - 30  # subtract icon and margin width
        char_width = 8  # estimated value
        max_chars = max(30, int(max_text_width / char_width))
        
        # Process text
        text = item.content
        
        # Handle multiple lines
        if '\n' in text:
            lines = text.split('\n')
            text = next((line.strip() for line in lines if line.strip()), '')
        
        # Remove extra spaces
        text = text.strip()
        if not text:
            return
        
        # Normalize spaces
        text = ' '.join(text.split())
        
        # Truncate if too long
        if len(text) > max_chars:
            last_space = text.rfind(' ', 0, max_chars)
            if last_space > max_chars // 2:
                text = text[:last_space] + "..."
            else:
                text = text[:max_chars] + "..."
        
        # Get timestamp
        time_str = item.get_formatted_time()
        
        # Create display text
        display_text = f"{text}\n{time_str}"
        
        # Add pin indicator if pinned
        if item.pinned:
            display_text = f"{display_text}    📌"
        
        list_item.setText(display_text)
        
        # Store item ID
        list_item.setData(Qt.ItemDataRole.UserRole, item.id)
        
        list_widget.addItem(list_item) 
