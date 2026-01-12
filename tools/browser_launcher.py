# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import os
from typing import Dict, Optional, Any
from playwright.async_api import Playwright, BrowserType, BrowserContext, Page

from config import base_config


class BrowserLauncher:
    """Browser launcher for Playwright"""
    
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser_contexts: Dict[str, BrowserContext] = {}
    
    async def initialize(self):
        """Initialize Playwright"""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()
    
    async def launch_browser(self, platform: str, proxy: Optional[Dict[str, str]] = None, 
                           user_agent: Optional[str] = None, headless: Optional[bool] = None) -> BrowserContext:
        """Launch browser with specified settings"""
        if not self.playwright:
            await self.initialize()
        
        # Use global setting if headless not specified
        if headless is None:
            headless = base_config.HEADLESS
        
        # Use CDP if enabled
        if base_config.USE_CDP:
            return await self._launch_browser_with_cdp(platform, proxy, user_agent, headless)
        
        # Use standard Playwright launch
        return await self._launch_browser_standard(platform, proxy, user_agent, headless)
    
    async def _launch_browser_standard(self, platform: str, proxy: Optional[Dict[str, str]] = None, 
                                     user_agent: Optional[str] = None, headless: bool = True) -> BrowserContext:
        """Launch browser using standard Playwright method"""
        chromium = self.playwright.chromium
        
        # Browser launch options
        launch_options = {
            "headless": headless,
            "proxy": proxy,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-extensions",
                "--disable-infobars",
                "--disable-notifications",
                "--disable-popup-blocking",
                "--disable-translate",
                "--ignore-certificate-errors",
                "--window-size=1920,1080",
            ]
        }
        
        # Create context with additional settings
        context = await chromium.launch_persistent_context(
            "",  # Empty directory for temporary profile
            **launch_options,
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            timezone_id="Asia/Shanghai",
            geolocation={"latitude": 31.2304, "longitude": 121.4737},  # Shanghai coordinates
            permissions=["geolocation"],
        )
        
        # Apply stealth techniques
        await self._apply_stealth(context)
        
        # Store context
        self.browser_contexts[platform] = context
        
        return context
    
    async def _launch_browser_with_cdp(self, platform: str, proxy: Optional[Dict[str, str]] = None, 
                                     user_agent: Optional[str] = None, headless: bool = True) -> BrowserContext:
        """Launch browser using CDP mode"""
        chromium = self.playwright.chromium
        
        # Launch browser with CDP options
        browser = await chromium.launch(
            headless=headless,
            proxy=proxy,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--remote-debugging-port=9222",
                "--window-size=1920,1080",
            ]
        )
        
        # Create context
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1920, "height": 1080},
            timezone_id="Asia/Shanghai",
            geolocation={"latitude": 31.2304, "longitude": 121.4737},
            permissions=["geolocation"],
        )
        
        # Apply stealth techniques
        await self._apply_stealth(context)
        
        # Store context
        self.browser_contexts[platform] = context
        
        return context
    
    async def _apply_stealth(self, context: BrowserContext):
        """Apply stealth techniques to avoid detection"""
        # Load stealth.min.js
        stealth_js_path = os.path.join(os.path.dirname(__file__), "..", "libs", "stealth.min.js")
        
        if os.path.exists(stealth_js_path):
            with open(stealth_js_path, "r", encoding="utf-8") as f:
                stealth_js = f.read()
        else:
            # Fallback to basic stealth
            stealth_js = """
            // Basic stealth techniques
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Remove Chrome-specific properties
            if (window.chrome) {
                delete window.chrome.loadTimes;
                delete window.chrome.csi;
            }
            
            // Mock navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });
            
            // Mock navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [{}]
            });
            
            // Mock navigator.mimeTypes
            Object.defineProperty(navigator, 'mimeTypes', {
                get: () => [{}]
            });
            
            // Mock window.outerWidth and window.outerHeight
            Object.defineProperty(window, 'outerWidth', {
                get: () => window.innerWidth
            });
            Object.defineProperty(window, 'outerHeight', {
                get: () => window.innerHeight
            });
            
            // Mock screen orientation
            Object.defineProperty(screen, 'orientation', {
                get: () => ({
                    angle: 0,
                    type: 'landscape-primary',
                    onchange: null
                })
            });
            """
        
        # Apply stealth to all pages
        page = await context.new_page()
        await page.evaluate(stealth_js)
        await page.close()
    
    async def get_browser_context(self, platform: str) -> Optional[BrowserContext]:
        """Get existing browser context for platform"""
        return self.browser_contexts.get(platform)
    
    async def close_browser(self, platform: str):
        """Close browser for specific platform"""
        if platform in self.browser_contexts:
            context = self.browser_contexts[platform]
            try:
                await context.close()
            except Exception:
                pass
            del self.browser_contexts[platform]
    
    async def close_all_browsers(self):
        """Close all browser contexts"""
        for platform in list(self.browser_contexts.keys()):
            await self.close_browser(platform)
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.close_all_browsers()
        if self.playwright:
            await self.playwright.stop()
    
    async def new_page(self, platform: str) -> Page:
        """Create a new page for specified platform"""
        context = await self.get_browser_context(platform)
        if not context:
            context = await self.launch_browser(platform)
        return await context.new_page()


# Global browser launcher instance
browser_launcher = BrowserLauncher()


async def get_browser_launcher() -> BrowserLauncher:
    """Get browser launcher instance"""
    return browser_launcher


async def launch_browser(platform: str, proxy: Optional[Dict[str, str]] = None, 
                       user_agent: Optional[str] = None, headless: Optional[bool] = None) -> BrowserContext:
    """Launch browser for specified platform"""
    return await browser_launcher.launch_browser(platform, proxy, user_agent, headless)


async def close_browser(platform: str):
    """Close browser for specified platform"""
    await browser_launcher.close_browser(platform)


async def close_all_browsers():
    """Close all browsers"""
    await browser_launcher.close_all_browsers()


async def cleanup_browser_resources():
    """Cleanup browser resources"""
    await browser_launcher.cleanup()