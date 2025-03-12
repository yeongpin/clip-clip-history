#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration Manager Module
Manages application settings and configuration.
"""

import os
import sys
import json
import tempfile

class ConfigManager:
    def __init__(self, config_path=None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to configuration file
        """
        if not config_path:
            # Default to user's home directory
            config_dir = os.path.join(os.path.expanduser("~"), ".clipboard_history")
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, "config.json")
            
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self):
        """Load configuration from file"""
        default_config = {
            "hotkey": "ctrl+shift+q",
            "max_items": 100,
            "storage_path": os.path.join(tempfile.gettempdir(), "clipboard_history"),
            "startup": False,
            "theme": "system"
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**default_config, **config}
            except Exception as e:
                print(f"Error loading config: {e}")
                
        return default_config
        
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def get_hotkey(self):
        """Get global hotkey"""
        return self.config.get("hotkey")
        
    def set_hotkey(self, hotkey):
        """Set global hotkey"""
        self.config["hotkey"] = hotkey
        self.save_config()
        
    def get_max_items(self):
        """Get maximum number of items to store"""
        return self.config.get("max_items", 100)
        
    def set_max_items(self, max_items):
        """Set maximum number of items to store"""
        self.config["max_items"] = max_items
        self.save_config()
        
    def get_storage_path(self):
        """Get storage path"""
        return self.config.get("storage_path")
        
    def set_storage_path(self, path):
        """Set storage path"""
        self.config["storage_path"] = path
        self.save_config()
        
    def get_startup(self):
        """Get startup setting"""
        return self.config.get("startup", False)
        
    def set_startup(self, enabled):
        """Set startup setting"""
        self.config["startup"] = enabled
        self.save_config()
        
        # Implement platform-specific startup registration
        if enabled:
            self._register_startup()
        else:
            self._unregister_startup()
            
    def get_theme(self):
        """Get UI theme"""
        return self.config.get("theme", "system")
        
    def set_theme(self, theme):
        """Set UI theme"""
        self.config["theme"] = theme
        self.save_config()
        
    def _register_startup(self):
        """Register application to start on system boot"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, "ClipboardHistory", 0, winreg.REG_SZ, sys.executable + " " + os.path.abspath(__file__))
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Error registering startup: {e}")
                
        elif system == "Darwin":  # macOS
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.clipboardhistory.plist")
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clipboardhistory</string>
    <key>ProgramArguments</key>
    <array>
        <string>{sys.executable}</string>
        <string>{os.path.abspath(__file__)}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""
            try:
                with open(plist_path, 'w') as f:
                    f.write(plist_content)
            except Exception as e:
                print(f"Error registering startup: {e}")
                
        elif system == "Linux":
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_path = os.path.join(autostart_dir, "clipboard-history.desktop")
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Clipboard History
Exec={sys.executable} {os.path.abspath(__file__)}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
            try:
                with open(desktop_path, 'w') as f:
                    f.write(desktop_content)
                os.chmod(desktop_path, 0o755)
            except Exception as e:
                print(f"Error registering startup: {e}")
                
    def _unregister_startup(self):
        """Unregister application from starting on system boot"""
        import platform
        system = platform.system()
        
        if system == "Windows":
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                winreg.DeleteValue(key, "ClipboardHistory")
                winreg.CloseKey(key)
            except Exception as e:
                print(f"Error unregistering startup: {e}")
                
        elif system == "Darwin":  # macOS
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.clipboardhistory.plist")
            if os.path.exists(plist_path):
                try:
                    os.remove(plist_path)
                except Exception as e:
                    print(f"Error unregistering startup: {e}")
                    
        elif system == "Linux":
            desktop_path = os.path.expanduser("~/.config/autostart/clipboard-history.desktop")
            if os.path.exists(desktop_path):
                try:
                    os.remove(desktop_path)
                except Exception as e:
                    print(f"Error unregistering startup: {e}") 
