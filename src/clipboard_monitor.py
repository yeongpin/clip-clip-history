#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clipboard Monitor Module
Monitors system clipboard for changes and saves new content to storage.
"""

import os
import time
import tempfile
from PyQt6.QtCore import QObject, QMimeData, QByteArray, QBuffer, QIODevice, QUrl
from PyQt6.QtGui import QClipboard, QImage, QAction, QShortcut
from models.clipboard_item import ClipboardItem

class ClipboardMonitor(QObject):
    def __init__(self, clipboard, storage_manager):
        """
        Initialize clipboard monitor
        
        Args:
            clipboard: QClipboard instance
            storage_manager: StorageManager instance
        """
        super().__init__()
        self.clipboard = clipboard
        self.storage = storage_manager
        self.last_content_hash = None
        self.item_added_signal = None  # set in main.py
        self.ignore_next_change = False  # new flag
        
    def start(self):
        """Start monitoring clipboard changes"""
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        
    def stop(self):
        """Stop monitoring clipboard changes"""
        self.clipboard.dataChanged.disconnect(self.on_clipboard_change)
        
    def on_clipboard_change(self):
        """Handle clipboard content change"""
        # if copied from within the app, ignore this change
        if self.ignore_next_change:
            self.ignore_next_change = False
            return
            
        print("Clipboard changed")
        mime_data = self.clipboard.mimeData()
        
        if not mime_data:
            print("No mime data")
            return
            
        # only process text content
        if mime_data.hasText():
            print("Processing text")
            self._process_text(mime_data)
        else:
            print("Skipping non-text content")
        
        # emit signal to notify main window to update list
        if hasattr(self, 'item_added_signal') and self.item_added_signal is not None:
            print("Emitting item_added_signal")
            self.item_added_signal.emit()
        else:
            print("No item_added_signal available")
    
    def _process_text(self, mime_data):
        """Process text content"""
        text = mime_data.text()
        if not text or text.isspace():
            return
            
        # Avoid duplicates
        content_hash = hash(text)
        if content_hash == self.last_content_hash:
            return
            
        self.last_content_hash = content_hash
        
        # create plain text clipboard item
        item = ClipboardItem(
            content_type="text",
            content=text,
            timestamp=time.time(),
            preview=text[:100] if len(text) > 100 else text,
            size=len(text.encode('utf-8'))  # 計算文本的字節大小
        )
        
        # Save to storage
        self.storage.add_item(item)
        
        # emit signal to notify main window to update list
        if self.item_added_signal is not None:
            self.item_added_signal.emit()
    
    def _process_image(self, mime_data):
        """Process image content"""
        image = mime_data.imageData()
        if not image:
            return
            
        # Save image to temp file
        temp_path = os.path.join(tempfile.gettempdir(), f"clipboard_img_{int(time.time())}.png")
        image.save(temp_path, "PNG")
        
        # Create thumbnail
        thumbnail = image.scaled(100, 100)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        thumbnail.save(buffer, "PNG")
        thumbnail_data = buffer.data().data()
        
        # Create clipboard item
        item = ClipboardItem(
            content_type="image",
            content=temp_path,
            timestamp=time.time(),
            preview=thumbnail_data,
            size=os.path.getsize(temp_path)
        )
        
        # Save to storage
        self.storage.add_item(item)
    
    def _process_urls(self, mime_data):
        """Process URL content"""
        urls = mime_data.urls()
        if not urls:
            return
        
        for url in urls:
            url_string = url.toString()
            
            # check if it's a local file
            if url.isLocalFile():
                # get local file path
                file_path = url.toLocalFile()
                print(f"Processing local file: {file_path}")
                
                # check file type
                if os.path.isfile(file_path):
                    # get file size
                    size = os.path.getsize(file_path)
                    
                    # create clipboard item
                    item = ClipboardItem(
                        content_type="file",
                        content=file_path,  # store original file path, not URL
                        timestamp=time.time(),
                        preview=os.path.basename(file_path),
                        size=size
                    )
                    
                    # save to storage
                    self.storage.add_item(item)
            else:
                # process network URL
                print(f"Processing URL: {url_string}")
                
                # create clipboard item
                item = ClipboardItem(
                    content_type="url",
                    content=url_string,
                    timestamp=time.time(),
                    preview=url_string
                )
                
                # save to storage
                self.storage.add_item(item)
    
    def _process_other_formats(self, mime_data):
        """Process other MIME formats"""
        formats = mime_data.formats()
        
        # Try to identify video or other binary data
        for format_name in formats:
            if "video" in format_name.lower():
                data = mime_data.data(format_name)
                if data:
                    # Save to temp file
                    temp_path = os.path.join(tempfile.gettempdir(), f"clipboard_video_{int(time.time())}.mp4")
                    with open(temp_path, 'wb') as f:
                        f.write(data.data())
                    
                    # Create clipboard item
                    item = ClipboardItem(
                        content_type="video",
                        content=temp_path,
                        timestamp=time.time(),
                        preview="Video clip",
                        size=os.path.getsize(temp_path)
                    )
                    
                    # Save to storage
                    self.storage.add_item(item)
                    break 
