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
        
        # Filter options layout
        filter_layout = QHBoxLayout()
        
        # add filter dropdown menu
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
        
        # add Today button
        today_button = QPushButton("Today")
        today_button.setFixedWidth(80)  # set fixed width
        today_button.clicked.connect(self.go_to_today)
        filter_layout.addWidget(today_button)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # add search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 10, 0, 10)  # add some vertical spacing
        
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter keywords to search...")
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # clear search button
        clear_button = QPushButton("Clear")
        clear_button.setFixedWidth(60)
        clear_button.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(clear_button)
        
        layout.addLayout(search_layout)
        
        # add calendar
        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_date_selected)
        layout.addWidget(self.calendar)
        
        # add filtered items list
        self.filtered_items_list = QListWidget()
        self.filtered_items_list.setIconSize(QSize(40, 40))
        self.filtered_items_list.setAlternatingRowColors(True)
        self.filtered_items_list.itemDoubleClicked.connect(self.main_window.on_item_double_clicked)
        self.filtered_items_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.filtered_items_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Connect hover events for tooltips
        self.filtered_items_list.setMouseTracking(True)
        self.filtered_items_list.itemEntered.connect(
            lambda item: self.main_window.tooltip_manager.handle_hover(self.filtered_items_list, item)
        )
        self.filtered_items_list.viewportEntered.connect(
            self.main_window.tooltip_manager.hide_tooltip
        )
        
        # Override leaveEvent to hide tooltip
        original_leave_event = self.filtered_items_list.leaveEvent
        def custom_leave_event(event):
            self.main_window.tooltip_manager.hide_tooltip()
            if original_leave_event:
                original_leave_event(event)
        self.filtered_items_list.leaveEvent = custom_leave_event
        
        layout.addWidget(self.filtered_items_list)
        
        # initialize display recent 30 days items
        self.filter_items(30)
        
    def show_context_menu(self, position):
        """Show context menu at the correct position"""
        # get global position
        global_pos = self.filtered_items_list.mapToGlobal(position)
        # call main window's context menu
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
        """Handle search text change"""
        # get current date filter condition items
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
        """Clear search"""
        self.search_input.clear()
        self.on_search_changed("")
    
    def filter_items(self, days, search_text=""):
        """Filter items"""
        self.filtered_items_list.clear()
        items = self.main_window.storage.get_items()
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        # filter by time first
        filtered_items = [item for item in items if item.timestamp >= cutoff_time]
        
        # if there is search text, further filter
        if search_text:
            search_text = search_text.lower()
            filtered_items = [
                item for item in filtered_items
                if (item.content_type == "text" and search_text in item.content.lower())
            ]
        
        self.main_window._populate_items_list(self.filtered_items_list, filtered_items)
    
    def filter_items_by_date(self, date, search_text=""):
        """Filter items by date"""
        self.filtered_items_list.clear()
        items = self.main_window.storage.get_items()
        
        start_time = datetime.combine(date, datetime.min.time()).timestamp()
        end_time = datetime.combine(date, datetime.max.time()).timestamp()
        
        # filter by date first
        filtered_items = [
            item for item in items 
            if start_time <= item.timestamp <= end_time
        ]
        
        # if there is search text, further filter
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
        self.filter_combo.setCurrentIndex(3)  # switch to Custom date
        self.filter_items_by_date(today.date()) 