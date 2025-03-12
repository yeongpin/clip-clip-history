from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
import platform
import winreg
import os
import configparser

class ThemeManager:
    # 主題顏色角色列表 - 使用小寫
    REQUIRED_COLORS = [
        'window', 'windowtext', 'base', 'alternatebase', 
        'text', 'button', 'buttontext', 'highlight', 'highlightedtext'
    ]
    
    # 默認主題顏色 - 使用小寫
    LIGHT_THEME = {
        'window': '240,240,240',
        'windowtext': '0,0,0',
        'base': '255,255,255',
        'alternatebase': '245,245,245',
        'text': '0,0,0',
        'button': '240,240,240',
        'buttontext': '0,0,0',
        'highlight': '42,130,218',
        'highlightedtext': '255,255,255'
    }
    
    DARK_THEME = {
        'window': '53,53,53',
        'windowtext': '255,255,255',
        'base': '35,35,35',
        'alternatebase': '45,45,45',
        'text': '255,255,255',
        'button': '53,53,53',
        'buttontext': '255,255,255',
        'highlight': '42,130,218',
        'highlightedtext': '255,255,255'
    }

    @staticmethod
    def init_themes():
        """初始化主題文件夾和默認主題文件"""
        docs_path = os.path.expanduser('~/Documents')
        theme_dir = os.path.join(docs_path, '.clip-history', 'themes')
        os.makedirs(theme_dir, exist_ok=True)

        # 保存默認主題
        themes = {
            'light': ThemeManager.LIGHT_THEME,
            'dark': ThemeManager.DARK_THEME
        }
        
        for theme_name, colors in themes.items():
            theme_file = os.path.join(theme_dir, f'{theme_name}.ini')
            if not os.path.exists(theme_file):
                config = configparser.ConfigParser()
                config['Colors'] = colors
                with open(theme_file, 'w') as f:
                    config.write(f)
            else:
                # 檢查並更新現有主題文件
                config = configparser.ConfigParser()
                config.read(theme_file)
                if 'Colors' not in config:
                    config['Colors'] = {}
                modified = False
                for key, value in colors.items():
                    if key not in config['Colors']:
                        config['Colors'][key] = value
                        modified = True
                if modified:
                    with open(theme_file, 'w') as f:
                        config.write(f)

    @staticmethod
    def validate_and_format_theme(theme_data):
        """驗證並格式化主題數據"""
        if not isinstance(theme_data, dict):
            print(f"Invalid theme data type: {type(theme_data)}")
            return None
            
        formatted_theme = {}
        print(f"Formatting theme data: {theme_data}")
        
        # 檢查是否包含所有必需的顏色角色
        for role in ThemeManager.REQUIRED_COLORS:
            # 檢查顏色值格式
            if role in theme_data:
                color_str = theme_data[role]
                try:
                    # 嘗試解析顏色值
                    if isinstance(color_str, str):
                        # 如果是字符串格式 "r,g,b"
                        color_values = [int(x.strip()) for x in color_str.split(',')]
                        if len(color_values) == 3:
                            r, g, b = color_values
                            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                                formatted_theme[role] = f"{r},{g},{b}"
                                print(f"Formatted {role}: {formatted_theme[role]}")
                                continue
                except Exception as e:
                    print(f"Error formatting color for {role}: {e}")
                    
            print(f"Using default value for {role}")
            formatted_theme[role] = ThemeManager.LIGHT_THEME[role]
            
        return formatted_theme

    @staticmethod
    def get_available_themes():
        """獲取所有可用的主題"""
        theme_dir = os.path.join(os.path.expanduser('~/Documents'), '.clip-history', 'themes')
        themes = {}
        if os.path.exists(theme_dir):
            for file in os.listdir(theme_dir):
                if file.endswith('.ini'):
                    theme_name = os.path.splitext(file)[0]
                    theme_path = os.path.join(theme_dir, file)
                    config = configparser.ConfigParser()
                    config.read(theme_path)
                    
                    if 'Colors' in config:
                        # 驗證並格式化主題
                        formatted_theme = ThemeManager.validate_and_format_theme(dict(config['Colors']))
                        if formatted_theme:
                            themes[theme_name] = formatted_theme
                            
        return themes

    @staticmethod
    def _str_to_color(color_str):
        """將顏色字符串轉換為 QColor"""
        try:
            r, g, b = map(int, color_str.split(','))
            return QColor(r, g, b)
        except:
            return QColor(0, 0, 0)  # 默認黑色

    @staticmethod
    def apply_theme(theme_name):
        """應用指定的主題"""
        app = QApplication.instance()
        print(f"Applying theme: {theme_name}")

        # 設置 Fusion 風格
        app.setStyle("Fusion")
        palette = QPalette()

        # 獲取主題顏色
        if theme_name.lower() == "system":
            is_dark = ThemeManager.is_system_dark_theme()
            print(f"System theme detected as: {'dark' if is_dark else 'light'}")
            colors = ThemeManager.DARK_THEME if is_dark else ThemeManager.LIGHT_THEME
        else:
            # 嘗試從文件加載主題
            themes = ThemeManager.get_available_themes()
            theme_name = theme_name.lower()
            print(f"Available themes: {list(themes.keys())}")
            
            if theme_name in themes:
                print(f"Using custom theme: {theme_name}")
                colors = themes[theme_name]
            else:
                # 如果找不到自定義主題，檢查是否是內置主題
                if theme_name == "dark":
                    print("Using built-in dark theme")
                    colors = ThemeManager.DARK_THEME
                elif theme_name == "light":
                    print("Using built-in light theme")
                    colors = ThemeManager.LIGHT_THEME
                else:
                    print(f"Theme {theme_name} not found, using light theme")
                    colors = ThemeManager.LIGHT_THEME

        print(f"Applying colors: {colors}")

        # 創建角色名稱映射（注意：QPalette.ColorRole 的屬性是大寫的）
        role_map = {
            'window': QPalette.ColorRole.Window,
            'windowtext': QPalette.ColorRole.WindowText,
            'base': QPalette.ColorRole.Base,
            'alternatebase': QPalette.ColorRole.AlternateBase,
            'text': QPalette.ColorRole.Text,
            'button': QPalette.ColorRole.Button,
            'buttontext': QPalette.ColorRole.ButtonText,
            'highlight': QPalette.ColorRole.Highlight,
            'highlightedtext': QPalette.ColorRole.HighlightedText
        }

        # 應用主題顏色
        for role_name, color_str in colors.items():
            role_name = role_name.lower()  # 確保角色名稱是小寫的
            if role_name in role_map:
                color = ThemeManager._str_to_color(color_str)
                print(f"Setting {role_name} to {color_str}")
                palette.setColor(role_map[role_name], color)

        app.setPalette(palette)

    @staticmethod
    def is_system_dark_theme():
        """檢查系統是否使用深色主題"""
        system = platform.system()
        
        if system == "Windows":
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0  # 0 表示深色主題
            except Exception as e:
                print(f"Error detecting Windows theme: {e}")
                return False
        else:
            app = QApplication.instance()
            palette = app.style().standardPalette()
            bg_color = palette.color(QPalette.ColorRole.Window)
            return bg_color.lightness() < 128 