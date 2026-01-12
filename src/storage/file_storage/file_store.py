# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import json
import csv
import os
import aiofiles
from typing import Dict, Optional, Any, List

from src.storage.base.base_store import BaseStore, BaseStoreImage, BaseStoreVideo


class FileStore(BaseStore):
    """File store implementation"""
    
    def __init__(self, output_dir: str = "./output"):
        super().__init__()
        self.output_dir = output_dir
        self.content_file = os.path.join(output_dir, "content.json")
        self.comments_file = os.path.join(output_dir, "comments.json")
        self.creators_file = os.path.join(output_dir, "creators.json")
    
    async def initialize(self):
        """Initialize file store"""
        await super().initialize()
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create empty files if they don't exist
        for file_path in [self.content_file, self.comments_file, self.creators_file]:
            if not os.path.exists(file_path):
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write('[]')
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item to file"""
        if not self.connected:
            await self.initialize()
        
        # Read existing content
        async with aiofiles.open(self.content_file, 'r', encoding='utf-8') as f:
            content = json.loads(await f.read())
        
        # Add new content
        content.append(content_item)
        
        # Write back to file
        async with aiofiles.open(self.content_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(content, ensure_ascii=False, indent=2))
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item to file"""
        if not self.connected:
            await self.initialize()
        
        # Read existing comments
        async with aiofiles.open(self.comments_file, 'r', encoding='utf-8') as f:
            comments = json.loads(await f.read())
        
        # Add new comment
        comments.append(comment_item)
        
        # Write back to file
        async with aiofiles.open(self.comments_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(comments, ensure_ascii=False, indent=2))
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information to file"""
        if not self.connected:
            await self.initialize()
        
        # Read existing creators
        async with aiofiles.open(self.creators_file, 'r', encoding='utf-8') as f:
            creators = json.loads(await f.read())
        
        # Add new creator
        creators.append(creator)
        
        # Write back to file
        async with aiofiles.open(self.creators_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(creators, ensure_ascii=False, indent=2))
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from file"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.content_file, 'r', encoding='utf-8') as f:
            content = json.loads(await f.read())
        
        for item in content:
            if item.get('id') == content_id:
                return item
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from file"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.comments_file, 'r', encoding='utf-8') as f:
            comments = json.loads(await f.read())
        
        return [comment for comment in comments if comment.get('content_id') == content_id]
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from file"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.creators_file, 'r', encoding='utf-8') as f:
            creators = json.loads(await f.read())
        
        for creator in creators:
            if creator.get('id') == creator_id:
                return creator
        return None
    
    async def close(self):
        """Close file store"""
        await super().close()


class CSVStore(BaseStore):
    """CSV store implementation"""
    
    def __init__(self, output_dir: str = "./output"):
        super().__init__()
        self.output_dir = output_dir
        self.content_file = os.path.join(output_dir, "content.csv")
        self.comments_file = os.path.join(output_dir, "comments.csv")
        self.creators_file = os.path.join(output_dir, "creators.csv")
    
    async def initialize(self):
        """Initialize CSV store"""
        await super().initialize()
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create CSV files with headers if they don't exist
        if not os.path.exists(self.content_file):
            async with aiofiles.open(self.content_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'title', 'content', 'author', 'platform', 'created_at', 'url'])
                writer.writeheader()
        
        if not os.path.exists(self.comments_file):
            async with aiofiles.open(self.comments_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'content_id', 'author', 'content', 'created_at'])
                writer.writeheader()
        
        if not os.path.exists(self.creators_file):
            async with aiofiles.open(self.creators_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'name', 'username', 'platform', 'followers', 'following'])
                writer.writeheader()
    
    async def store_content(self, content_item: Dict[str, Any]):
        """Store content item to CSV"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.content_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'title', 'content', 'author', 'platform', 'created_at', 'url'])
            writer.writerow(content_item)
    
    async def store_comment(self, comment_item: Dict[str, Any]):
        """Store comment item to CSV"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.comments_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'content_id', 'author', 'content', 'created_at'])
            writer.writerow(comment_item)
    
    async def store_creator(self, creator: Dict[str, Any]):
        """Store creator information to CSV"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.creators_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'username', 'platform', 'followers', 'following'])
            writer.writerow(creator)
    
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content by ID from CSV"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.content_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            async for row in reader:
                if row.get('id') == content_id:
                    return row
        return None
    
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """Get comments by content ID from CSV"""
        if not self.connected:
            await self.initialize()
        
        comments = []
        async with aiofiles.open(self.comments_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            async for row in reader:
                if row.get('content_id') == content_id:
                    comments.append(row)
        return comments
    
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """Get creator by ID from CSV"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.creators_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            async for row in reader:
                if row.get('id') == creator_id:
                    return row
        return None
    
    async def close(self):
        """Close CSV store"""
        await super().close()


class FileStoreImage(BaseStoreImage):
    """File store image implementation"""
    
    def __init__(self, output_dir: str = "./output/images"):
        super().__init__()
        self.output_dir = output_dir
        self.images_file = os.path.join(output_dir, "images.json")
    
    async def initialize(self):
        """Initialize file store image"""
        await super().initialize()
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(self.images_file):
            async with aiofiles.open(self.images_file, 'w', encoding='utf-8') as f:
                await f.write('[]')
    
    async def store_image(self, image_content_item: Dict[str, Any]):
        """Store image content to file"""
        if not self.connected:
            await self.initialize()
        
        # Read existing images
        async with aiofiles.open(self.images_file, 'r', encoding='utf-8') as f:
            images = json.loads(await f.read())
        
        # Add new image
        images.append(image_content_item)
        
        # Write back to file
        async with aiofiles.open(self.images_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(images, ensure_ascii=False, indent=2))
    
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get image by ID from file"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.images_file, 'r', encoding='utf-8') as f:
            images = json.loads(await f.read())
        
        for image in images:
            if image.get('id') == image_id:
                return image
        return None
    
    async def close(self):
        """Close file store image"""
        await super().close()


class FileStoreVideo(BaseStoreVideo):
    """File store video implementation"""
    
    def __init__(self, output_dir: str = "./output/videos"):
        super().__init__()
        self.output_dir = output_dir
        self.videos_file = os.path.join(output_dir, "videos.json")
    
    async def initialize(self):
        """Initialize file store video"""
        await super().initialize()
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(self.videos_file):
            async with aiofiles.open(self.videos_file, 'w', encoding='utf-8') as f:
                await f.write('[]')
    
    async def store_video(self, video_content_item: Dict[str, Any]):
        """Store video content to file"""
        if not self.connected:
            await self.initialize()
        
        # Read existing videos
        async with aiofiles.open(self.videos_file, 'r', encoding='utf-8') as f:
            videos = json.loads(await f.read())
        
        # Add new video
        videos.append(video_content_item)
        
        # Write back to file
        async with aiofiles.open(self.videos_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(videos, ensure_ascii=False, indent=2))
    
    async def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video by ID from file"""
        if not self.connected:
            await self.initialize()
        
        async with aiofiles.open(self.videos_file, 'r', encoding='utf-8') as f:
            videos = json.loads(await f.read())
        
        for video in videos:
            if video.get('id') == video_id:
                return video
        return None
    
    async def close(self):
        """Close file store video"""
        await super().close()