# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from src.core.base.base_crawler_impl import BaseCrawler


class XiaoHongShuCrawler(BaseCrawler):
    """Xiaohongshu crawler implementation"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Xiaohongshu"
        self.supported_features = [
            "search",
            "content_detail",
            "comments",
            "user_profile",
            "user_content",
            "login"
        ]
    
    async def start(self):
        """Start crawler"""
        await super().start()
    
    async def crawl(self):
        """Crawl logic"""
        # Get search query from config or use default
        search_query = getattr(self.config, 'SEARCH_QUERY', '美食')
        await self.search(search_query)
    
    async def search(self, query: str, **kwargs):
        """Search Xiaohongshu content"""
        print(f"Searching Xiaohongshu for: {query}")
        
        # Xiaohongshu search API
        url = "https://www.xiaohongshu.com/api/sns/v3/search/notes"
        params = {
            "keyword": query,
            "page": kwargs.get('page', 1),
            "sort": kwargs.get('sort', 'general')
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process search results
        notes = data.get('data', {}).get('notes', [])
        for note in notes:
            # Get content detail
            content_id = note.get('note_id')
            if content_id:
                content_detail = await self.get_content_detail(content_id)
                await self.store_data(content_detail, 'content')
        
        return notes
    
    async def get_content_detail(self, content_id: str):
        """Get Xiaohongshu content detail"""
        print(f"Getting Xiaohongshu content detail for: {content_id}")
        
        # Xiaohongshu content detail API
        url = f"https://www.xiaohongshu.com/api/sns/v3/notes/{content_id}"
        
        # Make API request
        data = await self.api_request("GET", url)
        
        # Process content detail
        note = data.get('data', {})
        content_detail = {
            'id': note.get('note_id'),
            'title': note.get('title'),
            'content': note.get('desc'),
            'author': note.get('user', {}).get('nickname'),
            'platform': self.platform_name,
            'created_at': note.get('time'),
            'url': f"https://www.xiaohongshu.com/explore/{content_id}",
            'metadata': note
        }
        
        return content_detail
    
    async def get_comments(self, content_id: str, max_comments: int = 100):
        """Get Xiaohongshu comments"""
        print(f"Getting Xiaohongshu comments for: {content_id}")
        
        # Xiaohongshu comments API
        url = f"https://www.xiaohongshu.com/api/sns/v3/notes/{content_id}/comments"
        params = {
            "page": 1,
            "count": max_comments
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process comments
        comments = data.get('data', {}).get('comments', [])
        comment_list = []
        
        for comment in comments:
            comment_item = {
                'id': comment.get('id'),
                'content_id': content_id,
                'author': comment.get('user', {}).get('nickname'),
                'content': comment.get('content'),
                'created_at': comment.get('time'),
                'metadata': comment
            }
            comment_list.append(comment_item)
            await self.store_data(comment_item, 'comment')
        
        return comment_list
    
    async def get_user_profile(self, user_id: str):
        """Get Xiaohongshu user profile"""
        print(f"Getting Xiaohongshu user profile for: {user_id}")
        
        # Xiaohongshu user profile API
        url = f"https://www.xiaohongshu.com/api/sns/v3/user/{user_id}"
        
        # Make API request
        data = await self.api_request("GET", url)
        
        # Process user profile
        user = data.get('data', {})
        user_profile = {
            'id': user.get('id'),
            'name': user.get('nickname'),
            'username': user.get('username'),
            'platform': self.platform_name,
            'followers': user.get('follower_count'),
            'following': user.get('following_count'),
            'metadata': user
        }
        
        await self.store_data(user_profile, 'creator')
        return user_profile
    
    async def get_user_content(self, user_id: str, max_items: int = 50):
        """Get Xiaohongshu user content"""
        print(f"Getting Xiaohongshu user content for: {user_id}")
        
        # Xiaohongshu user content API
        url = f"https://www.xiaohongshu.com/api/sns/v3/user/{user_id}/notes"
        params = {
            "page": 1,
            "count": max_items
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process user content
        notes = data.get('data', {}).get('notes', [])
        content_list = []
        
        for note in notes:
            content_item = {
                'id': note.get('note_id'),
                'title': note.get('title'),
                'content': note.get('desc'),
                'author': note.get('user', {}).get('nickname'),
                'platform': self.platform_name,
                'created_at': note.get('time'),
                'url': f"https://www.xiaohongshu.com/explore/{note.get('note_id')}",
                'metadata': note
            }
            content_list.append(content_item)
            await self.store_data(content_item, 'content')
        
        return content_list