#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from scrapy import signals
import time

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SupercrawlerSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.
        spider.logger.debug(f"Processing spider input for URL: {response.url}")
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        spider.logger.error(f"Spider exception: {exception}")
        # Return None to let other middleware handle the exception
        return None

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
        spider.start_time = time.time()

    def spider_closed(self, spider):
        runtime = time.time() - getattr(spider, 'start_time', time.time())
        spider.logger.info(f"Spider closed: {spider.name}, runtime: {runtime:.2f}s")


class SupercrawlerDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.
        spider.logger.debug(f"Processing request: {request.url}")
        
        # Add custom headers if needed
        request.headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.
        spider.logger.debug(f"Processing response: {response.url}, status: {response.status}")
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.
        spider.logger.error(f"Download exception for {request.url}: {exception}")
        
        # Return None to let other middleware handle the exception
        return None

    def spider_opened(self, spider):
        spider.logger.info(f"Spider opened: {spider.name}")
