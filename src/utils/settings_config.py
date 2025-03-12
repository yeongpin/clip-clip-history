import os
import configparser
from pathlib import Path

class SettingsConfig:
    """管理應用程序的設置配置"""
    
    # 默認配置
    DEFAULT_CONFIG = {
        'General': {
            'hotkey': 'ctrl+shift+q',
            'startup': 'false',
            'theme': 'system'
        },
        'Storage': {
            'max_items': '100'
        }
    }
    
    def __init__(self):
        # 設置配置文件路徑
        self.docs_path = os.path.expanduser('~/Documents')
        self.config_dir = os.path.join(self.docs_path, '.clip-history')
        self.config_file = os.path.join(self.config_dir, 'settings.ini')
        
        # 確保配置目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 初始化配置解析器
        self.config = configparser.ConfigParser()
        
        # 加載或創建配置
        self.load_config()
    
    def load_config(self):
        """加載配置文件，如果不存在則創建默認配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self._ensure_defaults()
        else:
            self._create_default_config()
    
    def _ensure_defaults(self):
        """確保所有默認配置項都存在，但保留現有值"""
        modified = False
        for section, options in self.DEFAULT_CONFIG.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                modified = True
            
            # 只添加缺失的選項，不覆蓋現有值
            for key, default_value in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, default_value)
                    modified = True
                    print(f"Added missing config option: [{section}] {key} = {default_value}")
        
        # 只在有修改時保存
        if modified:
            self.save_config()
            print("Updated config file with new default options")
    
    def _create_default_config(self):
        """創建默認配置文件"""
        for section, options in self.DEFAULT_CONFIG.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)
    
    # 通用獲取和設置方法
    def get(self, section, key, fallback=None):
        """獲取配置值"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """設置配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
    
    # 快捷方法 - 熱鍵
    def get_hotkey(self):
        """獲取快捷鍵設置"""
        return self.get('General', 'hotkey', 'ctrl+shift+q')
    
    def set_hotkey(self, hotkey):
        """設置快捷鍵"""
        self.set('General', 'hotkey', hotkey)
    
    # 快捷方法 - 主題
    def get_theme(self):
        """獲取主題設置"""
        return self.get('General', 'theme', 'system')
    
    def set_theme(self, theme):
        """設置主題"""
        self.set('General', 'theme', theme)
    
    # 快捷方法 - 開機啟動
    def get_startup(self):
        """獲取開機啟動設置"""
        return self.get('General', 'startup', 'false').lower() == 'true'
    
    def set_startup(self, enabled):
        """設置開機啟動"""
        self.set('General', 'startup', str(enabled).lower())
    
    # 快捷方法 - 存儲相關
    def get_storage_path(self):
        """獲取存儲路徑"""
        default_path = os.path.join(self.config_dir, 'storage')
        return self.get('Storage', 'path', default_path)
    
    def set_storage_path(self, path):
        """設置存儲路徑"""
        self.set('Storage', 'path', path)
    
    def get_max_items(self):
        """獲取最大項目數"""
        return int(self.get('Storage', 'max_items', '100'))
    
    def set_max_items(self, count):
        """設置最大項目數"""
        self.set('Storage', 'max_items', str(count))
    
    def upgrade_config(self, new_version):
        """處理配置文件版本升級"""
        current_version = self.get('General', 'version', '1.0')
        if current_version != new_version:
            print(f"Upgrading config from version {current_version} to {new_version}")
            # 在這裡添加版本升級邏輯
            self.set('General', 'version', new_version) 