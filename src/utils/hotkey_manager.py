#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hotkey Manager Module
Manages global hotkeys for the application.
"""

import keyboard
import threading
import time

class HotkeyManager:
    def __init__(self, hotkey, callback):
        """
        Initialize hotkey manager
        
        Args:
            hotkey: Hotkey string (e.g., "ctrl+shift+q")
            callback: Function to call when hotkey is pressed
        """
        self.hotkey = hotkey
        self.callback = callback
        self.active = False
        self.thread = None
        
        # Register hotkey in a separate thread
        self.thread = threading.Thread(target=self._register_hotkey_thread, args=(hotkey,))
        self.thread.daemon = True
        self.thread.start()
        
    def _register_hotkey_thread(self, hotkey):
        """Register hotkey in a separate thread"""
        try:
            keyboard.add_hotkey(hotkey, self._safe_callback)
            self.active = True
            # Keep thread alive
            while self.active:
                time.sleep(0.1)
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            
    def _safe_callback(self):
        """Safely call the callback function"""
        try:
            # Use threading to avoid blocking the keyboard library
            threading.Thread(target=self.callback).start()
        except Exception as e:
            print(f"Error in hotkey callback: {e}")
            
    def register_hotkey(self, hotkey):
        """Register a new hotkey"""
        try:
            # 先取消註冊舊的熱鍵
            if self.active:
                self.unregister_hotkey()
            
            # 更新熱鍵
            self.hotkey = hotkey
            
            # 在新線程中註冊新的熱鍵
            self.thread = threading.Thread(target=self._register_hotkey_thread, args=(hotkey,))
            self.thread.daemon = True
            self.thread.start()
            
            print(f"Registered new hotkey: {hotkey}")
            return True
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            return False
            
    def unregister_hotkey(self):
        """Unregister the current hotkey"""
        if self.active:
            keyboard.remove_hotkey(self.hotkey)
            self.active = False
            # Wait for thread to terminate
            if self.thread and self.thread.is_alive():
                self.thread.join(1.0) 
