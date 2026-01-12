# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import aiohttp
from typing import Dict, Optional, Any, List

from src.proxy.manager import BaseProxyManager


class FileProxyProvider(BaseProxyManager):
    """File proxy provider"""
    
    def __init__(self, proxy_file: str = "./proxies.txt"):
        super().__init__()
        self._proxy_file = proxy_file
    
    async def _load_proxies(self):
        """Load proxies from file"""
        try:
            with open(self._proxy_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    proxy = {
                        'http': f'http://{line}',
                        'https': f'http://{line}'
                    }
                    self._proxies.append(proxy)
        except Exception as e:
            print(f"Error loading proxies from file: {e}")


class ApiProxyProvider(BaseProxyManager):
    """API proxy provider"""
    
    def __init__(self, api_url: str, api_key: str = None):
        super().__init__()
        self._api_url = api_url
        self._api_key = api_key
    
    async def _load_proxies(self):
        """Load proxies from API"""
        try:
            headers = {}
            if self._api_key:
                headers['Authorization'] = f'Bearer {self._api_key}'
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self._api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        proxies = data.get('proxies', [])
                        
                        for proxy in proxies:
                            proxy_url = proxy.get('url') or f"{proxy.get('ip')}:{proxy.get('port')}"
                            if proxy_url:
                                proxy_dict = {
                                    'http': f'http://{proxy_url}',
                                    'https': f'http://{proxy_url}'
                                }
                                self._proxies.append(proxy_dict)
        except Exception as e:
            print(f"Error loading proxies from API: {e}")


class FreeProxyProvider(BaseProxyManager):
    """Free proxy provider"""
    
    def __init__(self):
        super().__init__()
        self._free_proxy_urls = [
            'https://www.free-proxy-list.net/',
            'https://free-proxy-list.com/',
            'https://proxy-daily.com/'
        ]
    
    async def _load_proxies(self):
        """Load proxies from free sources"""
        try:
            async with aiohttp.ClientSession() as session:
                for url in self._free_proxy_urls:
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                html = await response.text()
                                # Simple parsing to extract proxies
                                # Note: This is a basic implementation and may need to be adjusted
                                # based on the actual HTML structure of the proxy sites
                                import re
                                proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', html)
                                
                                for proxy in proxies:
                                    proxy_dict = {
                                        'http': f'http://{proxy}',
                                        'https': f'http://{proxy}'
                                    }
                                    if proxy_dict not in self._proxies:
                                        self._proxies.append(proxy_dict)
                    except Exception as e:
                        print(f"Error fetching proxies from {url}: {e}")
        except Exception as e:
            print(f"Error loading free proxies: {e}")