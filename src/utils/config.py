import os
import configparser
from pathlib import Path

class Config:
    def __init__(self):
        # 獲取用戶文檔目錄
        self.docs_path = os.path.expanduser('~/Documents')
        self.config_dir = os.path.join(self.docs_path, '.clip-history')
        self.config_file = os.path.join(self.config_dir, 'config.ini')
        
        # 確保配置目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 默認配置
        self.defaults = {
            'General': {
                'hotkey': 'ctrl+shift+q',
                'startup': 'false',
                'theme': 'system'
            },
            'Storage': {
                'path': os.path.join(self.config_dir, 'storage'),
                'max_items': '100'
            }
        }
        
        # 加載配置
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """加載配置文件，如果不存在則創建默認配置"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            # 使用默認配置
            self.config.read_dict(self.defaults)
            self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)
    
    def get(self, section, key, fallback=None):
        """獲取配置值"""
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        """設置配置值"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        self.save_config()
    
    # 快捷方法
    def get_hotkey(self):
        """獲取快捷鍵設置"""
        return self.get('General', 'hotkey', 'ctrl+shift+q')
    
    def set_hotkey(self, hotkey):
        """設置快捷鍵"""
        self.set('General', 'hotkey', hotkey) 