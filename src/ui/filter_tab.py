from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCalendarWidget, QComboBox, QListWidget, QPushButton,
    QLineEdit
)
from PyQt6.QtCore import Qt, QSize
from datetime import datetime
import time

class FilterTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the filter tab UI"""
        layout = QVBoxLayout(self)
        
        # 上方的快速過濾選項
        filter_layout = QHBoxLayout()
        
        # 添加過濾下拉選單
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Last 30 days",
            "Last 7 days",
            "Today",
            "Custom date"
        ])
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(QLabel("Show items from:"))
        filter_layout.addWidget(self.filter_combo)
        
        # 添加 Today 按鈕
        today_button = QPushButton("Today")
        today_button.setFixedWidth(80)  # 設置固定寬度
        today_button.clicked.connect(self.go_to_today)
        filter_layout.addWidget(today_button)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # 添加搜索欄
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 10)  # 添加一些垂直間距
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords to search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # 清除搜索按鈕
        clear_button = QPushButton("Clear")
        clear_button.setFixedWidth(60)
        clear_button.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(clear_button)
        
        layout.addLayout(search_layout)
        
        # 添加日曆
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)
        
        # 添加過濾後的項目列表
        self.filtered_items_list = QListWidget()
        self.filtered_items_list.setIconSize(QSize(40, 40))
        self.filtered_items_list.setAlternatingRowColors(True)
        self.filtered_items_list.itemDoubleClicked.connect(self.main_window.on_item_double_clicked)
        self.filtered_items_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.filtered_items_list.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.filtered_items_list)
        
        # 初始化顯示最近30天的項目
        self.filter_items(30)
        
    def show_context_menu(self, position):
        """Show context menu at the correct position"""
        # 獲取全局位置
        global_pos = self.filtered_items_list.mapToGlobal(position)
        # 調用主窗口的上下文菜單
        self.main_window.show_context_menu_at_pos(self.filtered_items_list, global_pos)
        
    def on_filter_changed(self, index):
        """Handle filter combo box change"""
        if index == 0:  # Last 30 days
            self.filter_items(30)
        elif index == 1:  # Last 7 days
            self.filter_items(7)
        elif index == 2:  # Today
            self.filter_items(1)
        elif index == 3:  # Custom date
            selected_date = self.calendar.selectedDate()
            self.filter_items_by_date(selected_date.toPyDate())
            
    def on_date_selected(self, date):
        """Handle calendar date selection"""
        self.filter_combo.setCurrentIndex(3)
        self.filter_items_by_date(date.toPyDate())
        
    def on_search_changed(self, text):
        """處理搜索文本變化"""
        # 獲取當前日期過濾條件下的項目
        current_filter = self.filter_combo.currentIndex()
        if current_filter == 0:  # Last 30 days
            self.filter_items(30, search_text=text)
        elif current_filter == 1:  # Last 7 days
            self.filter_items(7, search_text=text)
        elif current_filter == 2:  # Today
            self.filter_items(1, search_text=text)
        elif current_filter == 3:  # Custom date
            selected_date = self.calendar.selectedDate()
            self.filter_items_by_date(selected_date.toPyDate(), search_text=text)
    
    def clear_search(self):
        """清除搜索"""
        self.search_input.clear()
        self.on_search_changed("")
    
    def filter_items(self, days, search_text=""):
        """過濾項目"""
        self.filtered_items_list.clear()
        items = self.main_window.storage.get_items()
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # 先按時間過濾
        filtered_items = [item for item in items if item.timestamp >= cutoff_time]
        
        # 如果有搜索文本，進一步過濾
        if search_text:
            search_text = search_text.lower()
            filtered_items = [
                item for item in filtered_items
                if (item.content_type == "text" and search_text in item.content.lower())
            ]
        
        self.main_window._populate_items_list(self.filtered_items_list, filtered_items)
    
    def filter_items_by_date(self, date, search_text=""):
        """按日期過濾項目"""
        self.filtered_items_list.clear()
        items = self.main_window.storage.get_items()
        
        start_time = datetime.combine(date, datetime.min.time()).timestamp()
        end_time = datetime.combine(date, datetime.max.time()).timestamp()
        
        # 先按日期過濾
        filtered_items = [
            item for item in items 
            if start_time <= item.timestamp <= end_time
        ]
        
        # 如果有搜索文本，進一步過濾
        if search_text:
            search_text = search_text.lower()
            filtered_items = [
                item for item in filtered_items
                if (item.content_type == "text" and search_text in item.content.lower())
            ]
        
        self.main_window._populate_items_list(self.filtered_items_list, filtered_items)
        
    def go_to_today(self):
        """Go to today's date in calendar"""
        today = datetime.today()
        self.calendar.setSelectedDate(today)
        self.filter_combo.setCurrentIndex(3)  # 切換到 Custom date
        self.filter_items_by_date(today.date()) 