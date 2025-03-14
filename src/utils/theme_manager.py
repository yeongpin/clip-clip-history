from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor
import platform
import os
import configparser

class ThemeManager:
    # list of theme color roles - use lowercase
    REQUIRED_COLORS = [
        'window', 'windowtext', 'base', 'alternatebase', 
        'text', 'button', 'buttontext', 'highlight', 'highlightedtext',
        'tooltipbase', 'tooltiptext'
    ]
    
    # default theme colors - use lowercase
    LIGHT_THEME = {
        'window': '240,240,240',
        'windowtext': '0,0,0',
        'base': '255,255,255',
        'alternatebase': '245,245,245',
        'text': '0,0,0',
        'button': '240,240,240',
        'buttontext': '0,0,0',
        'highlight': '42,130,218',
        'highlightedtext': '255,255,255',
        'tooltipbase': '240,240,240',
        'tooltiptext': '0,0,0'
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
        'highlightedtext': '255,255,255',
        'tooltipbase': '53,53,53',
        'tooltiptext': '255,255,255'
    }

    @staticmethod
    def init_themes():
        """initialize theme folder and default theme file"""
        docs_path = os.path.expanduser('~/Documents')
        theme_dir = os.path.join(docs_path, '.clip-history', 'themes')
        os.makedirs(theme_dir, exist_ok=True)

        # save default themes
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
                # check and update existing theme file
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
        """validate and format theme data"""
        if not isinstance(theme_data, dict):
            print(f"Invalid theme data type: {type(theme_data)}")
            return None
            
        formatted_theme = {}
        
        # check if all required color roles are included
        for role in ThemeManager.REQUIRED_COLORS:
            # check color value format
            if role in theme_data:
                color_str = theme_data[role]
                try:
                    # try to parse color value
                    if isinstance(color_str, str):
                        # if string format "r,g,b"
                        color_values = [int(x.strip()) for x in color_str.split(',')]
                        if len(color_values) == 3:
                            r, g, b = color_values
                            if 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255:
                                formatted_theme[role] = f"{r},{g},{b}"
                                continue
                except Exception as e:
                    print(f"Error formatting color for {role}: {e}")
                    
            print(f"Using default value for {role}")
            formatted_theme[role] = ThemeManager.LIGHT_THEME[role]
            
        return formatted_theme

    @staticmethod
    def get_available_themes():
        """get all available themes"""
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
                        # validate and format theme
                        formatted_theme = ThemeManager.validate_and_format_theme(dict(config['Colors']))
                        if formatted_theme:
                            themes[theme_name] = formatted_theme
                            
        return themes

    @staticmethod
    def _str_to_color(color_str):
        """convert color string to QColor"""
        try:
            r, g, b = map(int, color_str.split(','))
            return QColor(r, g, b)
        except:
            return QColor(0, 0, 0)  # default black

    @staticmethod
    def apply_theme(theme_name):
        """apply specified theme"""
        app = QApplication.instance()
        print(f"Applying theme: {theme_name}")

        # set Fusion style
        app.setStyle("Fusion")
        palette = QPalette()

        # get theme colors
        if theme_name.lower() == "system":
            is_dark = ThemeManager.is_system_dark_theme()
            colors = ThemeManager.DARK_THEME if is_dark else ThemeManager.LIGHT_THEME
        else:
            # try to load theme from file
            themes = ThemeManager.get_available_themes()
            theme_name = theme_name.lower()
            
            if theme_name in themes:
                colors = themes[theme_name]
            else:
                # if custom theme not found, check if it's built-in theme
                if theme_name == "dark":
                    print("Using built-in dark theme")
                    colors = ThemeManager.DARK_THEME
                elif theme_name == "light":
                    print("Using built-in light theme")
                    colors = ThemeManager.LIGHT_THEME
                else:
                    print(f"Theme {theme_name} not found, using light theme")
                    colors = ThemeManager.LIGHT_THEME

        # create role name mapping (note: QPalette.ColorRole properties are uppercase)
        role_map = {
            'window': QPalette.ColorRole.Window,
            'windowtext': QPalette.ColorRole.WindowText,
            'base': QPalette.ColorRole.Base,
            'alternatebase': QPalette.ColorRole.AlternateBase,
            'text': QPalette.ColorRole.Text,
            'button': QPalette.ColorRole.Button,
            'buttontext': QPalette.ColorRole.ButtonText,
            'highlight': QPalette.ColorRole.Highlight,
            'highlightedtext': QPalette.ColorRole.HighlightedText,
            'tooltipbase': QPalette.ColorRole.ToolTipBase,
            'tooltiptext': QPalette.ColorRole.ToolTipText
        }

        # Set tooltip colors based on theme
        if 'window' in colors and 'windowtext' in colors:
            # Use window/windowtext colors for tooltips if not explicitly defined
            if 'tooltipbase' not in colors:
                # For tooltip background, use a slightly lighter/darker version of window color
                window_color = ThemeManager._str_to_color(colors['window'])
                is_dark = window_color.lightness() < 128
                
                if is_dark:
                    # For dark themes, make tooltip slightly lighter
                    tooltip_base = QColor(
                        min(window_color.red() + 20, 255),
                        min(window_color.green() + 20, 255),
                        min(window_color.blue() + 20, 255)
                    )
                else:
                    # For light themes, make tooltip slightly darker
                    tooltip_base = QColor(
                        max(window_color.red() - 10, 0),
                        max(window_color.green() - 10, 0),
                        max(window_color.blue() - 10, 0)
                    )
                    
                colors['tooltipbase'] = f"{tooltip_base.red()},{tooltip_base.green()},{tooltip_base.blue()}"
                
            if 'tooltiptext' not in colors:
                # Use windowtext color for tooltip text
                colors['tooltiptext'] = colors['windowtext']

        # apply theme colors
        for role_name, color_str in colors.items():
            role_name = role_name.lower()  # ensure role name is lowercase
            if role_name in role_map:
                color = ThemeManager._str_to_color(color_str)
                palette.setColor(role_map[role_name], color)

        app.setPalette(palette)
        
        # Update any existing tooltips
        ThemeManager.update_tooltips()

    @staticmethod
    def update_tooltips():
        """Update existing tooltips to match current theme"""
        # Find all tooltip instances and update them
        app = QApplication.instance()
        
        # Find all ClipboardTooltip instances
        for widget in app.allWidgets():
            if widget.__class__.__name__ == 'ClipboardTooltip':
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()

    @staticmethod
    def is_system_dark_theme():
        """check if system uses dark theme"""
        system = platform.system()
        
        if system == "Windows":
            # check if system uses dark theme
            import winreg
            try:
                registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return value == 0  # 0 means dark theme
            except Exception as e:
                print(f"Error detecting Windows theme: {e}")
                return False
        else:
            app = QApplication.instance()
            palette = app.style().standardPalette()
            bg_color = palette.color(QPalette.ColorRole.Window)
            return bg_color.lightness() < 128 