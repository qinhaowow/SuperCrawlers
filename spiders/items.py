#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import scrapy


class SupercrawlerItem(scrapy.Item):
    """SuperCrawler item for scraped data"""
    # Basic fields
    platform = scrapy.Field()
    content_id = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()
    author_id = scrapy.Field()
    publish_time = scrapy.Field()
    likes = scrapy.Field()
    comments = scrapy.Field()
    shares = scrapy.Field()
    views = scrapy.Field()
    url = scrapy.Field()
    
    # Additional fields for different platforms
    tags = scrapy.Field()
    categories = scrapy.Field()
    media_urls = scrapy.Field()  # For images, videos, etc.
    location = scrapy.Field()
    hashtags = scrapy.Field()
    
    # Metadata
    crawled_at = scrapy.Field()
    spider_name = scrapy.Field()
    crawl_type = scrapy.Field()  # search, detail, creator
    
    # Error handling
    error = scrapy.Field()
