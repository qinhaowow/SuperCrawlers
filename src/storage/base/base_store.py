# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List

from src.core.base.base_crawler import AbstractStore, AbstractStoreImage, AbstractStoreVideo


class BaseStore(AbstractStore):
    """Base store implementation"""
    
    def __init__(self):
        self._connected = False
    
    async def initialize(self):
        """Initialize store"""
        self._connected = True
    
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
        pass
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID"""
        pass
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID"""
        pass
    
    async def close(self):
        """Close storage connection"""
        self._connected = False
    
    @property
    def connected(self) -> bool:
        """Check if store is connected"""
        return self._connected


class BaseStoreImage(AbstractStoreImage):
    """Base store image implementation"""
    
    def __init__(self):
        self._connected = False
    
    async def initialize(self):
        """Initialize store"""
        self._connected = True
    
    async def store_image(self, image_content_item: Dict[str, Any]):
        """Store image content"""
        pass
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID"""
        pass
    
    async def close(self):
        """Close storage connection"""
        self._connected = False
    
    @property
    def connected(self) -> bool:
        """Check if store is connected"""
        return self._connected


class BaseStoreVideo(AbstractStoreVideo):
    """Base store video implementation"""
    
    def __init__(self):
        self._connected = False
    
    async def initialize(self):
        """Initialize store"""
        self._connected = True
    
    async def store_video(self, video_content_item: Dict[str, Any]):
        """Store video content"""
        pass
    
    async def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID"""
        pass
    
    async def close(self):
        """Close storage connection"""
        self._connected = False
    
    @property
    def connected(self) -> bool:
        """Check if store is connected"""
        return self._connected