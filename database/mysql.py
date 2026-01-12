#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import json
from typing import Dict, Optional, Any, List

import aiomysql

from database.db import Database
from config import base_config


class MySQLDatabase(Database):
    """MySQL database implementation"""
    
    def __init__(self):
        """Initialize MySQL database"""
        super().__init__()
        self.pool = None
    
    async def connect(self) -> bool:
        """Connect to MySQL database"""
        try:
            # Create connection pool
            self.pool = await aiomysql.create_pool(
                host=base_config.DB_HOST,
                port=base_config.DB_PORT,
                user=base_config.DB_USER,
                password=base_config.DB_PASSWORD,
                db=base_config.DB_NAME,
                charset='utf8mb4',
                cursorclass=aiomysql.DictCursor,
                autocommit=False
            )
            
            self.connected = True
            print(f"[MySQL] Connected to database: {base_config.DB_HOST}:{base_config.DB_PORT}/{base_config.DB_NAME}")
            return True
            
        except Exception as e:
            print(f"[MySQL] Error connecting to database: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from MySQL database"""
        try:
            if self.pool:
                self.pool.close()
                await self.pool.wait_closed()
                self.pool = None
                self.connected = False
                print("[MySQL] Disconnected from database")
            return True
            
        except Exception as e:
            print(f"[MySQL] Error disconnecting from database: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """Create MySQL tables"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Create crawled_data table
                    await cursor.execute('''
                        CREATE TABLE IF NOT EXISTS crawled_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            platform VARCHAR(50) NOT NULL,
                            data JSON NOT NULL,
                            created_at DOUBLE NOT NULL,
                            updated_at DOUBLE DEFAULT NULL,
                            INDEX idx_platform (platform)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    ''')
                    
                    # Create tasks table
                    await cursor.execute('''
                        CREATE TABLE IF NOT EXISTS tasks (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            task_id VARCHAR(100) NOT NULL UNIQUE,
                            name VARCHAR(255) NOT NULL,
                            platform VARCHAR(50) NOT NULL,
                            crawler_type VARCHAR(50) NOT NULL,
                            query TEXT DEFAULT NULL,
                            max_results INT DEFAULT 100,
                            interval INT DEFAULT NULL,
                            status VARCHAR(20) DEFAULT 'pending',
                            execution_count INT DEFAULT 0,
                            last_error TEXT DEFAULT NULL,
                            created_at DOUBLE NOT NULL,
                            updated_at DOUBLE DEFAULT NULL,
                            INDEX idx_status (status),
                            INDEX idx_platform (platform)
                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                    ''')
                
                await conn.commit()
                print("[MySQL] Tables created successfully")
                return True
                
        except Exception as e:
            print(f"[MySQL] Error creating tables: {e}")
            return False
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert data into MySQL table"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Prepare SQL statement
                    columns = ", ".join(data.keys())
                    placeholders = ", ".join(["%s"] * len(data))
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    
                    # Execute SQL
                    await cursor.execute(sql, list(data.values()))
                    await conn.commit()
                    
                    return cursor.lastrowid
                    
        except Exception as e:
            print(f"[MySQL] Error inserting data: {e}")
            return None
    
    async def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records into MySQL table"""
        if not data_list:
            return 0
        
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Prepare SQL statement
                    columns = ", ".join(data_list[0].keys())
                    placeholders = ", ".join(["%s"] * len(data_list[0]))
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                    
                    # Prepare data
                    values = []
                    for data in data_list:
                        values.append(list(data.values()))
                    
                    # Execute SQL
                    await cursor.executemany(sql, values)
                    await conn.commit()
                    
                    return cursor.rowcount
                    
        except Exception as e:
            print(f"[MySQL] Error inserting multiple records: {e}")
            return 0
    
    async def select(self, table: str, conditions: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from MySQL table"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Prepare SQL statement
                    sql = f"SELECT * FROM {table}"
                    
                    # Add conditions
                    params = []
                    if conditions:
                        where_clause = []
                        for key, value in conditions.items():
                            where_clause.append(f"{key} = %s")
                            params.append(value)
                        sql += " WHERE " + " AND ".join(where_clause)
                    
                    # Add limit and offset
                    if limit:
                        sql += f" LIMIT {limit}"
                        if offset:
                            sql += f" OFFSET {offset}"
                    
                    # Execute SQL
                    await cursor.execute(sql, params)
                    rows = await cursor.fetchall()
                    
                    return rows
                    
        except Exception as e:
            print(f"[MySQL] Error selecting data: {e}")
            return []
    
    async def update(self, table: str, data: Dict[str, Any], 
                    conditions: Optional[Dict[str, Any]] = None) -> int:
        """Update data in MySQL table"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Prepare SQL statement
                    set_clause = []
                    params = []
                    for key, value in data.items():
                        set_clause.append(f"{key} = %s")
                        params.append(value)
                    
                    sql = f"UPDATE {table} SET " + ", ".join(set_clause)
                    
                    # Add conditions
                    if conditions:
                        where_clause = []
                        for key, value in conditions.items():
                            where_clause.append(f"{key} = %s")
                            params.append(value)
                        sql += " WHERE " + " AND ".join(where_clause)
                    
                    # Execute SQL
                    await cursor.execute(sql, params)
                    await conn.commit()
                    
                    return cursor.rowcount
                    
        except Exception as e:
            print(f"[MySQL] Error updating data: {e}")
            return 0
    
    async def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Delete data from MySQL table"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    # Prepare SQL statement
                    sql = f"DELETE FROM {table}"
                    
                    # Add conditions
                    params = []
                    if conditions:
                        where_clause = []
                        for key, value in conditions.items():
                            where_clause.append(f"{key} = %s")
                            params.append(value)
                        sql += " WHERE " + " AND ".join(where_clause)
                    
                    # Execute SQL
                    await cursor.execute(sql, params)
                    await conn.commit()
                    
                    return cursor.rowcount
                    
        except Exception as e:
            print(f"[MySQL] Error deleting data: {e}")
            return 0
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """Execute raw SQL query"""
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, params or [])
                    await conn.commit()
                    
                    # Return result if it's a SELECT query
                    if query.strip().upper().startswith("SELECT"):
                        return await cursor.fetchall()
                    else:
                        return cursor.rowcount
                        
        except Exception as e:
            print(f"[MySQL] Error executing query: {e}")
            return None