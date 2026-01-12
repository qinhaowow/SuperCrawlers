# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from pymongo import MongoClient
from typing import Dict, Optional, Any, List

from src.storage.base.base_store import BaseStore, BaseStoreImage, BaseStoreVideo


class MongoDBStore(BaseStore):
    """MongoDB store implementation"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", db_name: str = "supercrawler"):
        super().__init__()
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
    
    async def initialize(self):
        """Initialize MongoDB store"""
        await super().initialize()
        # Connect to MongoDB
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item to MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Insert or update content
        self.db.content.update_one(
            {"id": content_item.get("id")},
            {"$set": content_item},
            upsert=True
        )
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item to MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Insert or update comment
        self.db.comments.update_one(
            {"id": comment_item.get("id")},
            {"$set": comment_item},
            upsert=True
        )
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information to MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Insert or update creator
        self.db.creators.update_one(
            {"id": creator.get("id")},
            {"$set": creator},
            upsert=True
        )
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Find content by ID
        content = self.db.content.find_one({"id": content_id})
        if content:
            # Convert ObjectId to string
            if "_id" in content:
                content["_id"] = str(content["_id"])
            return content
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Find comments by content ID
        comments = []
        for comment in self.db.comments.find({"content_id": content_id}):
            # Convert ObjectId to string
            if "_id" in comment:
                comment["_id"] = str(comment["_id"])
            comments.append(comment)
        return comments
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Find creator by ID
        creator = self.db.creators.find_one({"id": creator_id})
        if creator:
            # Convert ObjectId to string
            if "_id" in creator:
                creator["_id"] = str(creator["_id"])
            return creator
        return None
    
    async def close(self):
        """Close MongoDB store"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
        await super().close()


class MongoDBStoreImage(BaseStoreImage):
    """MongoDB store image implementation"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", db_name: str = "supercrawler"):
        super().__init__()
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
    
    async def initialize(self):
        """Initialize MongoDB store image"""
        await super().initialize()
        # Connect to MongoDB
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
    
    async def store_image(self, image_content_item: Dict[str, Any]):
        """Store image content to MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Insert or update image
        self.db.images.update_one(
            {"id": image_content_item.get("id")},
            {"$set": image_content_item},
            upsert=True
        )
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID from MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Find image by ID
        image = self.db.images.find_one({"id": image_id})
        if image:
            # Convert ObjectId to string
            if "_id" in image:
                image["_id"] = str(image["_id"])
            return image
        return None
    
    async def close(self):
        """Close MongoDB store image"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
        await super().close()


class MongoDBStoreVideo(BaseStoreVideo):
    """MongoDB store video implementation"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", db_name: str = "supercrawler"):
        super().__init__()
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
    
    async def initialize(self):
        """Initialize MongoDB store video"""
        await super().initialize()
        # Connect to MongoDB
        self.client = MongoClient(self.connection_string)
        self.db = self.client[self.db_name]
    
    async def store_video(self, video_content_item: Dict[str, Any]):
        """Store video content to MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Insert or update video
        self.db.videos.update_one(
            {"id": video_content_item.get("id")},
            {"$set": video_content_item},
            upsert=True
        )
    
    async def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID from MongoDB"""
        if not self.connected:
            await self.initialize()
        
        # Find video by ID
        video = self.db.videos.find_one({"id": video_id})
        if video:
            # Convert ObjectId to string
            if "_id" in video:
                video["_id"] = str(video["_id"])
            return video
        return None
    
    async def close(self):
        """Close MongoDB store video"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
        await super().close()