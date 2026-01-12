# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, Optional, Any, List
from playwright.async_api import BrowserContext, BrowserType, Playwright

from base.base_crawler import AbstractCrawler, AbstractLogin, AbstractApiClient


class BaseCrawler(AbstractCrawler):
    """Base crawler implementation with common functionality"""
    
    def __init__(self):
        self.platform_name = "base"
        self.supported_features = [
            "search",
            "content_detail",
            "comments",
            "user_profile",
            "user_content",
            "login"
        ]
        self.browser_context: Optional[BrowserContext] = None
        self.api_client: Optional[AbstractApiClient] = None
        self.login_manager: Optional[AbstractLogin] = None
    
    async def start(self):
        """Start crawler"""
        print(f"Starting {self.get_platform_name()} crawler...")
    
    async def search(self, query: str, **kwargs):
        """Search content"""
        print(f"Searching {self.get_platform_name()} for: {query}")
        return []
    
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], 
                            user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """Launch browser"""
        print(f"Launching browser for {self.get_platform_name()}...")
        context = await chromium.launch_persistent_context(
            "",
            headless=headless,
            proxy=playwright_proxy,
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        self.browser_context = context
        return context
    
    async def get_content_detail(self, content_id: str) -> Dict[str, Any]:
        """Get content detail by ID"""
        print(f"Getting content detail for {content_id} on {self.get_platform_name()}...")
        return {}
    
    async def get_comments(self, content_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        """Get comments for content"""
        print(f"Getting comments for {content_id} on {self.get_platform_name()}...")
        return []
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile"""
        print(f"Getting user profile for {user_id} on {self.get_platform_name()}...")
        return {}
    
    async def get_user_content(self, user_id: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """Get user's content"""
        print(f"Getting user content for {user_id} on {self.get_platform_name()}...")
        return []
    
    def get_platform_name(self) -> str:
        """Get platform name"""
        return self.platform_name
    
    def get_supported_features(self) -> List[str]:
        """Get list of supported features"""
        return self.supported_features