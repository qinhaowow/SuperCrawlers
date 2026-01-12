# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import hashlib
from typing import Dict, Optional, Any, Set

class TaskDeduplicator:
    """Task deduplicator implementation"""
    
    def __init__(self, max_size: int = 10000):
        self._task_hashes = set()
        self._max_size = max_size
    
    async def initialize(self):
        """Initialize task deduplicator"""
        pass
    
    async def is_duplicate(self, task: Dict[str, Any]) -> bool:
        """Check if task is duplicate"""
        task_hash = self._get_task_hash(task)
        
        if task_hash in self._task_hashes:
            return True
        
        # Add task hash to set
        self._task_hashes.add(task_hash)
        
        # Trim set if it's too large
        if len(self._task_hashes) > self._max_size:
            # Remove oldest entries (simplified - just keep last max_size)
            self._task_hashes = set(list(self._task_hashes)[-self._max_size:])
        
        return False
    
    async def add_task(self, task: Dict[str, Any]):
        """Add task to deduplicator"""
        task_hash = self._get_task_hash(task)
        self._task_hashes.add(task_hash)
        
        # Trim set if it's too large
        if len(self._task_hashes) > self._max_size:
            self._task_hashes = set(list(self._task_hashes)[-self._max_size:])
    
    async def remove_task(self, task: Dict[str, Any]):
        """Remove task from deduplicator"""
        task_hash = self._get_task_hash(task)
        if task_hash in self._task_hashes:
            self._task_hashes.remove(task_hash)
    
    async def clear(self):
        """Clear deduplicator"""
        self._task_hashes.clear()
    
    def _get_task_hash(self, task: Dict[str, Any]) -> str:
        """Get task hash"""
        # Create a string representation of the task
        task_str = str(sorted(task.items()))
        # Generate hash
        return hashlib.md5(task_str.encode()).hexdigest()