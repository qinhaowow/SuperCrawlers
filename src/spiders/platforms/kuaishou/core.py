# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from src.core.base.base_crawler_impl import BaseCrawler


class KuaishouCrawler(BaseCrawler):
    """Kuaishou crawler implementation"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Kuaishou"
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
        """Search Kuaishou content"""
        print(f"Searching Kuaishou for: {query}")
        
        # Kuaishou search API
        url = "https://api.kuaishou.com/graphql"
        data = {
            "operationName": "visionSearchPhoto",
            "variables": {
                "keyword": query,
                "pcursor": kwargs.get('pcursor', ''),
                "page": kwargs.get('page', 1)
            },
            "query": """
            query visionSearchPhoto($keyword: String, $pcursor: String, $page: Int) {
                visionSearchPhoto(keyword: $keyword, pcursor: $pcursor, page: $page) {
                    result
                    pcursor
                    feeds {
                        id
                        type
                        authorId
                        caption
                        photoId
                        playUrl
                        coverUrl
                        timestamp
                        user {
                            id
                            name
                            avatar
                        }
                    }
                }
            }
            """
        }
        
        # Make API request
        data = await self.api_request("POST", url, json=data)
        
        # Process search results
        feeds = data.get('data', {}).get('visionSearchPhoto', {}).get('feeds', [])
        for feed in feeds:
            # Get content detail
            content_id = feed.get('photoId')
            if content_id:
                content_detail = await self.get_content_detail(content_id)
                await self.store_data(content_detail, 'content')
        
        return feeds
    
    async def get_content_detail(self, content_id: str):
        """Get Kuaishou content detail"""
        print(f"Getting Kuaishou content detail for: {content_id}")
        
        # Kuaishou content detail API
        url = "https://api.kuaishou.com/graphql"
        data = {
            "operationName": "photoDetail",
            "variables": {
                "photoId": content_id
            },
            "query": """
            query photoDetail($photoId: String!) {
                photoDetail(photoId: $photoId) {
                    id
                    type
                    authorId
                    caption
                    photoId
                    playUrl
                    coverUrl
                    timestamp
                    user {
                        id
                        name
                        avatar
                    }
                }
            }
            """
        }
        
        # Make API request
        data = await self.api_request("POST", url, json=data)
        
        # Process content detail
        photo = data.get('data', {}).get('photoDetail', {})
        content_detail = {
            'id': photo.get('photoId'),
            'title': photo.get('caption'),
            'content': photo.get('caption'),
            'author': photo.get('user', {}).get('name'),
            'platform': self.platform_name,
            'created_at': photo.get('timestamp'),
            'url': f"https://www.kuaishou.com/short-video/{content_id}",
            'metadata': photo
        }
        
        return content_detail
    
    async def get_comments(self, content_id: str, max_comments: int = 100):
        """Get Kuaishou comments"""
        print(f"Getting Kuaishou comments for: {content_id}")
        
        # Kuaishou comments API
        url = "https://api.kuaishou.com/graphql"
        data = {
            "operationName": "commentList",
            "variables": {
                "photoId": content_id,
                "pcursor": "",
                "count": max_comments
            },
            "query": """
            query commentList($photoId: String!, $pcursor: String, $count: Int) {
                commentList(photoId: $photoId, pcursor: $pcursor, count: $count) {
                    result
                    pcursor
                    comments {
                        id
                        authorId
                        content
                        timestamp
                        user {
                            id
                            name
                            avatar
                        }
                    }
                }
            }
            """
        }
        
        # Make API request
        data = await self.api_request("POST", url, json=data)
        
        # Process comments
        comments = data.get('data', {}).get('commentList', {}).get('comments', [])
        comment_list = []
        
        for comment in comments:
            comment_item = {
                'id': comment.get('id'),
                'content_id': content_id,
                'author': comment.get('user', {}).get('name'),
                'content': comment.get('content'),
                'created_at': comment.get('timestamp'),
                'metadata': comment
            }
            comment_list.append(comment_item)
            await self.store_data(comment_item, 'comment')
        
        return comment_list
    
    async def get_user_profile(self, user_id: str):
        """Get Kuaishou user profile"""
        print(f"Getting Kuaishou user profile for: {user_id}")
        
        # Kuaishou user profile API
        url = "https://api.kuaishou.com/graphql"
        data = {
            "operationName": "userProfile",
            "variables": {
                "userId": user_id
            },
            "query": """
            query userProfile($userId: String!) {
                userProfile(userId: $userId) {
                    id
                    name
                    avatar
                    followerCount
                    followingCount
                    photoCount
                }
            }
            """
        }
        
        # Make API request
        data = await self.api_request("POST", url, json=data)
        
        # Process user profile
        user = data.get('data', {}).get('userProfile', {})
        user_profile = {
            'id': user.get('id'),
            'name': user.get('name'),
            'username': user.get('id'),
            'platform': self.platform_name,
            'followers': user.get('followerCount'),
            'following': user.get('followingCount'),
            'metadata': user
        }
        
        await self.store_data(user_profile, 'creator')
        return user_profile
    
    async def get_user_content(self, user_id: str, max_items: int = 50):
        """Get Kuaishou user content"""
        print(f"Getting Kuaishou user content for: {user_id}")
        
        # Kuaishou user content API
        url = "https://api.kuaishou.com/graphql"
        data = {
            "operationName": "fetchUserFeed",
            "variables": {
                "userId": user_id,
                "pcursor": "",
                "count": max_items
            },
            "query": """
            query fetchUserFeed($userId: String!, $pcursor: String, $count: Int) {
                fetchUserFeed(userId: $userId, pcursor: $pcursor, count: $count) {
                    result
                    pcursor
                    feeds {
                        id
                        type
                        authorId
                        caption
                        photoId
                        playUrl
                        coverUrl
                        timestamp
                        user {
                            id
                            name
                            avatar
                        }
                    }
                }
            }
            """
        }
        
        # Make API request
        data = await self.api_request("POST", url, json=data)
        
        # Process user content
        feeds = data.get('data', {}).get('fetchUserFeed', {}).get('feeds', [])
        content_list = []
        
        for feed in feeds:
            content_item = {
                'id': feed.get('photoId'),
                'title': feed.get('caption'),
                'content': feed.get('caption'),
                'author': feed.get('user', {}).get('name'),
                'platform': self.platform_name,
                'created_at': feed.get('timestamp'),
                'url': f"https://www.kuaishou.com/short-video/{feed.get('photoId')}",
                'metadata': feed
            }
            content_list.append(content_item)
            await self.store_data(content_item, 'content')
        
        return content_list