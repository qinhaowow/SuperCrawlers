# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
from typing import Dict, Optional, Any, List

class TaskQueue:
    """Task queue implementation"""
    
    def __init__(self, max_size: int = 1000):
        self._queue = asyncio.Queue(maxsize=max_size)
        self._task_count = 0
    
    async def initialize(self):
        """Initialize task queue"""
        pass
    
    async def enqueue(self, task: Dict[str, Any]) -> str:
        """Enqueue a task"""
        task_id = f"queue_task_{self._task_count}"
        self._task_count += 1
        task['id'] = task_id
        
        await self._queue.put(task)
        return task_id
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Dequeue a task"""
        try:
            return await asyncio.wait_for(self._queue.get(), timeout=1)
        except asyncio.TimeoutError:
            return None
    
    async def get_size(self) -> int:
        """Get queue size"""
        return self._queue.qsize()
    
    async def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self._queue.empty()
    
    async def clear(self):
        """Clear queue"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                break