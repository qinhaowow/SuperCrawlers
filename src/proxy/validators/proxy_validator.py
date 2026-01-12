# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import aiohttp
from typing import Dict, Optional, Any


class ProxyValidator:
    """Proxy validator"""
    
    @staticmethod
    async def validate_proxy(proxy: Dict[str, str], timeout: int = 5) -> bool:
        """Validate a proxy"""
        proxy_url = proxy.get('http') or proxy.get('https')
        if not proxy_url:
            return False
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get('https://www.baidu.com', proxy=proxy_url) as response:
                    if response.status == 200:
                        return True
        except Exception:
            pass
        
        return False
    
    @staticmethod
    async def validate_proxy_speed(proxy: Dict[str, str], timeout: int = 10) -> Optional[float]:
        """Validate proxy speed and return response time in seconds"""
        proxy_url = proxy.get('http') or proxy.get('https')
        if not proxy_url:
            return None
        
        try:
            import time
            start_time = time.time()
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
                async with session.get('https://www.baidu.com', proxy=proxy_url) as response:
                    if response.status == 200:
                        end_time = time.time()
                        return end_time - start_time
        except Exception:
            pass
        
        return None
    
    @staticmethod
    async def validate_proxy_anonymous(proxy: Dict[str, str]) -> bool:
        """Validate if proxy is anonymous"""
        proxy_url = proxy.get('http') or proxy.get('https')
        if not proxy_url:
            return False
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.ipify.org', proxy=proxy_url) as response:
                    if response.status == 200:
                        proxy_ip = await response.text()
                        
                        # Check if the IP returned is different from our original IP
                        # This is a basic check and may not work for all cases
                        async with aiohttp.ClientSession() as session2:
                            async with session2.get('https://api.ipify.org') as response2:
                                if response2.status == 200:
                                    original_ip = await response2.text()
                                    return proxy_ip != original_ip
        except Exception:
            pass
        
        return False