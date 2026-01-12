# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


class BaseProxyProvider(ABC):
    """Base proxy provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def get_proxies(self, count: int) -> List[Dict[str, str]]:
        """Get proxies from provider"""
        pass
    
    @abstractmethod
    async def get_single_proxy(self) -> Optional[Dict[str, str]]:
        """Get a single proxy"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass