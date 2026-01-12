# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import time
from typing import Dict, Optional, Any, List

from src.core.base.base_crawler import AbstractScheduler


class Scheduler(AbstractScheduler):
    """Scheduler implementation"""
    
    def __init__(self):
        self._tasks = []
        self._recurring_tasks = []
        self._task_counter = 0
        self._running = False
    
    async def initialize(self):
        """Initialize scheduler"""
        self._running = True
        # Start task processing loop
        asyncio.create_task(self._process_tasks())
    
    async def schedule_task(self, task: Dict[str, Any], delay: int = 0):
        """Schedule a task"""
        task_id = f"task_{self._task_counter}"
        self._task_counter += 1
        
        scheduled_task = {
            'id': task_id,
            'task': task,
            'scheduled_at': time.time() + delay,
            'status': 'scheduled'
        }
        
        self._tasks.append(scheduled_task)
        return task_id
    
    async def schedule_recurring_task(self, task: Dict[str, Any], interval: int):
        """Schedule a recurring task"""
        task_id = f"recurring_task_{self._task_counter}"
        self._task_counter += 1
        
        recurring_task = {
            'id': task_id,
            'task': task,
            'interval': interval,
            'last_run': 0,
            'status': 'active'
        }
        
        self._recurring_tasks.append(recurring_task)
        return task_id
    
    async def cancel_task(self, task_id: str):
        """Cancel a task"""
        # Cancel scheduled task
        for i, task in enumerate(self._tasks):
            if task['id'] == task_id:
                self._tasks[i]['status'] = 'cancelled'
                return True
        
        # Cancel recurring task
        for i, task in enumerate(self._recurring_tasks):
            if task['id'] == task_id:
                self._recurring_tasks[i]['status'] = 'cancelled'
                return True
        
        return False
    
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks"""
        pending_tasks = []
        
        # Get scheduled tasks
        for task in self._tasks:
            if task['status'] == 'scheduled':
                pending_tasks.append(task)
        
        # Get recurring tasks
        for task in self._recurring_tasks:
            if task['status'] == 'active':
                pending_tasks.append(task)
        
        return pending_tasks
    
    async def cleanup(self):
        """Cleanup scheduler"""
        self._running = False
    
    async def _process_tasks(self):
        """Process tasks loop"""
        while self._running:
            current_time = time.time()
            
            # Process scheduled tasks
            completed_tasks = []
            for i, task in enumerate(self._tasks):
                if task['status'] == 'scheduled' and current_time >= task['scheduled_at']:
                    # Execute task
                    await self._execute_task(task)
                    completed_tasks.append(i)
            
            # Remove completed tasks
            for i in reversed(completed_tasks):
                self._tasks.pop(i)
            
            # Process recurring tasks
            for task in self._recurring_tasks:
                if task['status'] == 'active' and current_time - task['last_run'] >= task['interval']:
                    # Execute task
                    await self._execute_task(task)
                    task['last_run'] = current_time
            
            # Sleep for a short time
            await asyncio.sleep(1)
    
    async def _execute_task(self, task: Dict[str, Any]):
        """Execute a task"""
        try:
            task_func = task['task'].get('func')
            if callable(task_func):
                await task_func(**task['task'].get('kwargs', {}))
            task['status'] = 'completed'
        except Exception as e:
            task['status'] = 'failed'
            task['error'] = str(e)