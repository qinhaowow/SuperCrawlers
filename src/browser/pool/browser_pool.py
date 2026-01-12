# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
from typing import Dict, Optional, Any, List

from playwright.async_api import BrowserContext, Page

from src.browser.manager import BrowserManager


class BrowserPool:
    """Browser pool implementation"""
    
    def __init__(self, max_browsers: int = 5, max_contexts_per_browser: int = 10):
        self._browser_manager = BrowserManager()
        self._max_browsers = max_browsers
        self._max_contexts_per_browser = max_contexts_per_browser
        self._context_pool = []
        self._page_pool = []
    
    async def initialize(self):
        """Initialize browser pool"""
        await self._browser_manager.initialize()
    
    async def get_context(self, **kwargs) -> BrowserContext:
        """Get a browser context from pool"""
        # Check if there are available contexts
        if self._context_pool:
            return self._context_pool.pop()
        
        # Create new context
        context = await self._browser_manager.create_context(**kwargs)
        return context
    
    async def return_context(self, context: BrowserContext, reuse: bool = True):
        """Return a browser context to pool"""
        if reuse:
            self._context_pool.append(context)
        else:
            await self._browser_manager.close_context(context)
    
    async def get_page(self, context: Optional[BrowserContext] = None, **kwargs) -> Page:
        """Get a page from pool"""
        # Check if there are available pages
        if self._page_pool:
            return self._page_pool.pop()
        
        # Create new page
        page = await self._browser_manager.create_page(context, **kwargs)
        return page
    
    async def return_page(self, page: Page, reuse: bool = True):
        """Return a page to pool"""
        if reuse:
            self._page_pool.append(page)
        else:
            await self._browser_manager.close_page(page)
    
    async def refresh_pool(self):
        """Refresh browser pool"""
        # Close all contexts and pages
        for context in self._context_pool:
            await self._browser_manager.close_context(context)
        self._context_pool.clear()
        
        for page in self._page_pool:
            await self._browser_manager.close_page(page)
        self._page_pool.clear()
    
    async def cleanup(self):
        """Cleanup browser pool"""
        await self.refresh_pool()
        await self._browser_manager.cleanup()
    
    async def get_pool_size(self) -> Dict[str, int]:
        """Get pool size"""
        return {
            'available_contexts': len(self._context_pool),
            'available_pages': len(self._page_pool),
            'total_browsers': await self._browser_manager.get_browser_count(),
            'total_contexts': await self._browser_manager.get_context_count(),
            'total_pages': await self._browser_manager.get_page_count()
        }