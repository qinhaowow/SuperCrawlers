# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import time
from typing import Dict, Optional, Any

class TaskThrottler:
    """Task throttler implementation"""
    
    def __init__(self, max_tasks_per_second: int = 10):
        self._max_tasks_per_second = max_tasks_per_second
        self._task_times = []
        self._last_cleanup = time.time()
    
    async def initialize(self):
        """Initialize task throttler"""
        pass
    
    async def throttle(self) -> float:
        """Throttle tasks to maintain rate limit"""
        current_time = time.time()
        
        # Clean up old task times
        if current_time - self._last_cleanup > 1:
            self._task_times = [t for t in self._task_times if current_time - t < 1]
            self._last_cleanup = current_time
        
        # Check if we've reached the rate limit
        if len(self._task_times) >= self._max_tasks_per_second:
            # Calculate wait time
            oldest_task_time = self._task_times[0]
            wait_time = 1 - (current_time - oldest_task_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                current_time = time.time()
        
        # Record current task time
        self._task_times.append(current_time)
        return current_time
    
    async def set_rate_limit(self, max_tasks_per_second: int):
        """Set rate limit"""
        self._max_tasks_per_second = max_tasks_per_second
    
    async def get_rate_limit(self) -> int:
        """Get rate limit"""
        return self._max_tasks_per_second
    
    async def get_current_rate(self) -> float:
        """Get current rate"""
        current_time = time.time()
        recent_tasks = [t for t in self._task_times if current_time - t < 1]
        return len(recent_tasks)


# Import asyncio for the throttle method
import asyncio