# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import os
import json
import csv
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

from base.base_crawler import AbstractStore, AbstractStoreImage, AbstractStoreVideo


class StoreFactory:
    """Store factory for creating storage instances"""
    
    @staticmethod
    def create_store(store_type: str, platform: str) -> AbstractStore:
        """Create a store instance for the specified type"""
        if store_type == "json":
            return JSONStore(platform)
        elif store_type == "csv":
            return CSVStore(platform)
        elif store_type == "excel":
            return ExcelStore(platform)
        elif store_type == "sqlite":
            return SQLiteStore(platform)
        elif store_type == "db":
            return DatabaseStore(platform)
        elif store_type == "mongodb":
            return MongoDBStore(platform)
        else:
            raise ValueError(f"Invalid store type: {store_type}")


class BaseStore(AbstractStore):
    """Base store implementation"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", platform)
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item"""
        pass
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item"""
        pass
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information"""
        pass
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID"""
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID"""
        return []
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID"""
        return None
    
    async def close(self):
        """Close storage connection"""
        pass


class JSONStore(BaseStore):
    """JSON store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.content_file = os.path.join(self.data_dir, "content.json")
        self.comments_file = os.path.join(self.data_dir, "comments.json")
        self.creators_file = os.path.join(self.data_dir, "creators.json")
        
        # Initialize files if they don't exist
        for file_path in [self.content_file, self.comments_file, self.creators_file]:
            if not os.path.exists(file_path):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in JSON file"""
        with open(self.content_file, "r", encoding="utf-8") as f:
            content_list = json.load(f)
        
        content_list.append(content_item)
        
        with open(self.content_file, "w", encoding="utf-8") as f:
            json.dump(content_list, f, ensure_ascii=False, indent=2)
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in JSON file"""
        with open(self.comments_file, "r", encoding="utf-8") as f:
            comments_list = json.load(f)
        
        comments_list.append(comment_item)
        
        with open(self.comments_file, "w", encoding="utf-8") as f:
            json.dump(comments_list, f, ensure_ascii=False, indent=2)
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in JSON file"""
        with open(self.creators_file, "r", encoding="utf-8") as f:
            creators_list = json.load(f)
        
        creators_list.append(creator)
        
        with open(self.creators_file, "w", encoding="utf-8") as f:
            json.dump(creators_list, f, ensure_ascii=False, indent=2)
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from JSON file"""
        with open(self.content_file, "r", encoding="utf-8") as f:
            content_list = json.load(f)
        
        for content in content_list:
            if content.get("id") == content_id:
                return content
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from JSON file"""
        with open(self.comments_file, "r", encoding="utf-8") as f:
            comments_list = json.load(f)
        
        return [comment for comment in comments_list if comment.get("content_id") == content_id]
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from JSON file"""
        with open(self.creators_file, "r", encoding="utf-8") as f:
            creators_list = json.load(f)
        
        for creator in creators_list:
            if creator.get("id") == creator_id:
                return creator
        return None


class CSVStore(BaseStore):
    """CSV store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.content_file = os.path.join(self.data_dir, "content.csv")
        self.comments_file = os.path.join(self.data_dir, "comments.csv")
        self.creators_file = os.path.join(self.data_dir, "creators.csv")
        
        # Initialize CSV files with headers
        self._init_csv_file(self.content_file, ["id", "title", "author", "platform", "created_at", "content", "url", "likes", "comments", "shares", "tags"])
        self._init_csv_file(self.comments_file, ["id", "content_id", "author", "content", "created_at", "likes"])
        self._init_csv_file(self.creators_file, ["id", "name", "username", "bio", "followers", "following", "posts", "avatar", "url"])
    
    def _init_csv_file(self, file_path: str, headers: List[str]):
        """Initialize CSV file with headers"""
        if not os.path.exists(file_path):
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in CSV file"""
        with open(self.content_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                content_item.get("id", ""),
                content_item.get("title", ""),
                content_item.get("author", ""),
                content_item.get("platform", ""),
                content_item.get("created_at", ""),
                content_item.get("content", ""),
                content_item.get("url", ""),
                content_item.get("likes", 0),
                content_item.get("comments", 0),
                content_item.get("shares", 0),
                ",".join(content_item.get("tags", []))
            ])
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in CSV file"""
        with open(self.comments_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                comment_item.get("id", ""),
                comment_item.get("content_id", ""),
                comment_item.get("author", ""),
                comment_item.get("content", ""),
                comment_item.get("created_at", ""),
                comment_item.get("likes", 0)
            ])
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in CSV file"""
        with open(self.creators_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                creator.get("id", ""),
                creator.get("name", ""),
                creator.get("username", ""),
                creator.get("bio", ""),
                creator.get("followers", 0),
                creator.get("following", 0),
                creator.get("posts", 0),
                creator.get("avatar", ""),
                creator.get("url", "")
            ])


class ExcelStore(BaseStore):
    """Excel store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.excel_file = os.path.join(self.data_dir, "data.xlsx")
        self.workbook = None
        self.sheets = {}
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in Excel file"""
        # Excel implementation would use openpyxl or similar
        print(f"Storing content to Excel: {content_item.get('title', 'Untitled')}")
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in Excel file"""
        print(f"Storing comment to Excel: {comment_item.get('content', '')[:50]}...")
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in Excel file"""
        print(f"Storing creator to Excel: {creator.get('name', 'Unknown')}")
    
    @classmethod
    async def flush_all(cls):
        """Flush all Excel data"""
        print("Flushing Excel data...")


class SQLiteStore(BaseStore):
    """SQLite store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.db_file = os.path.join(self.data_dir, "data.db")
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database"""
        import sqlite3
        self.conn = sqlite3.connect(self.db_file)
        cursor = self.conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS content (
            id TEXT PRIMARY KEY,
            title TEXT,
            author TEXT,
            platform TEXT,
            created_at TEXT,
            content TEXT,
            url TEXT,
            likes INTEGER,
            comments INTEGER,
            shares INTEGER,
            tags TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            content_id TEXT,
            author TEXT,
            content TEXT,
            created_at TEXT,
            likes INTEGER,
            FOREIGN KEY (content_id) REFERENCES content (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS creators (
            id TEXT PRIMARY KEY,
            name TEXT,
            username TEXT,
            bio TEXT,
            followers INTEGER,
            following INTEGER,
            posts INTEGER,
            avatar TEXT,
            url TEXT
        )
        ''')
        
        self.conn.commit()
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO content (id, title, author, platform, created_at, content, url, likes, comments, shares, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_item.get("id", ""),
            content_item.get("title", ""),
            content_item.get("author", ""),
            content_item.get("platform", ""),
            content_item.get("created_at", ""),
            content_item.get("content", ""),
            content_item.get("url", ""),
            content_item.get("likes", 0),
            content_item.get("comments", 0),
            content_item.get("shares", 0),
            ",".join(content_item.get("tags", []))
        ))
        self.conn.commit()
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO comments (id, content_id, author, content, created_at, likes)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            comment_item.get("id", ""),
            comment_item.get("content_id", ""),
            comment_item.get("author", ""),
            comment_item.get("content", ""),
            comment_item.get("created_at", ""),
            comment_item.get("likes", 0)
        ))
        self.conn.commit()
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO creators (id, name, username, bio, followers, following, posts, avatar, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            creator.get("id", ""),
            creator.get("name", ""),
            creator.get("username", ""),
            creator.get("bio", ""),
            creator.get("followers", 0),
            creator.get("following", 0),
            creator.get("posts", 0),
            creator.get("avatar", ""),
            creator.get("url", "")
        ))
        self.conn.commit()
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "author": row[2],
                "platform": row[3],
                "created_at": row[4],
                "content": row[5],
                "url": row[6],
                "likes": row[7],
                "comments": row[8],
                "shares": row[9],
                "tags": row[10].split(",") if row[10] else []
            }
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM comments WHERE content_id = ?', (content_id,))
        rows = cursor.fetchall()
        return [
            {
                "id": row[0],
                "content_id": row[1],
                "author": row[2],
                "content": row[3],
                "created_at": row[4],
                "likes": row[5]
            }
            for row in rows
        ]
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from SQLite database"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM creators WHERE id = ?', (creator_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "bio": row[3],
                "followers": row[4],
                "following": row[5],
                "posts": row[6],
                "avatar": row[7],
                "url": row[8]
            }
        return None
    
    async def close(self):
        """Close SQLite connection"""
        if self.conn:
            self.conn.close()


class DatabaseStore(BaseStore):
    """Database store implementation (MySQL/PostgreSQL)"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.db_config = {
            "host": "localhost",
            "port": 3306,
            "user": "root",
            "password": "",
            "database": "supercrawler"
        }
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database connection"""
        try:
            import mysql.connector
            self.conn = mysql.connector.connect(**self.db_config)
            cursor = self.conn.cursor()
            
            # Create tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(255),
                author VARCHAR(255),
                platform VARCHAR(50),
                created_at DATETIME,
                content TEXT,
                url VARCHAR(255),
                likes INT,
                comments INT,
                shares INT,
                tags VARCHAR(255)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                id VARCHAR(255) PRIMARY KEY,
                content_id VARCHAR(255),
                author VARCHAR(255),
                content TEXT,
                created_at DATETIME,
                likes INT,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS creators (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                username VARCHAR(255),
                bio TEXT,
                followers INT,
                following INT,
                posts INT,
                avatar VARCHAR(255),
                url VARCHAR(255)
            )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in database"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO content (id, title, author, platform, created_at, content, url, likes, comments, shares, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                author = VALUES(author),
                platform = VALUES(platform),
                created_at = VALUES(created_at),
                content = VALUES(content),
                url = VALUES(url),
                likes = VALUES(likes),
                comments = VALUES(comments),
                shares = VALUES(shares),
                tags = VALUES(tags)
            ''', (
                content_item.get("id", ""),
                content_item.get("title", ""),
                content_item.get("author", ""),
                content_item.get("platform", ""),
                content_item.get("created_at", None),
                content_item.get("content", ""),
                content_item.get("url", ""),
                content_item.get("likes", 0),
                content_item.get("comments", 0),
                content_item.get("shares", 0),
                ",".join(content_item.get("tags", []))
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error storing content: {e}")
            self.conn.rollback()
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in database"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO comments (id, content_id, author, content, created_at, likes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                content_id = VALUES(content_id),
                author = VALUES(author),
                content = VALUES(content),
                created_at = VALUES(created_at),
                likes = VALUES(likes)
            ''', (
                comment_item.get("id", ""),
                comment_item.get("content_id", ""),
                comment_item.get("author", ""),
                comment_item.get("content", ""),
                comment_item.get("created_at", None),
                comment_item.get("likes", 0)
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error storing comment: {e}")
            self.conn.rollback()
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in database"""
        if not self.conn:
            return
        
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO creators (id, name, username, bio, followers, following, posts, avatar, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                name = VALUES(name),
                username = VALUES(username),
                bio = VALUES(bio),
                followers = VALUES(followers),
                following = VALUES(following),
                posts = VALUES(posts),
                avatar = VALUES(avatar),
                url = VALUES(url)
            ''', (
                creator.get("id", ""),
                creator.get("name", ""),
                creator.get("username", ""),
                creator.get("bio", ""),
                creator.get("followers", 0),
                creator.get("following", 0),
                creator.get("posts", 0),
                creator.get("avatar", ""),
                creator.get("url", "")
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Error storing creator: {e}")
            self.conn.rollback()
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


class MongoDBStore(BaseStore):
    """MongoDB store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.mongo_uri = "mongodb://localhost:27017"
        self.db_name = "supercrawler"
        self.client = None
        self.db = None
        self._init_db()
    
    def _init_db(self):
        """Initialize MongoDB connection"""
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            
            # Create indexes
            self.db.content.create_index("id", unique=True)
            self.db.comments.create_index("id", unique=True)
            self.db.comments.create_index("content_id")
            self.db.creators.create_index("id", unique=True)
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item in MongoDB"""
        if not self.db:
            return
        
        try:
            self.db.content.update_one(
                {"id": content_item.get("id")},
                {"$set": content_item},
                upsert=True
            )
        except Exception as e:
            print(f"Error storing content to MongoDB: {e}")
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item in MongoDB"""
        if not self.db:
            return
        
        try:
            self.db.comments.update_one(
                {"id": comment_item.get("id")},
                {"$set": comment_item},
                upsert=True
            )
        except Exception as e:
            print(f"Error storing comment to MongoDB: {e}")
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information in MongoDB"""
        if not self.db:
            return
        
        try:
            self.db.creators.update_one(
                {"id": creator.get("id")},
                {"$set": creator},
                upsert=True
            )
        except Exception as e:
            print(f"Error storing creator to MongoDB: {e}")
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from MongoDB"""
        if not self.db:
            return None
        
        try:
            return self.db.content.find_one({"id": content_id})
        except Exception as e:
            print(f"Error getting content from MongoDB: {e}")
            return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from MongoDB"""
        if not self.db:
            return []
        
        try:
            return list(self.db.comments.find({"content_id": content_id}))
        except Exception as e:
            print(f"Error getting comments from MongoDB: {e}")
            return []
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from MongoDB"""
        if not self.db:
            return None
        
        try:
            return self.db.creators.find_one({"id": creator_id})
        except Exception as e:
            print(f"Error getting creator from MongoDB: {e}")
            return None
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()


class StoreImage(BaseStore, AbstractStoreImage):
    """Image store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.images_dir = os.path.join(self.data_dir, "images")
        os.makedirs(self.images_dir, exist_ok=True)
    
    async def store_image(self, image_content_item: Dict[str, Any]):
        """Store image content"""
        print(f"Storing image: {image_content_item.get('url', 'Unknown')}")
        # Implement image storage logic


class StoreVideo(BaseStore, AbstractStoreVideo):
    """Video store implementation"""
    
    def __init__(self, platform: str):
        super().__init__(platform)
        self.videos_dir = os.path.join(self.data_dir, "videos")
        os.makedirs(self.videos_dir, exist_ok=True)
    
    async def store_video(self, video_content_item: Dict[str, Any]):
        """Store video content"""
        print(f"Storing video: {video_content_item.get('url', 'Unknown')}")
        # Implement video storage logic