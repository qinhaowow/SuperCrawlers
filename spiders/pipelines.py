# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import asyncio
from itemadapter import ItemAdapter
from typing import Dict, Any

from tools.async_file_writer import AsyncFileWriter
from database.db import insert, insert_many
from config import base_config


class SuperCrawlerPipeline:
    """
    Pipeline to save data from Scrapy to existing storage systems
    """
    
    def __init__(self):
        """
        Initialize the pipeline
        """
        self.items = []
        self.batch_size = 100
        self.file_writers = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        """
        Create pipeline instance from crawler
        """
        pipeline = cls()
        return pipeline
    
    def open_spider(self, spider):
        """
        Spider opened signal handler
        """
        spider.logger.info("SuperCrawlerPipeline opened")
    
    def close_spider(self, spider):
        """
        Spider closed signal handler
        """
        spider.logger.info("SuperCrawlerPipeline closed")
        
        # Process remaining items
        if self.items:
            self._process_batch(self.items, spider)
        
        # Cleanup file writers
        for writer in self.file_writers.values():
            # No cleanup needed for AsyncFileWriter
            pass
    
    def process_item(self, item, spider):
        """
        Process a single item
        """
        # Convert item to dictionary
        item_dict = dict(item)
        
        # Add to batch
        self.items.append(item_dict)
        
        # Process batch if it reaches size limit
        if len(self.items) >= self.batch_size:
            self._process_batch(self.items, spider)
            self.items = []
        
        return item
    
    def _process_batch(self, items, spider):
        """
        Process a batch of items
        """
        spider.logger.info(f"Processing batch of {len(items)} items")
        
        # Get platform from first item or use spider's platform
        platform = items[0].get('platform', spider.platform) if items else spider.platform
        
        # Save to storage based on configuration
        if base_config.SAVE_DATA_OPTION == "json":
            self._save_to_json(items, platform, spider)
        elif base_config.SAVE_DATA_OPTION == "csv":
            self._save_to_csv(items, platform, spider)
        elif base_config.SAVE_DATA_OPTION == "excel":
            self._save_to_excel(items, platform, spider)
        elif base_config.SAVE_DATA_OPTION in ["sqlite", "mysql", "mongodb"]:
            self._save_to_database(items, spider)
        else:
            # Default to JSON
            self._save_to_json(items, platform, spider)
    
    def _save_to_json(self, items, platform, spider):
        """
        Save items to JSON file
        """
        try:
            writer = self._get_file_writer(platform, "json")
            loop = asyncio.get_event_loop()
            file_path = loop.run_until_complete(writer.write_data(items))
            spider.logger.info(f"Saved {len(items)} items to JSON: {file_path}")
        except Exception as e:
            spider.logger.error(f"Error saving to JSON: {e}")
    
    def _save_to_csv(self, items, platform, spider):
        """
        Save items to CSV file
        """
        try:
            writer = self._get_file_writer(platform, "csv")
            loop = asyncio.get_event_loop()
            file_path = loop.run_until_complete(writer.write_data(items))
            spider.logger.info(f"Saved {len(items)} items to CSV: {file_path}")
        except Exception as e:
            spider.logger.error(f"Error saving to CSV: {e}")
    
    def _save_to_excel(self, items, platform, spider):
        """
        Save items to Excel file
        """
        try:
            writer = self._get_file_writer(platform, "excel")
            loop = asyncio.get_event_loop()
            file_path = loop.run_until_complete(writer.write_data(items))
            spider.logger.info(f"Saved {len(items)} items to Excel: {file_path}")
        except Exception as e:
            spider.logger.error(f"Error saving to Excel: {e}")
    
    def _save_to_database(self, items, spider):
        """
        Save items to database
        """
        try:
            loop = asyncio.get_event_loop()
            count = loop.run_until_complete(insert_many("crawled_data", items))
            spider.logger.info(f"Saved {count} items to database")
        except Exception as e:
            spider.logger.error(f"Error saving to database: {e}")
    
    def _get_file_writer(self, platform, file_type):
        """
        Get or create file writer for the given platform and file type
        """
        key = f"{platform}_{file_type}"
        if key not in self.file_writers:
            # Set save data option based on file type
            original_save_option = base_config.SAVE_DATA_OPTION
            if file_type == "json":
                base_config.SAVE_DATA_OPTION = "json"
            elif file_type == "csv":
                base_config.SAVE_DATA_OPTION = "csv"
            elif file_type == "excel":
                base_config.SAVE_DATA_OPTION = "excel"
            
            # Create file writer
            self.file_writers[key] = AsyncFileWriter(
                platform=platform,
                crawler_type="scrapy"
            )
            
            # Restore original save option
            base_config.SAVE_DATA_OPTION = original_save_option
        
        return self.file_writers[key]
