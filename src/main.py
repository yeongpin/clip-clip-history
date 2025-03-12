#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clipboard History Manager
A lightweight clipboard history tool that supports text, images, videos, and files.
"""

import sys
import os
import keyboard
import threading
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QKeySequence, QAction
from PyQt6.QtCore import QObject, pyqtSignal, Qt

from ui.main_window import MainWindow
from clipboard_monitor import ClipboardMonitor
from utils.settings_config import SettingsConfig
from utils.hotkey_manager import HotkeyManager
from storage_manager import StorageManager
from utils.theme_manager import ThemeManager

# 創建一個全局信號類
class GlobalSignals(QObject):
    item_added = pyqtSignal()
    toggle_visibility = pyqtSignal()

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ClipClip History")
    
    # Initialize components
    config = SettingsConfig()
    
    # 初始化主題
    ThemeManager.init_themes()
    
    # 設置應用圖標
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "clipclip_icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Icon file not found at {icon_path}")
        # 使用系統默認圖標
        app.setWindowIcon(app.style().standardIcon(app.style().StandardPixmap.SP_DialogSaveButton))
    
    # 應用主題
    current_theme = config.get_theme()
    print(f"Applying theme: {current_theme}")
    ThemeManager.apply_theme(current_theme)
    
    # 定義 toggle_window 函數
    def toggle_window():
        app.global_signals.toggle_visibility.emit()
    
    # 創建全局信號
    app.global_signals = GlobalSignals()
    
    storage = StorageManager(config.get_storage_path())
    
    # Create main window
    main_window = MainWindow(storage, config)
    main_window.show()
    
    # Initialize clipboard monitor
    clipboard_monitor = ClipboardMonitor(app.clipboard(), storage)
    app.clipboard_monitor = clipboard_monitor
    app.global_signals.item_added.connect(main_window.load_clipboard_items)
    app.global_signals.toggle_visibility.connect(main_window.toggle_visibility)
    clipboard_monitor.item_added_signal = app.global_signals.item_added
    clipboard_monitor.start()
    
    # 設置全局快捷鍵
    hotkey_str = config.get_hotkey()
    hotkey_manager = HotkeyManager(hotkey_str, toggle_window)
    app.hotkey_manager = hotkey_manager
    
    # 在單獨的線程中註冊快捷鍵
    def register_hotkey():
        try:
            keyboard.add_hotkey(hotkey_str, toggle_window)
            print(f"Global hotkey registered: {hotkey_str}")
        except Exception as e:
            print(f"Error registering global hotkey: {e}")
    
    hotkey_thread = threading.Thread(target=register_hotkey)
    hotkey_thread.daemon = True
    hotkey_thread.start()
    
    print("Application started")
    print("Window should be visible now")
    
    # 設置 Ctrl+C 處理
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # 允許 Ctrl+C 終止程序
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 
