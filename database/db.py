#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import os
from typing import Dict, Optional, Any, List, Union
from config import base_config


class Database:
    """Base database interface"""
    
    def __init__(self):
        """Initialize database"""
        self.connected = False
    
    async def connect(self) -> bool:
        """Connect to database"""
        raise NotImplementedError
    
    async def disconnect(self) -> bool:
        """Disconnect from database"""
        raise NotImplementedError
    
    async def create_tables(self) -> bool:
        """Create database tables"""
        raise NotImplementedError
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[Any]:
        """Insert data into table"""
        raise NotImplementedError
    
    async def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records into table"""
        raise NotImplementedError
    
    async def select(self, table: str, conditions: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from table"""
        raise NotImplementedError
    
    async def update(self, table: str, data: Dict[str, Any], 
                    conditions: Optional[Dict[str, Any]] = None) -> int:
        """Update data in table"""
        raise NotImplementedError
    
    async def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Delete data from table"""
        raise NotImplementedError
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """Execute raw SQL query"""
        raise NotImplementedError


# Database instance
_db_instance: Optional[Database] = None


async def init_db(db_type: str) -> bool:
    """Initialize database"""
    global _db_instance
    
    print(f"[Database] Initializing {db_type} database...")
    
    try:
        if db_type == "sqlite":
            from database.sqlite import SQLiteDatabase
            _db_instance = SQLiteDatabase()
        elif db_type == "mysql":
            from database.mysql import MySQLDatabase
            _db_instance = MySQLDatabase()
        elif db_type == "mongodb":
            from database.mongodb import MongoDB
            _db_instance = MongoDB()
        else:
            print(f"[Database] Unsupported database type: {db_type}")
            return False
        
        # Connect to database
        connected = await _db_instance.connect()
        if not connected:
            print(f"[Database] Failed to connect to {db_type} database")
            return False
        
        # Create tables
        created = await _db_instance.create_tables()
        if not created:
            print(f"[Database] Failed to create tables for {db_type} database")
            return False
        
        print(f"[Database] {db_type} database initialized successfully")
        return True
        
    except Exception as e:
        print(f"[Database] Error initializing {db_type} database: {e}")
        import traceback
        traceback.print_exc()
        return False


async def close() -> bool:
    """Close database connection"""
    global _db_instance
    
    if _db_instance:
        try:
            result = await _db_instance.disconnect()
            _db_instance = None
            print("[Database] Database connection closed")
            return result
        except Exception as e:
            print(f"[Database] Error closing database connection: {e}")
            return False
    
    return True


def get_db() -> Optional[Database]:
    """Get database instance"""
    global _db_instance
    return _db_instance


async def insert(table: str, data: Dict[str, Any]) -> Optional[Any]:
    """Insert data into table"""
    db = get_db()
    if db:
        return await db.insert(table, data)
    raise Exception("Database not initialized")


async def insert_many(table: str, data_list: List[Dict[str, Any]]) -> int:
    """Insert multiple records into table"""
    db = get_db()
    if db:
        return await db.insert_many(table, data_list)
    raise Exception("Database not initialized")


async def select(table: str, conditions: Optional[Dict[str, Any]] = None, 
                limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
    """Select data from table"""
    db = get_db()
    if db:
        return await db.select(table, conditions, limit, offset)
    raise Exception("Database not initialized")


async def update(table: str, data: Dict[str, Any], 
                conditions: Optional[Dict[str, Any]] = None) -> int:
    """Update data in table"""
    db = get_db()
    if db:
        return await db.update(table, data, conditions)
    raise Exception("Database not initialized")


async def delete(table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
    """Delete data from table"""
    db = get_db()
    if db:
        return await db.delete(table, conditions)
    raise Exception("Database not initialized")


async def execute(query: str, params: Optional[List[Any]] = None) -> Any:
    """Execute raw SQL query"""
    db = get_db()
    if db:
        return await db.execute(query, params)
    raise Exception("Database not initialized")


async def save_crawled_data(platform: str, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> int:
    """Save crawled data to database"""
    if isinstance(data, dict):
        data = [data]
    
    if not data:
        return 0
    
    # Prepare data for insertion
    records = []
    for item in data:
        record = {
            "platform": platform,
            "data": item,
            "created_at": asyncio.get_event_loop().time()
        }
        records.append(record)
    
    # Insert into database
    try:
        return await insert_many("crawled_data", records)
    except Exception as e:
        print(f"[Database] Error saving crawled data: {e}")
        return 0


async def get_crawled_data(platform: Optional[str] = None, 
                          limit: Optional[int] = 100, 
                          offset: Optional[int] = 0) -> List[Dict[str, Any]]:
    """Get crawled data from database"""
    conditions = {}
    if platform:
        conditions["platform"] = platform
    
    try:
        return await select("crawled_data", conditions, limit, offset)
    except Exception as e:
        print(f"[Database] Error getting crawled data: {e}")
        return []