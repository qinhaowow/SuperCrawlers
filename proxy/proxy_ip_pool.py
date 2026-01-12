# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any
import asyncio
import random
import httpx


class AbstractProxyManager(ABC):
    """Abstract proxy manager"""
    
    @abstractmethod
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a proxy"""
        pass
    
    @abstractmethod
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """Validate a proxy"""
        pass
    
    @abstractmethod
    async def rotate_proxy(self):
        """Rotate to next proxy"""
        pass
    
    @abstractmethod
    async def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        pass


class ProxyManager(AbstractProxyManager):
    """Proxy manager implementation"""
    
    def __init__(self, provider: str = "none", api_key: Optional[str] = None, pool_size: int = 50):
        self.provider = provider
        self.api_key = api_key
        self.pool_size = pool_size
        self.proxy_pool: List[Dict[str, str]] = []
        self.valid_proxies: List[Dict[str, str]] = []
        self.current_proxy_index = 0
        self.stats = {
            "total_proxies": 0,
            "valid_proxies": 0,
            "invalid_proxies": 0,
            "proxy_usage": 0,
            "last_update": None
        }
    
    async def initialize(self):
        """Initialize proxy manager"""
        await self._load_proxies()
        await self._validate_proxies()
    
    async def _load_proxies(self):
        """Load proxies from provider"""
        if self.provider == "none":
            self.proxy_pool = []
            return
        
        provider_class = None
        if self.provider == "wandou":
            from proxy.providers.wandou_http_proxy import WandouHTTPProxy
            provider_class = WandouHTTPProxy
        elif self.provider == "kuaidl":
            from proxy.providers.kuaidl_proxy import KuaidlProxy
            provider_class = KuaidlProxy
        elif self.provider == "jishu":
            from proxy.providers.jishu_http_proxy import JishuHTTPProxy
            provider_class = JishuHTTPProxy
        
        if provider_class:
            provider = provider_class(self.api_key)
            self.proxy_pool = await provider.get_proxies(self.pool_size)
            self.stats["total_proxies"] = len(self.proxy_pool)
            self.stats["last_update"] = asyncio.get_event_loop().time()
    
    async def _validate_proxies(self):
        """Validate proxies in pool"""
        tasks = []
        for proxy in self.proxy_pool:
            tasks.append(self.validate_proxy(proxy))
        
        results = await asyncio.gather(*tasks)
        self.valid_proxies = [proxy for proxy, valid in zip(self.proxy_pool, results) if valid]
        self.stats["valid_proxies"] = len(self.valid_proxies)
        self.stats["invalid_proxies"] = len(self.proxy_pool) - len(self.valid_proxies)
    
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a proxy"""
        if not self.valid_proxies:
            await self.initialize()
        
        if not self.valid_proxies:
            return None
        
        # Rotate proxy
        proxy = self.valid_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.valid_proxies)
        self.stats["proxy_usage"] += 1
        
        return proxy
    
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """Validate a proxy"""
        try:
            async with httpx.AsyncClient(
                proxies=proxy,
                timeout=10.0
            ) as client:
                response = await client.get("https://www.baidu.com", timeout=10.0)
                return response.status_code == 200
        except Exception:
            return False
    
    async def rotate_proxy(self):
        """Rotate to next proxy"""
        if self.valid_proxies:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.valid_proxies)
    
    async def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy statistics"""
        return self.stats
    
    async def refresh_proxies(self):
        """Refresh proxy pool"""
        await self._load_proxies()
        await self._validate_proxies()
        return len(self.valid_proxies)