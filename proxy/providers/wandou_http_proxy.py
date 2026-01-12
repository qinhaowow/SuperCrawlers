# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import httpx
from typing import List, Dict, Optional

from proxy.base_proxy import BaseProxyProvider


class WandouHTTPProxy(BaseProxyProvider):
    """Wandou HTTP proxy provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.api_url = "http://api.wandouip.com/api/ip"
    
    async def get_proxies(self, count: int) -> List[Dict[str, str]]:
        """Get proxies from Wandou"""
        proxies = []
        try:
            params = {
                "key": self.api_key,
                "num": count,
                "type": "http",
                "protocol": "http",
                "format": "json",
                "sep": 1
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                data = response.json()
                
                if data.get("code") == 200:
                    for ip_info in data.get("data", []):
                        ip = ip_info.get("ip")
                        port = ip_info.get("port")
                        if ip and port:
                            proxy_url = f"http://{ip}:{port}"
                            proxies.append({
                                "http://": proxy_url,
                                "https://": proxy_url
                            })
        
        except Exception as e:
            print(f"Error getting proxies from Wandou: {e}")
        
        return proxies
    
    async def get_single_proxy(self) -> Optional[Dict[str, str]]:
        """Get a single proxy from Wandou"""
        proxies = await self.get_proxies(1)
        return proxies[0] if proxies else None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Wandou HTTP Proxy"