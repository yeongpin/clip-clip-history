#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Storage Manager Module
Manages the storage and retrieval of clipboard history items.
"""

import os
import json
import sqlite3
import time
from models.clipboard_item import ClipboardItem

class StorageManager:
    def __init__(self, storage_path=None):
        """
        Initialize storage manager
        
        Args:
            storage_path: Path to store database file
        """
        if not storage_path:
            # Default to user's temp directory
            storage_path = os.path.join(os.path.expanduser("~"), ".clipboard_history")
            
        # Create directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)
        
        self.db_path = os.path.join(storage_path, "clipboard_history.db")
        self.max_items = 100  # Default max items to store
        
        # Initialize database
        self._init_db()
        
    def _init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 檢查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clipboard_items'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # 檢查表結構
            cursor.execute("PRAGMA table_info(clipboard_items)")
            columns = [col[1] for col in cursor.fetchall()]
            
            # 如果缺少 content_type 列，則添加它
            if 'content_type' not in columns:
                print("Upgrading database schema: adding content_type column")
                cursor.execute("ALTER TABLE clipboard_items ADD COLUMN content_type TEXT DEFAULT 'text' NOT NULL")
                conn.commit()
        else:
            # 創建新表
            cursor.execute('''
            CREATE TABLE clipboard_items (
                id INTEGER PRIMARY KEY,
                content_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                preview TEXT,
                size INTEGER,
                pinned BOOLEAN DEFAULT 0
            )
            ''')
            conn.commit()
        
        # Create settings table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_item(self, item):
        """
        Add a new clipboard item to storage
        
        Args:
            item: ClipboardItem instance
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all attributes from item.to_dict()
        item_data = item.to_dict()
        
        # Build the SQL query dynamically
        columns = ', '.join(item_data.keys())
        placeholders = ', '.join(['?' for _ in item_data])
        values = tuple(item_data.values())
        
        # Insert new item with all attributes
        cursor.execute(
            f"INSERT INTO clipboard_items ({columns}) VALUES ({placeholders})",
            values
        )
        
        # Enforce maximum items limit
        cursor.execute(
            "DELETE FROM clipboard_items WHERE id NOT IN (SELECT id FROM clipboard_items ORDER BY timestamp DESC LIMIT ?)",
            (self.max_items,)
        )
        
        conn.commit()
        conn.close()
        
    def get_items(self, limit=50, offset=0):
        """
        Get clipboard items from storage
        
        Args:
            limit: Maximum number of items to retrieve
            offset: Offset for pagination
            
        Returns:
            List of ClipboardItem instances
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all columns from the table
        cursor.execute("SELECT * FROM clipboard_items ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        items = []
        for row in cursor.fetchall():
            # Create dictionary with column names as keys
            item_dict = dict(zip(columns, row))
            items.append(ClipboardItem.from_dict(item_dict))
            
        conn.close()
        return items
        
    def delete_item(self, item_id):
        """
        Delete a clipboard item
        
        Args:
            item_id: ID of item to delete
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))
        
        conn.commit()
        conn.close()
        
    def clear_history(self):
        """Clear all clipboard history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM clipboard_items")
        
        conn.commit()
        conn.close()
        
    def get_storage_info(self):
        """
        Get storage usage information
        
        Returns:
            Dictionary with storage statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get item count
        cursor.execute("SELECT COUNT(*) FROM clipboard_items")
        item_count = cursor.fetchone()[0]
        
        # Get total size
        cursor.execute("SELECT SUM(size) FROM clipboard_items WHERE size IS NOT NULL")
        total_size = cursor.fetchone()[0] or 0
        
        # Get type distribution
        cursor.execute("SELECT content_type, COUNT(*) FROM clipboard_items GROUP BY content_type")
        type_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "item_count": item_count,
            "total_size": total_size,
            "type_distribution": type_distribution,
            "db_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        }
        
    def set_max_items(self, max_items):
        """
        Set maximum number of items to store
        
        Args:
            max_items: Maximum number of items
        """
        self.max_items = max_items
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update setting
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            ("max_items", str(max_items))
        )
        
        # Enforce the limit
        cursor.execute(
            "DELETE FROM clipboard_items WHERE id NOT IN (SELECT id FROM clipboard_items ORDER BY timestamp DESC LIMIT ?)",
            (max_items,)
        )
        
        conn.commit()
        conn.close()
        
    def toggle_pin_item(self, item_id, pinned):
        """Toggle pin status of an item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE clipboard_items SET pinned = ? WHERE id = ?",
            (pinned, item_id)
        )
        
        conn.commit()
        conn.close() 
