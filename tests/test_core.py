# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import pytest
from src.spiders.factory import CrawlerFactory
from src.storage.factory import StoreFactory
from src.monitoring.monitor import Monitor


class TestCrawlerFactory:
    """Test crawler factory"""
    
    def test_get_supported_platforms(self):
        """Test get supported platforms"""
        platforms = CrawlerFactory.get_supported_platforms()
        assert isinstance(platforms, dict)
        assert "xhs" in platforms
        assert "dy" in platforms
        assert "ks" in platforms
    
    def test_create_crawler(self):
        """Test create crawler"""
        crawler = CrawlerFactory.create_crawler("xhs")
        assert crawler is not None
        assert crawler.get_platform_name() == "Xiaohongshu"


class TestStoreFactory:
    """Test store factory"""
    
    async def test_create_store(self):
        """Test create store"""
        store = StoreFactory.create_store("file")
        await store.initialize()
        assert store is not None
        await store.close()


class TestMonitor:
    """Test monitor"""
    
    async def test_monitor(self):
        """Test monitor"""
        monitor = Monitor()
        await monitor.initialize()
        
        # Test log event
        await monitor.log_event("test", {"message": "test"})
        
        # Test log error
        try:
            raise Exception("Test error")
        except Exception as e:
            await monitor.log_error(e, {"context": "test"})
        
        # Test get stats
        stats = await monitor.get_stats()
        assert isinstance(stats, dict)
        
        # Test check health
        health = await monitor.check_health()
        assert isinstance(health, dict)
        assert "status" in health
        
        await monitor.cleanup()


if __name__ == "__main__":
    """Run tests"""
    asyncio.run(TestMonitor().test_monitor())
    asyncio.run(TestStoreFactory().test_create_store())
    
    test_factory = TestCrawlerFactory()
    test_factory.test_get_supported_platforms()
    test_factory.test_create_crawler()
    
    print("All tests passed!")