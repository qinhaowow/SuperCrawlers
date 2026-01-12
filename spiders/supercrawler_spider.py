# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from typing import Dict, List, Optional, Any
import asyncio

from main import CrawlerFactory
from items import SupercrawleItem
from config import base_config


class SuperCrawlerSpider(scrapy.Spider):
    """
    Scrapy spider that integrates with existing platform crawlers
    """
    name = "supercrawler"
    
    def __init__(self, platform: str = "xhs", query: str = "", max_results: int = 100, **kwargs):
        """
        Initialize the spider
        :param platform: Target platform
        :param query: Search query
        :param max_results: Maximum number of results
        """
        super().__init__(**kwargs)
        self.platform = platform
        self.query = query
        self.max_results = max_results
        self.crawler_instance = None
    
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        """
        Create spider instance from crawler
        """
        spider = super(SuperCrawlerSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider
    
    def spider_opened(self, spider):
        """
        Spider opened signal handler
        """
        self.logger.info(f"Spider opened: {spider.name}")
        self.logger.info(f"Target platform: {self.platform}")
        self.logger.info(f"Search query: {self.query}")
        self.logger.info(f"Max results: {self.max_results}")
        
        # Create crawler instance
        try:
            self.crawler_instance = CrawlerFactory.create_crawler(platform=self.platform)
            self.logger.info(f"Created crawler: {self.crawler_instance.get_platform_name()}")
            self.logger.info(f"Supported features: {', '.join(self.crawler_instance.get_supported_features())}")
        except Exception as e:
            self.logger.error(f"Error creating crawler: {e}")
            raise
    
    def spider_closed(self, spider):
        """
        Spider closed signal handler
        """
        self.logger.info(f"Spider closed: {spider.name}")
    
    def start_requests(self):
        """
        Start requests - this will trigger the crawling process
        """
        # We'll use a dummy request to start the async crawling process
        # since Scrapy is synchronous but our crawlers are async
        yield scrapy.Request(url="http://example.com", callback=self.parse)
    
    def parse(self, response):
        """
        Parse the dummy response and start the async crawling process
        """
        # Run the async crawling process
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(self.crawl_async())
        
        # Process the results
        for result in results:
            yield self.process_result(result)
    
    async def crawl_async(self):
        """
        Async crawling process using the existing crawler
        """
        results = []
        
        try:
            # Start the crawler
            await self.crawler_instance.start()
            
            # Search for content if query is provided
            if self.query:
                self.logger.info(f"Searching for: {self.query}")
                search_results = await self.crawler_instance.search(
                    query=self.query,
                    max_results=self.max_results
                )
                results.extend(search_results)
                
                # For each search result, get details and comments
                for item in search_results[:5]:  # Limit to first 5 items for demonstration
                    if "id" in item:
                        content_id = item["id"]
                        
                        # Get content details
                        try:
                            details = await self.crawler_instance.get_content_detail(content_id)
                            if details:
                                results.append(details)
                        except Exception as e:
                            self.logger.error(f"Error getting content details: {e}")
                        
                        # Get comments
                        try:
                            comments = await self.crawler_instance.get_comments(content_id)
                            if comments:
                                results.extend(comments)
                        except Exception as e:
                            self.logger.error(f"Error getting comments: {e}")
        
        except Exception as e:
            self.logger.error(f"Error during crawling: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        finally:
            # Cleanup
            if hasattr(self.crawler_instance, "browser_context") and self.crawler_instance.browser_context:
                try:
                    await self.crawler_instance.browser_context.close()
                except Exception as e:
                    self.logger.error(f"Error closing browser context: {e}")
        
        return results
    
    def process_result(self, result):
        """
        Process a result into a Scrapy item
        """
        item = SupercrawleItem()
        
        # Extract common fields
        if isinstance(result, dict):
            # Set fields based on result type
            if "id" in result:
                item["id"] = result["id"]
            
            if "title" in result:
                item["title"] = result["title"]
            
            if "content" in result:
                item["content"] = result["content"]
            
            if "author" in result:
                item["author"] = result["author"]
            
            if "platform" not in result:
                item["platform"] = self.platform
            
            if "url" in result:
                item["url"] = result["url"]
            
            if "timestamp" in result:
                item["timestamp"] = result["timestamp"]
            
            if "type" not in result:
                # Determine type based on fields
                if "comment" in result:
                    item["type"] = "comment"
                elif "author" in result and "content" in result:
                    item["type"] = "content"
                else:
                    item["type"] = "unknown"
            else:
                item["type"] = result["type"]
            
            # Add all other fields
            for key, value in result.items():
                if key not in item:
                    item[key] = value
        
        return item


def run_spider(platform: str, query: str, max_results: int = 100):
    """
    Run the spider with the given parameters
    """
    settings = get_project_settings()
    
    process = CrawlerProcess(settings)
    process.crawl(
        SuperCrawlerSpider,
        platform=platform,
        query=query,
        max_results=max_results
    )
    
    process.start()