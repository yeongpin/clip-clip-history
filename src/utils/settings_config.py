import os
import configparser
from utils.config_manager import ConfigManager

class SettingsConfig:
    """manage application settings configuration"""
    
    # 默認配置
    DEFAULT_CONFIG = {
        'General': {
            'hotkey': 'ctrl+shift+q',
            'startup': 'false',
            'theme': 'system',
            'minimize_to_tray': 'true'
        },
        'Storage': {
            'max_items': '100',
            'path': os.path.join(os.path.expanduser('~/Documents'), '.clip-history', 'storage')
        }
    }
    
    def __init__(self):
        # set config file path
        self.docs_path = os.path.expanduser('~/Documents')
        self.config_dir = os.path.join(self.docs_path, '.clip-history')
        self.config_file = os.path.join(self.config_dir, 'settings.ini')
        
        # ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        # initialize config parser
        self.config = configparser.ConfigParser()
        
        # load or create config
        self.load_config()
    
    def load_config(self):
        """load config file, create default if not exists"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self._ensure_defaults()
        else:
            self._create_default_config()
    
    def _ensure_defaults(self):
        """ensure all default config options exist, but keep existing values"""
        modified = False
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                modified = True
            
            # add missing options, do not overwrite existing values
            for key, default_value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, default_value)
                    modified = True
                    print(f"Added missing config option: [{section}] {key} = {default_value}")
        
        # save only if modified
        if modified:
            self.save_config()
            print("Updated config file with new default options")
    
    def _create_default_config(self):
        """create default config file"""
        for section, options in self.DEFAULT_CONFIG.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save_config()
    
    def save_config(self):
        """save config to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    # get and set config value
    def get(self, section, key, fallback=None):
        """get config value"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """set config value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
    
    # shortcut method - hotkey
    def get_hotkey(self):
        """get shortcut key setting"""
        return self.get('General', 'hotkey', 'ctrl+shift+q')
    
    def set_hotkey(self, hotkey):
        """set shortcut key"""
        self.set('General', 'hotkey', hotkey)
    
    # shortcut method - theme
    def get_theme(self):
        """get theme setting"""
        return self.get('General', 'theme', 'system')
    
    def set_theme(self, theme):
        """set theme"""
        self.set('General', 'theme', theme)
    
    # shortcut method - startup
    def get_startup(self):
        """get startup setting"""
        return self.get('General', 'startup', 'false').lower() == 'true'
    
    def set_startup(self, enabled):
        """set startup"""
        self.set('General', 'startup', str(enabled).lower())
        
        # Implement platform-specific startup registration
        if enabled:
            ConfigManager.register_startup()
        else:
            ConfigManager.unregister_startup()
        
    # shortcut method - storage related
    def get_storage_path(self):
        """get storage path"""
        default_path = os.path.join(self.config_dir, 'storage')
        return self.get('Storage', 'path', default_path)
    
    def set_storage_path(self, path):
        """set storage path"""
        self.set('Storage', 'path', path)
    
    def get_max_items(self):
        """get max item count"""
        return int(self.get('Storage', 'max_items', '100'))
    
    def set_max_items(self, count):
        """set max item count"""
        self.set('Storage', 'max_items', str(count))
    
    def upgrade_config(self, new_version):
        """handle config file version upgrade"""
        current_version = self.get('General', 'version', '1.0')
        if current_version != new_version:
            print(f"Upgrading config from version {current_version} to {new_version}")
            # add version upgrade logic here
            self.set('General', 'version', new_version)
    
    def get_minimize_to_tray(self):
        """get close button behavior setting"""
        return self.get('General', 'minimize_to_tray', 'true').lower() == 'true'
    
    def set_minimize_to_tray(self, value):
        """set close button behavior"""
        self.set('General', 'minimize_to_tray', str(value).lower()) 