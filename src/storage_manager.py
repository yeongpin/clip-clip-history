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
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS clipboard_items (
            id INTEGER PRIMARY KEY,
            content_type TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL,
            preview TEXT,
            size INTEGER
        )
        ''')
        
        # Create settings table
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
        
        # Insert new item
        cursor.execute(
            "INSERT INTO clipboard_items (id, content_type, content, timestamp, preview, size) VALUES (?, ?, ?, ?, ?, ?)",
            (item.id, item.content_type, item.content, item.timestamp, item.preview, item.size)
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
        
        cursor.execute(
            "SELECT id, content_type, content, timestamp, preview, size FROM clipboard_items ORDER BY timestamp DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        
        items = []
        for row in cursor.fetchall():
            item_dict = {
                "id": row[0],
                "content_type": row[1],
                "content": row[2],
                "timestamp": row[3],
                "preview": row[4],
                "size": row[5]
            }
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
