# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import httpx
from typing import List, Dict, Optional

from proxy.base_proxy import BaseProxyProvider


class KuaidlProxy(BaseProxyProvider):
    """Kuaidl proxy provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.api_url = "http://dev.kdlapi.com/api/getproxy"
    
    async def get_proxies(self, count: int) -> List[Dict[str, str]]:
        """Get proxies from Kuaidl"""
        proxies = []
        try:
            params = {
                "orderid": self.api_key,
                "num": count,
                "protocol": 1,  # HTTP
                "method": 1,  # GET
                "an_an": 1,
                "an_ha": 1,
                "sep": 1
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url, params=params)
                data = response.text
                
                # Parse response
                proxy_list = data.strip().split('\n')
                for proxy in proxy_list:
                    if proxy:
                        proxy_url = f"http://{proxy}"
                        proxies.append({
                            "http://": proxy_url,
                            "https://": proxy_url
                        })
        
        except Exception as e:
            print(f"Error getting proxies from Kuaidl: {e}")
        
        return proxies
    
    async def get_single_proxy(self) -> Optional[Dict[str, str]]:
        """Get a single proxy from Kuaidl"""
        proxies = await self.get_proxies(1)
        return proxies[0] if proxies else None
    
    def get_provider_name(self) -> str:
        """Get provider name"""
        return "Kuaidl Proxy"