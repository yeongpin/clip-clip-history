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
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QObject, pyqtSignal

from ui.main_window import MainWindow
from clipboard_monitor import ClipboardMonitor
from utils.settings_config import SettingsConfig
from utils.hotkey_manager import HotkeyManager
from storage_manager import StorageManager
from utils.theme_manager import ThemeManager

# Create a global signal class
class GlobalSignals(QObject):
    item_added = pyqtSignal()
    toggle_visibility = pyqtSignal()

# add debounce control
class HotkeyDebouncer:
    def __init__(self, delay=300):  # 300ms delay
        self.delay = delay
        self.timer = None
        self.last_call = 0

    def debounce(self, func):
        current_time = time.time() * 1000  # convert to milliseconds
        if current_time - self.last_call < self.delay:
            return
        self.last_call = current_time
        func()

def main():
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("ClipClip History")
    
    # Initialize components
    config = SettingsConfig()
    
    # Initialize themes
    ThemeManager.init_themes()
    
    # Set application icon
    icon_path = os.path.join(os.path.dirname(__file__), "resources", "clip_clip_icon.svg")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Warning: Icon file not found at {icon_path}")
        # Use system default icon
        app.setWindowIcon(app.style().standardIcon(app.style().StandardPixmap.SP_DialogSaveButton))
    
    # Apply theme
    current_theme = config.get_theme()
    print(f"Applying theme: {current_theme}")
    ThemeManager.apply_theme(current_theme)
    
    # create debouncer
    hotkey_debouncer = HotkeyDebouncer()
    
    # modify toggle_window function
    def toggle_window():
        hotkey_debouncer.debounce(lambda: app.global_signals.toggle_visibility.emit())
    
    # Create global signals
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
    
    # Set global hotkey
    hotkey_str = config.get_hotkey()
    hotkey_manager = HotkeyManager(hotkey_str, toggle_window)
    app.hotkey_manager = hotkey_manager
    
    # Register hotkey in a separate thread
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
    
    # Set Ctrl+C handling
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Allow Ctrl+C to terminate program
    
    # Run application
    return app.exec()

if __name__ == "__main__":
    sys.exit(main()) 
