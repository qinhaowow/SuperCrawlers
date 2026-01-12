# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import random
from typing import Dict, Optional, Any, List

from src.proxy.manager import BaseProxyManager


class RoundRobinProxyStrategy:
    """Round robin proxy selection strategy"""
    
    def __init__(self, proxy_manager: BaseProxyManager):
        self._proxy_manager = proxy_manager
        self._current_index = 0
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy using round robin strategy"""
        proxy = await self._proxy_manager.get_proxy()
        await self._proxy_manager.rotate_proxy()
        return proxy


class RandomProxyStrategy:
    """Random proxy selection strategy"""
    
    def __init__(self, proxy_manager: BaseProxyManager):
        self._proxy_manager = proxy_manager
        self._proxy_list = []
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy using random strategy"""
        if not self._proxy_list:
            # Load proxies
            for _ in range(10):
                proxy = await self._proxy_manager.get_proxy()
                if proxy and proxy not in self._proxy_list:
                    self._proxy_list.append(proxy)
                await self._proxy_manager.rotate_proxy()
        
        if not self._proxy_list:
            return None
        
        # Randomly select a proxy
        proxy = random.choice(self._proxy_list)
        
        # Validate proxy
        if not await self._proxy_manager.validate_proxy(proxy):
            self._proxy_list.remove(proxy)
            return await self.get_proxy()
        
        return proxy


class PriorityProxyStrategy:
    """Priority proxy selection strategy"""
    
    def __init__(self, proxy_manager: BaseProxyManager):
        self._proxy_manager = proxy_manager
        self._priority_proxies = []
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get proxy using priority strategy"""
        if not self._priority_proxies:
            # Load and prioritize proxies
            proxies = []
            for _ in range(10):
                proxy = await self._proxy_manager.get_proxy()
                if proxy and proxy not in proxies:
                    proxies.append(proxy)
                await self._proxy_manager.rotate_proxy()
            
            # Validate and sort proxies by speed
            valid_proxies = []
            for proxy in proxies:
                if await self._proxy_manager.validate_proxy(proxy):
                    valid_proxies.append(proxy)
            
            # Sort by speed (simplified - just return in any order)
            self._priority_proxies = valid_proxies
        
        if not self._priority_proxies:
            return None
        
        # Get highest priority proxy
        proxy = self._priority_proxies[0]
        
        # Validate proxy
        if not await self._proxy_manager.validate_proxy(proxy):
            self._priority_proxies.pop(0)
            return await self.get_proxy()
        
        return proxy