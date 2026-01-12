#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
from typing import Dict, Optional, Any, List
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase

from config import base_config


class MongoDB:
    """MongoDB implementation"""
    
    def __init__(self):
        """Initialize MongoDB"""
        self.client = None
        self.db = None
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            # Use MongoDB URI if provided
            if base_config.MONGODB_URI:
                self.client = MongoClient(base_config.MONGODB_URI)
            else:
                # Use default connection
                self.client = MongoClient('localhost', 27017)
            
            # Get database
            self.db = self.client[base_config.MONGODB_DB]
            
            # Test connection
            await asyncio.to_thread(lambda: self.client.server_info())
            self.connected = True
            print(f"[MongoDB] Connected to database: {base_config.MONGODB_DB}")
            return True
            
        except Exception as e:
            print(f"[MongoDB] Error connecting to database: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MongoDB"""
        try:
            if self.client:
                self.client.close()
                self.client = None
                self.db = None
                self.connected = False
                print("[MongoDB] Disconnected from database")
            return True
            
        except Exception as e:
            print(f"[MongoDB] Error disconnecting from database: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """Create MongoDB collections (equivalent to tables)"""
        try:
            # MongoDB creates collections automatically when first used
            # So we just need to ensure indexes are created
            await self._create_indexes()
            print("[MongoDB] Collections initialized successfully")
            return True
            
        except Exception as e:
            print(f"[MongoDB] Error initializing collections: {e}")
            return False
    
    async def _create_indexes(self):
        """Create MongoDB indexes"""
        # Create indexes for crawled_data collection
        crawled_data = self.db['crawled_data']
        await asyncio.to_thread(lambda: crawled_data.create_index('platform'))
        await asyncio.to_thread(lambda: crawled_data.create_index('created_at'))
        
        # Create indexes for tasks collection
        tasks = self.db['tasks']
        await asyncio.to_thread(lambda: tasks.create_index('task_id', unique=True))
        await asyncio.to_thread(lambda: tasks.create_index('status'))
        await asyncio.to_thread(lambda: tasks.create_index('platform'))
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Any]:
        """Insert data into MongoDB collection"""
        try:
            collection = self.db[table]
            result = await asyncio.to_thread(lambda: collection.insert_one(data))
            return result.inserted_id
            
        except Exception as e:
            print(f"[MongoDB] Error inserting data: {e}")
            return None
    
    async def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records into MongoDB collection"""
        if not data_list:
            return 0
        
        try:
            collection = self.db[table]
            result = await asyncio.to_thread(lambda: collection.insert_many(data_list))
            return len(result.inserted_ids)
            
        except Exception as e:
            print(f"[MongoDB] Error inserting multiple records: {e}")
            return 0
    
    async def select(self, table: str, conditions: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from MongoDB collection"""
        try:
            collection = self.db[table]
            
            # Prepare query
            query = conditions or {}
            
            # Execute query
            cursor = collection.find(query)
            
            # Apply limit and offset
            if limit:
                cursor = cursor.limit(limit)
            if offset:
                cursor = cursor.skip(offset)
            
            # Convert to list
            result = await asyncio.to_thread(lambda: list(cursor))
            
            # Convert ObjectId to string
            for item in result:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
            
            return result
            
        except Exception as e:
            print(f"[MongoDB] Error selecting data: {e}")
            return []
    
    async def update(self, table: str, data: Dict[str, Any], 
                    conditions: Optional[Dict[str, Any]] = None) -> int:
        """Update data in MongoDB collection"""
        try:
            collection = self.db[table]
            
            # Prepare update
            update_data = {"$set": data}
            
            # Execute update
            result = await asyncio.to_thread(
                lambda: collection.update_many(conditions or {}, update_data)
            )
            
            return result.modified_count
            
        except Exception as e:
            print(f"[MongoDB] Error updating data: {e}")
            return 0
    
    async def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Delete data from MongoDB collection"""
        try:
            collection = self.db[table]
            
            # Execute delete
            result = await asyncio.to_thread(
                lambda: collection.delete_many(conditions or {})
            )
            
            return result.deleted_count
            
        except Exception as e:
            print(f"[MongoDB] Error deleting data: {e}")
            return 0
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """Execute MongoDB command (equivalent to SQL query)"""
        try:
            # MongoDB uses command-based operations, not SQL
            # This is a simplified implementation
            print(f"[MongoDB] execute() called with query: {query}")
            return None
            
        except Exception as e:
            print(f"[MongoDB] Error executing command: {e}")
            return None