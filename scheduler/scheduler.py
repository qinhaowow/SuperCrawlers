#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import time
import os
from typing import Dict, Optional, List, Any, Callable
import json
from datetime import datetime, timedelta
import threading

from config import base_config
from main import CrawlerFactory


class Task:
    """Scheduled task"""
    
    def __init__(self, 
                 task_id: str,
                 name: str,
                 platform: str,
                 crawler_type: str,
                 query: Optional[str] = None,
                 max_results: int = 100,
                 interval: Optional[int] = None,  # seconds
                 start_time: Optional[datetime] = None):
        """Initialize task"""
        self.task_id = task_id
        self.name = name
        self.platform = platform
        self.crawler_type = crawler_type
        self.query = query
        self.max_results = max_results
        self.interval = interval
        self.start_time = start_time or datetime.now()
        self.last_executed: Optional[datetime] = None
        self.next_execution: Optional[datetime] = None
        self.status = "pending"  # pending, running, completed, failed, paused
        self.execution_count = 0
        self.last_error: Optional[str] = None
        
        self._calculate_next_execution()
    
    def _calculate_next_execution(self):
        """Calculate next execution time"""
        if self.interval:
            if self.last_executed:
                self.next_execution = self.last_executed + timedelta(seconds=self.interval)
            else:
                self.next_execution = self.start_time
        else:
            self.next_execution = self.start_time
    
    def should_execute(self) -> bool:
        """Check if task should be executed"""
        return self.status == "pending" and self.next_execution and datetime.now() >= self.next_execution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "platform": self.platform,
            "crawler_type": self.crawler_type,
            "query": self.query,
            "max_results": self.max_results,
            "interval": self.interval,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "next_execution": self.next_execution.isoformat() if self.next_execution else None,
            "status": self.status,
            "execution_count": self.execution_count,
            "last_error": self.last_error
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary"""
        task = cls(
            task_id=data["task_id"],
            name=data["name"],
            platform=data["platform"],
            crawler_type=data["crawler_type"],
            query=data.get("query"),
            max_results=data.get("max_results", 100),
            interval=data.get("interval"),
            start_time=datetime.fromisoformat(data["start_time"]) if data.get("start_time") else None
        )
        task.last_executed = datetime.fromisoformat(data["last_executed"]) if data.get("last_executed") else None
        task.next_execution = datetime.fromisoformat(data["next_execution"]) if data.get("next_execution") else None
        task.status = data.get("status", "pending")
        task.execution_count = data.get("execution_count", 0)
        task.last_error = data.get("last_error")
        return task


class Scheduler:
    """Task scheduler for SuperCrawler"""
    
    def __init__(self):
        """Initialize scheduler"""
        self.tasks: Dict[str, Task] = {}
        self.scheduling_task: Optional[asyncio.Task] = None
        self.running = False
        self.task_file = os.path.join(base_config.DATA_DIR, "scheduled_tasks.json")
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.task_file), exist_ok=True)
        
        # Load tasks from file
        self._load_tasks()
    
    async def initialize(self):
        """Initialize scheduler"""
        self.running = True
        self.scheduling_task = asyncio.create_task(self._scheduling_loop())
        print("[Scheduler] Initialized task scheduler")
    
    async def cleanup(self):
        """Cleanup scheduler resources"""
        self.running = False
        if self.scheduling_task:
            try:
                self.scheduling_task.cancel()
                await asyncio.wait([self.scheduling_task], timeout=5.0)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"[Scheduler] Error cleaning up: {e}")
        self._save_tasks()
        print("[Scheduler] Task scheduler stopped")
    
    async def _scheduling_loop(self):
        """Main scheduling loop"""
        while self.running:
            try:
                await self._check_tasks()
                await asyncio.sleep(base_config.SCHEDULER_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Scheduler] Error in scheduling loop: {e}")
                await asyncio.sleep(1)
    
    async def _check_tasks(self):
        """Check and execute pending tasks"""
        for task_id, task in list(self.tasks.items()):
            if task.should_execute():
                await self._execute_task(task)
    
    async def _execute_task(self, task: Task):
        """Execute task"""
        print(f"[Scheduler] Executing task: {task.name} (ID: {task.task_id})")
        task.status = "running"
        
        try:
            # Create crawler and execute task
            crawler = CrawlerFactory.create_crawler(platform=task.platform)
            
            # Execute based on crawler type
            if task.crawler_type == "search" and task.query:
                await crawler.search(query=task.query, max_results=task.max_results)
            elif task.crawler_type == "detail":
                # Detail mode would require specific content IDs
                # For now, just log that it's not implemented
                print(f"[Scheduler] Detail mode not implemented for task: {task.name}")
            elif task.crawler_type == "creator":
                # Creator mode would require specific creator IDs
                # For now, just log that it's not implemented
                print(f"[Scheduler] Creator mode not implemented for task: {task.name}")
            
            task.status = "completed"
            task.last_executed = datetime.now()
            task.execution_count += 1
            task.last_error = None
            
            # Calculate next execution if it's a recurring task
            if task.interval:
                task.status = "pending"
                task._calculate_next_execution()
            else:
                task.status = "completed"
            
            print(f"[Scheduler] Task completed: {task.name}")
            
        except Exception as e:
            task.status = "failed"
            task.last_error = str(e)
            print(f"[Scheduler] Task failed: {task.name} - {e}")
        
        finally:
            self._save_tasks()
    
    def add_task(self, task: Task):
        """Add task to scheduler"""
        self.tasks[task.task_id] = task
        self._save_tasks()
        print(f"[Scheduler] Added task: {task.name} (ID: {task.task_id})")
    
    def remove_task(self, task_id: str):
        """Remove task from scheduler"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            print(f"[Scheduler] Removed task: {task_id}")
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return list(self.tasks.values())
    
    def pause_task(self, task_id: str):
        """Pause task"""
        task = self.get_task(task_id)
        if task:
            task.status = "paused"
            self._save_tasks()
            print(f"[Scheduler] Paused task: {task.name}")
    
    def resume_task(self, task_id: str):
        """Resume task"""
        task = self.get_task(task_id)
        if task:
            task.status = "pending"
            task._calculate_next_execution()
            self._save_tasks()
            print(f"[Scheduler] Resumed task: {task.name}")
    
    def _save_tasks(self):
        """Save tasks to file"""
        try:
            tasks_data = [task.to_dict() for task in self.tasks.values()]
            with open(self.task_file, "w", encoding="utf-8") as f:
                json.dump(tasks_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Scheduler] Error saving tasks: {e}")
    
    def _load_tasks(self):
        """Load tasks from file"""
        try:
            if os.path.exists(self.task_file):
                with open(self.task_file, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)
                    for task_data in tasks_data:
                        task = Task.from_dict(task_data)
                        self.tasks[task.task_id] = task
                print(f"[Scheduler] Loaded {len(self.tasks)} tasks from file")
        except Exception as e:
            print(f"[Scheduler] Error loading tasks: {e}")
    
    async def create_task(self, 
                         name: str,
                         platform: str,
                         crawler_type: str,
                         query: Optional[str] = None,
                         max_results: int = 100,
                         interval: Optional[int] = None,
                         start_time: Optional[datetime] = None) -> Task:
        """Create and add new task"""
        import uuid
        task_id = str(uuid.uuid4())
        
        task = Task(
            task_id=task_id,
            name=name,
            platform=platform,
            crawler_type=crawler_type,
            query=query,
            max_results=max_results,
            interval=interval,
            start_time=start_time
        )
        
        self.add_task(task)
        return task


# Global scheduler instance for easy access
scheduler = None


def get_scheduler() -> Scheduler:
    """Get global scheduler instance"""
    global scheduler
    if not scheduler:
        scheduler = Scheduler()
    return scheduler