# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from src.core.base.base_crawler_impl import BaseCrawler


class DouYinCrawler(BaseCrawler):
    """Douyin crawler implementation"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Douyin"
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
        """Search Douyin content"""
        print(f"Searching Douyin for: {query}")
        
        # Douyin search API
        url = "https://api.amemv.com/aweme/v1/search/item"
        params = {
            "keyword": query,
            "offset": (kwargs.get('page', 1) - 1) * 20,
            "count": 20
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process search results
        aweme_list = data.get('aweme_list', [])
        for aweme in aweme_list:
            # Get content detail
            content_id = aweme.get('aweme_id')
            if content_id:
                content_detail = await self.get_content_detail(content_id)
                await self.store_data(content_detail, 'content')
        
        return aweme_list
    
    async def get_content_detail(self, content_id: str):
        """Get Douyin content detail"""
        print(f"Getting Douyin content detail for: {content_id}")
        
        # Douyin content detail API
        url = f"https://api.amemv.com/aweme/v1/aweme/detail"
        params = {
            "aweme_id": content_id
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process content detail
        aweme = data.get('aweme_detail', {})
        content_detail = {
            'id': aweme.get('aweme_id'),
            'title': aweme.get('desc'),
            'content': aweme.get('desc'),
            'author': aweme.get('author', {}).get('nickname'),
            'platform': self.platform_name,
            'created_at': aweme.get('create_time'),
            'url': f"https://www.douyin.com/video/{content_id}",
            'metadata': aweme
        }
        
        return content_detail
    
    async def get_comments(self, content_id: str, max_comments: int = 100):
        """Get Douyin comments"""
        print(f"Getting Douyin comments for: {content_id}")
        
        # Douyin comments API
        url = "https://api.amemv.com/aweme/v2/comment/list"
        params = {
            "aweme_id": content_id,
            "count": max_comments,
            "offset": 0
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process comments
        comments = data.get('comments', [])
        comment_list = []
        
        for comment in comments:
            comment_item = {
                'id': comment.get('cid'),
                'content_id': content_id,
                'author': comment.get('user', {}).get('nickname'),
                'content': comment.get('text'),
                'created_at': comment.get('create_time'),
                'metadata': comment
            }
            comment_list.append(comment_item)
            await self.store_data(comment_item, 'comment')
        
        return comment_list
    
    async def get_user_profile(self, user_id: str):
        """Get Douyin user profile"""
        print(f"Getting Douyin user profile for: {user_id}")
        
        # Douyin user profile API
        url = "https://api.amemv.com/aweme/v1/user"
        params = {
            "user_id": user_id
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process user profile
        user = data.get('user', {})
        user_profile = {
            'id': user.get('uid'),
            'name': user.get('nickname'),
            'username': user.get('unique_id'),
            'platform': self.platform_name,
            'followers': user.get('follower_count'),
            'following': user.get('following_count'),
            'metadata': user
        }
        
        await self.store_data(user_profile, 'creator')
        return user_profile
    
    async def get_user_content(self, user_id: str, max_items: int = 50):
        """Get Douyin user content"""
        print(f"Getting Douyin user content for: {user_id}")
        
        # Douyin user content API
        url = "https://api.amemv.com/aweme/v1/aweme/post"
        params = {
            "user_id": user_id,
            "count": max_items,
            "offset": 0
        }
        
        # Make API request
        data = await self.api_request("GET", url, params=params)
        
        # Process user content
        aweme_list = data.get('aweme_list', [])
        content_list = []
        
        for aweme in aweme_list:
            content_item = {
                'id': aweme.get('aweme_id'),
                'title': aweme.get('desc'),
                'content': aweme.get('desc'),
                'author': aweme.get('author', {}).get('nickname'),
                'platform': self.platform_name,
                'created_at': aweme.get('create_time'),
                'url': f"https://www.douyin.com/video/{aweme.get('aweme_id')}",
                'metadata': aweme
            }
            content_list.append(content_item)
            await self.store_data(content_item, 'content')
        
        return content_list