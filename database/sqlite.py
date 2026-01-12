#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import sqlite3
import json
import os
from typing import Dict, Optional, Any, List
from datetime import datetime

from database.db import Database
from config import base_config


class SQLiteDatabase(Database):
    """SQLite database implementation"""
    
    def __init__(self):
        """Initialize SQLite database"""
        super().__init__()
        self.db_path = os.path.join(base_config.DATA_DIR, "supercrawler.db")
        self.conn = None
    
    async def connect(self) -> bool:
        """Connect to SQLite database"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Connect to SQLite database
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            self.connected = True
            print(f"[SQLite] Connected to database: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"[SQLite] Error connecting to database: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from SQLite database"""
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                self.connected = False
                print("[SQLite] Disconnected from database")
            return True
            
        except Exception as e:
            print(f"[SQLite] Error disconnecting from database: {e}")
            return False
    
    async def create_tables(self) -> bool:
        """Create SQLite tables"""
        try:
            cursor = self.conn.cursor()
            
            # Create crawled_data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS crawled_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL DEFAULT NULL
                )
            ''')
            
            # Create tasks table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    crawler_type TEXT NOT NULL,
                    query TEXT DEFAULT NULL,
                    max_results INTEGER DEFAULT 100,
                    interval INTEGER DEFAULT NULL,
                    status TEXT DEFAULT 'pending',
                    execution_count INTEGER DEFAULT 0,
                    last_error TEXT DEFAULT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL DEFAULT NULL
                )
            ''')
            
            # Create indices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawled_data_platform ON crawled_data(platform)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_platform ON tasks(platform)')
            
            self.conn.commit()
            cursor.close()
            print("[SQLite] Tables created successfully")
            return True
            
        except Exception as e:
            print(f"[SQLite] Error creating tables: {e}")
            self.conn.rollback()
            return False
    
    async def insert(self, table: str, data: Dict[str, Any]) -> Optional[int]:
        """Insert data into SQLite table"""
        try:
            cursor = self.conn.cursor()
            
            # Convert dict values to JSON strings if needed
            processed_data = {}
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    processed_data[key] = json.dumps(value, ensure_ascii=False)
                else:
                    processed_data[key] = value
            
            # Prepare SQL statement
            columns = ", ".join(processed_data.keys())
            placeholders = ", ".join(["?"] * len(processed_data))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Execute SQL
            cursor.execute(sql, list(processed_data.values()))
            self.conn.commit()
            
            last_id = cursor.lastrowid
            cursor.close()
            return last_id
            
        except Exception as e:
            print(f"[SQLite] Error inserting data: {e}")
            self.conn.rollback()
            return None
    
    async def insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records into SQLite table"""
        if not data_list:
            return 0
        
        try:
            cursor = self.conn.cursor()
            
            # Process data
            processed_data = []
            for data in data_list:
                row = []
                for value in data.values():
                    if isinstance(value, (dict, list)):
                        row.append(json.dumps(value, ensure_ascii=False))
                    else:
                        row.append(value)
                processed_data.append(row)
            
            # Prepare SQL statement
            columns = ", ".join(data_list[0].keys())
            placeholders = ", ".join(["?"] * len(data_list[0]))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Execute SQL
            cursor.executemany(sql, processed_data)
            self.conn.commit()
            
            count = cursor.rowcount
            cursor.close()
            return count
            
        except Exception as e:
            print(f"[SQLite] Error inserting multiple records: {e}")
            self.conn.rollback()
            return 0
    
    async def select(self, table: str, conditions: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """Select data from SQLite table"""
        try:
            cursor = self.conn.cursor()
            
            # Prepare SQL statement
            sql = f"SELECT * FROM {table}"
            
            # Add conditions
            params = []
            if conditions:
                where_clause = []
                for key, value in conditions.items():
                    where_clause.append(f"{key} = ?")
                    params.append(value)
                sql += " WHERE " + " AND ".join(where_clause)
            
            # Add limit and offset
            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"
            
            # Execute SQL
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            result = []
            for row in rows:
                row_dict = dict(row)
                # Convert JSON strings back to objects
                for key, value in row_dict.items():
                    if isinstance(value, str):
                        try:
                            # Try to parse JSON
                            parsed = json.loads(value)
                            row_dict[key] = parsed
                        except json.JSONDecodeError:
                            pass
                result.append(row_dict)
            
            cursor.close()
            return result
            
        except Exception as e:
            print(f"[SQLite] Error selecting data: {e}")
            return []
    
    async def update(self, table: str, data: Dict[str, Any], 
                    conditions: Optional[Dict[str, Any]] = None) -> int:
        """Update data in SQLite table"""
        try:
            cursor = self.conn.cursor()
            
            # Process data
            processed_data = []
            set_clause = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    processed_data.append(json.dumps(value, ensure_ascii=False))
                else:
                    processed_data.append(value)
                set_clause.append(f"{key} = ?")
            
            # Prepare SQL statement
            sql = f"UPDATE {table} SET " + ", ".join(set_clause)
            
            # Add conditions
            if conditions:
                where_clause = []
                for key, value in conditions.items():
                    where_clause.append(f"{key} = ?")
                    processed_data.append(value)
                sql += " WHERE " + " AND ".join(where_clause)
            
            # Execute SQL
            cursor.execute(sql, processed_data)
            self.conn.commit()
            
            count = cursor.rowcount
            cursor.close()
            return count
            
        except Exception as e:
            print(f"[SQLite] Error updating data: {e}")
            self.conn.rollback()
            return 0
    
    async def delete(self, table: str, conditions: Optional[Dict[str, Any]] = None) -> int:
        """Delete data from SQLite table"""
        try:
            cursor = self.conn.cursor()
            
            # Prepare SQL statement
            sql = f"DELETE FROM {table}"
            
            # Add conditions
            params = []
            if conditions:
                where_clause = []
                for key, value in conditions.items():
                    where_clause.append(f"{key} = ?")
                    params.append(value)
                sql += " WHERE " + " AND ".join(where_clause)
            
            # Execute SQL
            cursor.execute(sql, params)
            self.conn.commit()
            
            count = cursor.rowcount
            cursor.close()
            return count
            
        except Exception as e:
            print(f"[SQLite] Error deleting data: {e}")
            self.conn.rollback()
            return 0
    
    async def execute(self, query: str, params: Optional[List[Any]] = None) -> Any:
        """Execute raw SQL query"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, params or [])
            self.conn.commit()
            
            # Return result if it's a SELECT query
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append(dict(row))
                return result
            else:
                return cursor.rowcount
                
        except Exception as e:
            print(f"[SQLite] Error executing query: {e}")
            self.conn.rollback()
            return None