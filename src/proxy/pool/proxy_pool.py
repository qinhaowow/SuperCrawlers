# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
from typing import Dict, Optional, Any, List

from src.proxy.manager import BaseProxyManager


class ProxyPool:
    """Proxy pool implementation"""
    
    def __init__(self, proxy_manager: BaseProxyManager):
        self._proxy_manager = proxy_manager
        self._available_proxies = []
        self._validating = False
    
    async def initialize(self):
        """Initialize proxy pool"""
        await self._proxy_manager.initialize()
        await self._refresh_pool()
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a proxy from pool"""
        if not self._available_proxies:
            await self._refresh_pool()
        
        if not self._available_proxies:
            return None
        
        # Get first available proxy
        proxy = self._available_proxies.pop(0)
        
        # Validate proxy
        if not await self._proxy_manager.validate_proxy(proxy):
            return await self.get_proxy()
        
        return proxy
    
    async def return_proxy(self, proxy: Dict[str, str], is_valid: bool = True):
        """Return proxy to pool"""
        if is_valid:
            self._available_proxies.append(proxy)
    
    async def refresh_pool(self):
        """Refresh proxy pool"""
        await self._refresh_pool()
    
    async def _refresh_pool(self):
        """Refresh proxy pool internal implementation"""
        if self._validating:
            return
        
        self._validating = True
        
        try:
            # Get all proxies from manager
            proxies = []
            for _ in range(10):  # Try to get 10 proxies
                proxy = await self._proxy_manager.get_proxy()
                if proxy and proxy not in proxies:
                    proxies.append(proxy)
                await self._proxy_manager.rotate_proxy()
            
            # Validate all proxies
            valid_proxies = []
            tasks = [self._proxy_manager.validate_proxy(proxy) for proxy in proxies]
            results = await asyncio.gather(*tasks)
            
            for proxy, is_valid in zip(proxies, results):
                if is_valid:
                    valid_proxies.append(proxy)
            
            self._available_proxies = valid_proxies
        finally:
            self._validating = False
    
    async def get_pool_size(self) -> int:
        """Get pool size"""
        return len(self._available_proxies)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "pool_size": await self.get_pool_size(),
            "proxy_stats": await self._proxy_manager.get_proxy_stats()
        }