#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clipboard Item Model
Represents a single clipboard history item.
"""

import time
import json
import os

class ClipboardItem:
    def __init__(self, content_type, content, timestamp=None, preview=None, size=None, pinned=False):
        """
        Initialize a clipboard item
        
        Args:
            content_type: Type of content ("text", "image", "file", "url", "video")
            content: The actual content or path to content
            timestamp: Time when item was copied
            preview: Preview text or thumbnail data
            size: Size of content in bytes (for non-text items)
            pinned: Whether the item is pinned
        """
        self.id = int(time.time() * 1000)  # Unique ID based on timestamp
        self.content_type = content_type
        self.content = content
        self.timestamp = timestamp or time.time()
        self.preview = preview
        self.size = size
        self.pinned = pinned
        
    def to_dict(self):
        """Convert item to dictionary for storage"""
        return {
            "id": self.id,
            "content_type": self.content_type,
            "content": self.content,
            "timestamp": self.timestamp,
            "preview": self.preview,
            "size": self.size,
            "pinned": self.pinned
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create item from dictionary"""
        item = cls(
            content_type=data["content_type"],
            content=data["content"],
            timestamp=data["timestamp"],
            preview=data["preview"],
            size=data.get("size"),
            pinned=data.get("pinned", False)
        )
        item.id = data["id"]
        return item
        
    def get_formatted_time(self):
        """Get formatted timestamp string"""
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp))
        
    def get_formatted_size(self):
        """Get formatted size string"""
        if self.size is None:
            return "N/A"
            
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.1f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.1f} GB"

    def get_display_text(self, max_length=50):
        """Get display text for the item"""
        if self.content_type == "text":
            # For text, show the first line or truncated text
            text = self.content.split('\n')[0] if '\n' in self.content else self.content
            
            # check if it is a file URL format
            if text.startswith("file:///"):
                file_path = text.replace("file:///", "")
                return os.path.basename(file_path)
            
            if len(text) > max_length:
                text = text[:max_length] + "..."
            return text
        elif self.content_type == "file":
            # for file, only show file name
            file_path = self.content
            if file_path.startswith("file:///"):
                file_path = file_path.replace("file:///", "")
            elif file_path.startswith("file://"):
                file_path = file_path.replace("file://", "")
            return os.path.basename(file_path)
        elif self.content_type == "url":
            # for URL, show a short version
            url = self.content
            if len(url) > max_length:
                url = url[:max_length-3] + "..."
            return url
        elif self.content_type == "image":
            return "Image"
        elif self.content_type == "video":
            return "Video"
        else:
            return f"{self.content_type.capitalize()}: {self.preview}" 
