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
        self.is_pressed = False  # add key state tracking
        
        # Register hotkey in a separate thread
        self.thread = threading.Thread(target=self._register_hotkey_thread, args=(hotkey,))
        self.thread.daemon = True
        self.thread.start()
        
    def _register_hotkey_thread(self, hotkey):
        """Register hotkey in a separate thread"""
        try:
            # make sure the hotkey is in lowercase
            parts = hotkey.lower().split('+')
            self.main_key = parts[-1]
            self.modifiers = set(parts[:-1])  # use set to store modifiers
            
            # only listen to the main key, not suppress events
            keyboard.on_press_key(self.main_key, self._on_press, suppress=False)
            keyboard.on_release_key(self.main_key, self._on_release, suppress=False)
            
            self.active = True
            while self.active:
                time.sleep(0.1)
        except Exception as e:
            print(f"Error registering hotkey: {e}")
            
    def _on_press(self, event):
        """Handle key press event"""
        if not self.is_pressed:  # make sure the hotkey is not pressed
            # check if all required modifiers are pressed
            current_modifiers = set()
            if keyboard.is_pressed('shift'): current_modifiers.add('shift')
            if keyboard.is_pressed('ctrl'): current_modifiers.add('ctrl')
            if keyboard.is_pressed('alt'): current_modifiers.add('alt')
            if keyboard.is_pressed('win'): current_modifiers.add('win')
            
            # only trigger when all required modifiers are pressed
            if current_modifiers == self.modifiers:
                self.is_pressed = True
                self._safe_callback()
    
    def _on_release(self, event):
        """Handle key release event"""
        self.is_pressed = False
            
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
            # unregister old hotkey first
            if self.active:
                self.unregister_hotkey()
            
            # Reset state
            self.is_pressed = False
            self.active = False
            
            # 更新熱鍵
            self.hotkey = hotkey
            
            # register new hotkey in a separate thread
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
            try:
                # Remove both press and release handlers
                keyboard.unhook_all()  # remove all keyboard hooks
                self.active = False
                # Wait for thread to terminate
                if self.thread and self.thread.is_alive():
                    self.thread.join(1.0)
            except Exception as e:
                print(f"Error unregistering hotkey: {e}")
