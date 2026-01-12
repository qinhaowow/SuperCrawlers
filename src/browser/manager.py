# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
from typing import Dict, Optional, Any, List

from playwright.async_api import Playwright, Browser, BrowserContext, Page


class BrowserManager:
    """Browser manager implementation"""
    
    def __init__(self):
        self._playwright = None
        self._browsers = []
        self._browser_contexts = []
        self._pages = []
    
    async def initialize(self):
        """Initialize browser manager"""
        from playwright.async_api import async_playwright
        self._playwright = await async_playwright().start()
    
    async def launch_browser(self, **kwargs) -> Browser:
        """Launch a browser"""
        browser = await self._playwright.chromium.launch(**kwargs)
        self._browsers.append(browser)
        return browser
    
    async def create_context(self, browser: Optional[Browser] = None, **kwargs) -> BrowserContext:
        """Create a browser context"""
        if not browser:
            browser = await self.launch_browser()
        
        context = await browser.new_context(**kwargs)
        self._browser_contexts.append(context)
        return context
    
    async def create_page(self, context: Optional[BrowserContext] = None, **kwargs) -> Page:
        """Create a page"""
        if not context:
            context = await self.create_context()
        
        page = await context.new_page(**kwargs)
        self._pages.append(page)
        return page
    
    async def close_browser(self, browser: Browser):
        """Close a browser"""
        if browser in self._browsers:
            await browser.close()
            self._browsers.remove(browser)
    
    async def close_context(self, context: BrowserContext):
        """Close a browser context"""
        if context in self._browser_contexts:
            await context.close()
            self._browser_contexts.remove(context)
    
    async def close_page(self, page: Page):
        """Close a page"""
        if page in self._pages:
            await page.close()
            self._pages.remove(page)
    
    async def cleanup(self):
        """Cleanup browser manager"""
        # Close all pages
        for page in self._pages:
            try:
                await page.close()
            except Exception:
                pass
        
        # Close all contexts
        for context in self._browser_contexts:
            try:
                await context.close()
            except Exception:
                pass
        
        # Close all browsers
        for browser in self._browsers:
            try:
                await browser.close()
            except Exception:
                pass
        
        # Stop playwright
        if self._playwright:
            await self._playwright.stop()
    
    async def get_browser_count(self) -> int:
        """Get browser count"""
        return len(self._browsers)
    
    async def get_context_count(self) -> int:
        """Get context count"""
        return len(self._browser_contexts)
    
    async def get_page_count(self) -> int:
        """Get page count"""
        return len(self._pages)