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
from PyQt6.QtGui import QIcon, QPixmap, QImage, QAction
from PyQt6.QtCore import Qt, QSize, QBuffer, QByteArray, QIODevice, QMetaObject, Q_ARG, pyqtSignal, QUrl, QMimeData, QTimer
from datetime import datetime, timedelta

from ui.settings_dialog import SettingsDialog
from models.clipboard_item import ClipboardItem
from ui.filter_tab import FilterTab  # 添加這行

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
        
        self.setWindowTitle("ClipClip History")
        self.setMinimumSize(600, 400)
        
        # 設置窗口屬性，使其能夠接收全局快捷鍵
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        # Create system tray icon
        self.setup_tray_icon()
        
        # Create UI
        self.setup_ui()
        
        # Load initial items
        self.load_clipboard_items()
        
        # 連接剪貼板監視器的信號
        if hasattr(QApplication, 'clipboard_monitor'):
            QApplication.clipboard_monitor.item_added_signal.connect(self.load_clipboard_items)
        
        # Show window initially
        self.show()
        
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
        
        # 添加搜索欄
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)  # 底部間距
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords to search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # 清除搜索按鈕
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
        
        # 設置自動調整大小
        self.items_list.setWordWrap(True)
        self.items_list.setTextElideMode(Qt.TextElideMode.ElideRight)
        
        layout.addWidget(self.items_list)
        
    def setup_tray_icon(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Use system clipboard icon if available, otherwise use a default
        icon = QIcon.fromTheme("edit-paste")
        if icon.isNull():
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Clipboard History")
        
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
                # 確保窗口在前台
                self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        except Exception as e:
            print(f"Error in toggle_visibility: {e}")
            
    def load_clipboard_items(self):
        """Load clipboard items from storage"""
        self.items_list.clear()
        
        items = self.storage.get_items()
        
        # 獲取列表寬度，用於計算最大文本長度
        list_width = self.items_list.viewport().width()
        max_text_width = list_width - 30  # 減去圖標和邊距的寬度
        
        # 估算每個字符的平均寬度（像素）
        char_width = 8  # 估計值，可以根據實際字體調整
        max_chars = max(30, int(max_text_width / char_width))
        
        for item in items:
            list_item = QListWidgetItem()
            
            # 只處理文本項目
            if item.content_type != "text":
                continue
            
            # Set icon
            icon = QIcon.fromTheme("edit-copy")
            if icon.isNull():
                icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            list_item.setIcon(icon)
            
            # 獲取顯示文本並處理
            text = item.content
            
            # 尋找第一個非空的行
            if '\n' in text:
                lines = text.split('\n')
                text = next((line.strip() for line in lines if line.strip()), '')
            
            # 去除前後空白
            text = text.strip()
            
            # 如果所有行都是空的，跳過這個項目
            if not text:
                continue
            
            # 處理中間的多餘空白
            text = ' '.join(text.split())  # 將多個空白壓縮為一個
            
            # 如果文本超過最大長度，在有意義的位置截斷
            if len(text) > max_chars:
                # 尋找最後一個完整單詞的位置
                last_space = text.rfind(' ', 0, max_chars)
                if last_space > max_chars // 2:  # 如果找到合適的空格
                    text = text[:last_space] + "..."
                else:
                    text = text[:max_chars] + "..."
            
            # Add timestamp
            time_str = item.get_formatted_time()
            list_item.setText(f"{text}\n{time_str}")
            
            # Store the item ID as user data
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            
            self.items_list.addItem(list_item)
            
    def show_context_menu(self, position):
        """Show context menu for clipboard items"""
        item = self.items_list.itemAt(position)
        if not item:
            return
            
        # Get item ID
        item_id = item.data(Qt.ItemDataRole.UserRole)
        
        # 獲取項目
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
        
        # 添加查看選項
        view_action = QAction("View", self)
        view_action.triggered.connect(lambda: self.view_clipboard_item(selected_item))
        
        use_action = QAction("Copy", self)
        use_action.triggered.connect(lambda: self.use_clipboard_item(item))
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_clipboard_item(item_id))
        
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
        
        # 添加時間標籤
        time_label = QLabel(f"Copied at: {item.get_formatted_time()}")
        layout.addWidget(time_label)
        
        # 創建文本顯示區域
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText(item.content)
        layout.addWidget(text_edit)
        
        # 創建按鈕佈局
        button_layout = QHBoxLayout()
        
        # 添加複製按鈕
        copy_button = QPushButton("Copy")
        copy_button.clicked.connect(lambda: self.copy_from_dialog(item))
        
        # 添加關閉按鈕
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
        
    def copy_from_dialog(self, item):
        """Copy content from view dialog"""
        try:
            # 設置忽略標誌
            if hasattr(QApplication.instance(), 'clipboard_monitor'):
                QApplication.instance().clipboard_monitor.ignore_next_change = True
            
            # 複製到剪貼板
            self.clipboard.setText(item.content)
            
            # 獲取發送信號的按鈕（copy_button）
            copy_button = self.sender()
            if copy_button:
                # 暫時改變按鈕文字
                copy_button.setText("Copied!")
                # 禁用按鈕防止重複點擊
                copy_button.setEnabled(False)
            
            # 顯示通知
            self.tray_icon.showMessage(
                "Clipboard History",
                "Text copied to clipboard",
                QSystemTrayIcon.MessageIcon.Information,
                1000  # 顯示1秒
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
            # 只處理文本
            if selected_item.content_type == "text":
                print(f"Copying text: {selected_item.content[:30]}...")
                # 設置忽略標誌
                if hasattr(QApplication.instance(), 'clipboard_monitor'):
                    QApplication.instance().clipboard_monitor.ignore_next_change = True
                # 複製到剪貼板
                self.clipboard.setText(selected_item.content)
            else:
                print(f"Skipping non-text item: {selected_item.content_type}")
                return
            
            # 確保剪貼板數據已設置
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
        # Delete from storage
        self.storage.delete_item(item_id)
        
        # Reload items
        self.load_clipboard_items()
        
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
        """處理窗口關閉事件"""
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
        
        # 獲取項目
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
        
        view_action = QAction("View", self)
        view_action.triggered.connect(lambda: self.view_clipboard_item(selected_item))
        
        use_action = QAction("Copy", self)
        use_action.triggered.connect(lambda: self.use_clipboard_item(item))
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_clipboard_item(item_id))
        
        context_menu.addAction(view_action)
        context_menu.addAction(use_action)
        context_menu.addAction(delete_action)
        
        # 在正確的位置顯示菜單
        context_menu.exec(global_pos)

    def _populate_items_list(self, list_widget, items):
        """Populate list widget with items"""
        # 獲取列表寬度
        list_width = list_widget.viewport().width()
        max_text_width = list_width - 30
        char_width = 8
        max_chars = max(30, int(max_text_width / char_width))
        
        for item in items:
            if item.content_type != "text":
                continue
            
            list_item = QListWidgetItem()
            
            # Set icon
            icon = QIcon.fromTheme("edit-copy")
            if icon.isNull():
                icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            list_item.setIcon(icon)
            
            # 處理文本
            text = item.content
            if '\n' in text:
                lines = text.split('\n')
                text = next((line.strip() for line in lines if line.strip()), '')
            
            text = text.strip()
            if not text:
                continue
            
            text = ' '.join(text.split())
            
            if len(text) > max_chars:
                last_space = text.rfind(' ', 0, max_chars)
                if last_space > max_chars // 2:
                    text = text[:last_space] + "..."
                else:
                    text = text[:max_chars] + "..."
            
            # Add timestamp
            time_str = item.get_formatted_time()
            list_item.setText(f"{text}\n{time_str}")
            
            # Store item ID
            list_item.setData(Qt.ItemDataRole.UserRole, item.id)
            
            list_widget.addItem(list_item)

    def on_search_changed(self, text):
        """處理搜索文本變化"""
        items = self.storage.get_items()
        self.items_list.clear()
        
        # 如果搜索文本為空，顯示所有項目
        if not text:
            self._populate_items_list(self.items_list, items)
            return
        
        # 過濾項目
        search_text = text.lower()
        filtered_items = [
            item for item in items
            if item.content_type == "text" and search_text in item.content.lower()
        ]
        
        self._populate_items_list(self.items_list, filtered_items) 
