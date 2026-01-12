# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import sqlite3
import json
from typing import Dict, Optional, Any, List

from src.storage.base.base_store import BaseStore, BaseStoreImage, BaseStoreVideo


class SQLiteStore(BaseStore):
    """SQLite store implementation"""
    
    def __init__(self, db_path: str = "./supercrawler.db"):
        super().__init__()
        self.db_path = db_path
        self.conn = None
    
    async def initialize(self):
        """Initialize SQLite store"""
        await super().initialize()
        # Connect to SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables if they don't exist
        cursor = self.conn.cursor()
        
        # Create content table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            author TEXT,
            platform TEXT,
            created_at TEXT,
            url TEXT,
            metadata TEXT
        )
        ''')
        
        # Create comments table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            content_id TEXT,
            author TEXT,
            content TEXT,
            created_at TEXT,
            metadata TEXT,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        # Create creators table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS creators (
            id TEXT PRIMARY KEY,
            name TEXT,
            username TEXT,
            platform TEXT,
            followers INTEGER,
            following INTEGER,
            metadata TEXT
        )
        ''')
        
        self.conn.commit()
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item to SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        metadata = json.dumps(content_item.get('metadata', {}))
        
        cursor.execute('''
        INSERT OR REPLACE INTO content (id, title, content, author, platform, created_at, url, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_item.get('id'),
            content_item.get('title'),
            content_item.get('content'),
            content_item.get('author'),
            content_item.get('platform'),
            content_item.get('created_at'),
            content_item.get('url'),
            metadata
        ))
        
        self.conn.commit()
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item to SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        metadata = json.dumps(comment_item.get('metadata', {}))
        
        cursor.execute('''
        INSERT OR REPLACE INTO comments (id, content_id, author, content, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            comment_item.get('id'),
            comment_item.get('content_id'),
            comment_item.get('author'),
            comment_item.get('content'),
            comment_item.get('created_at'),
            metadata
        ))
        
        self.conn.commit()
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information to SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        metadata = json.dumps(creator.get('metadata', {}))
        
        cursor.execute('''
        INSERT OR REPLACE INTO creators (id, name, username, platform, followers, following, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            creator.get('id'),
            creator.get('name'),
            creator.get('username'),
            creator.get('platform'),
            creator.get('followers', 0),
            creator.get('following', 0),
            metadata
        ))
        
        self.conn.commit()
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
            return result
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM comments WHERE content_id = ?', (content_id,))
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            comment = dict(row)
            comment['metadata'] = json.loads(comment['metadata']) if comment['metadata'] else {}
            result.append(comment)
        return result
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM creators WHERE id = ?', (creator_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
            return result
        return None
    
    async def close(self):
        """Close SQLite store"""
        if self.conn:
            self.conn.close()
            self.conn = None
        await super().close()


class SQLiteStoreImage(BaseStoreImage):
    """SQLite store image implementation"""
    
    def __init__(self, db_path: str = "./supercrawler.db"):
        super().__init__()
        self.db_path = db_path
        self.conn = None
    
    async def initialize(self):
        """Initialize SQLite store image"""
        await super().initialize()
        # Connect to SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create images table if it doesn't exist
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            content_id TEXT,
            url TEXT,
            local_path TEXT,
            width INTEGER,
            height INTEGER,
            metadata TEXT,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        self.conn.commit()
    
    async def store_image(self, image_content_item: Dict[str, Any]):
        """Store image content to SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        metadata = json.dumps(image_content_item.get('metadata', {}))
        
        cursor.execute('''
        INSERT OR REPLACE INTO images (id, content_id, url, local_path, width, height, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_content_item.get('id'),
            image_content_item.get('content_id'),
            image_content_item.get('url'),
            image_content_item.get('local_path'),
            image_content_item.get('width'),
            image_content_item.get('height'),
            metadata
        ))
        
        self.conn.commit()
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID from SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM images WHERE id = ?', (image_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
            return result
        return None
    
    async def close(self):
        """Close SQLite store image"""
        if self.conn:
            self.conn.close()
            self.conn = None
        await super().close()


class SQLiteStoreVideo(BaseStoreVideo):
    """SQLite store video implementation"""
    
    def __init__(self, db_path: str = "./supercrawler.db"):
        super().__init__()
        self.db_path = db_path
        self.conn = None
    
    async def initialize(self):
        """Initialize SQLite store video"""
        await super().initialize()
        # Connect to SQLite database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Create videos table if it doesn't exist
        cursor = self.conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            content_id TEXT,
            url TEXT,
            local_path TEXT,
            duration INTEGER,
            metadata TEXT,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        self.conn.commit()
    
    async def store_video(self, video_content_item: Dict[str, Any]):
        """Store video content to SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        metadata = json.dumps(video_content_item.get('metadata', {}))
        
        cursor.execute('''
        INSERT OR REPLACE INTO videos (id, content_id, url, local_path, duration, metadata)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            video_content_item.get('id'),
            video_content_item.get('content_id'),
            video_content_item.get('url'),
            video_content_item.get('local_path'),
            video_content_item.get('duration'),
            metadata
        ))
        
        self.conn.commit()
    
    async def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID from SQLite"""
        if not self.connected:
            await self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM videos WHERE id = ?', (video_id,))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            result['metadata'] = json.loads(result['metadata']) if result['metadata'] else {}
            return result
        return None
    
    async def close(self):
        """Close SQLite store video"""
        if self.conn:
            self.conn.close()
            self.conn = None
        await super().close()