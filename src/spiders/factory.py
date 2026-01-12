# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, Type, Optional, Any

from src.core.base.base_crawler import AbstractCrawler
from src.spiders.platforms.xhs.core import XiaoHongShuCrawler
from src.spiders.platforms.douyin.core import DouYinCrawler
from src.spiders.platforms.kuaishou.core import KuaishouCrawler


class CrawlerFactory:
    """Crawler factory for creating platform-specific crawlers"""
    
    # Crawler implementations mapping
    CRAWLERS: Dict[str, Type[AbstractCrawler]] = {
        # Chinese platforms
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        # Add other platforms here
    }
    
    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        """Create a crawler for the specified platform"""
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            supported = ", ".join(sorted(CrawlerFactory.CRAWLERS))
            raise ValueError(f"Invalid platform: {platform!r}. Supported: {supported}")
        return crawler_class()
    
    @staticmethod
    def get_supported_platforms() -> Dict[str, Dict[str, Any]]:
        """Get list of supported platforms with their features"""
        platforms = {}
        for platform_code, crawler_class in CrawlerFactory.CRAWLERS.items():
            try:
                crawler = crawler_class()
                platforms[platform_code] = {
                    "name": crawler.get_platform_name(),
                    "features": crawler.get_supported_features(),
                    "enabled": True
                }
            except Exception:
                platforms[platform_code] = {
                    "name": platform_code.capitalize(),
                    "features": [],
                    "enabled": False
                }
        return platforms
    
    @staticmethod
    def is_platform_supported(platform: str) -> bool:
        """Check if a platform is supported"""
        return platform in CrawlerFactory.CRAWLERS