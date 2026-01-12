# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import psutil
import time
from typing import Dict, Optional, Any, List

from src.core.base.base_crawler import AbstractMonitor


class Monitor(AbstractMonitor):
    """Monitor implementation"""
    
    def __init__(self):
        self._events = []
        self._errors = []
        self._stats = {
            'start_time': time.time(),
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'avg_response_time': 0,
            'total_response_time': 0
        }
        self._system_stats = {}
    
    async def initialize(self):
        """Initialize monitor"""
        pass
    
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log event"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'data': data
        }
        self._events.append(event)
        
        # Update stats based on event type
        if event_type == 'request':
            self._stats['requests'] += 1
        elif event_type == 'success':
            self._stats['successes'] += 1
        elif event_type == 'failure':
            self._stats['failures'] += 1
    
    async def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log error"""
        error_log = {
            'timestamp': time.time(),
            'error': str(error),
            'context': context
        }
        self._errors.append(error_log)
        self._stats['failures'] += 1
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        # Update system stats
        await self._update_system_stats()
        
        # Calculate uptime
        uptime = time.time() - self._stats['start_time']
        
        # Calculate success rate
        success_rate = 0
        if self._stats['requests'] > 0:
            success_rate = (self._stats['successes'] / self._stats['requests']) * 100
        
        # Calculate average response time
        avg_response_time = 0
        if self._stats['successes'] > 0:
            avg_response_time = self._stats['total_response_time'] / self._stats['successes']
        
        return {
            'uptime': uptime,
            'requests': self._stats['requests'],
            'successes': self._stats['successes'],
            'failures': self._stats['failures'],
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'system': self._system_stats
        }
    
    async def check_health(self) -> Dict[str, Any]:
        """Check health status"""
        stats = await self.get_stats()
        
        # Determine health status
        status = 'healthy'
        if stats['failures'] > stats['successes']:
            status = 'unhealthy'
        elif stats['failures'] > 0 and stats['success_rate'] < 50:
            status = 'degraded'
        
        return {
            'status': status,
            'stats': stats
        }
    
    async def cleanup(self):
        """Cleanup monitor"""
        pass
    
    async def _update_system_stats(self):
        """Update system statistics"""
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=0.1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk = psutil.disk_usage('/')
        disk_usage = disk.percent
        
        # Get network stats
        network = psutil.net_io_counters()
        
        self._system_stats = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'network_sent': network.bytes_sent,
            'network_recv': network.bytes_recv
        }
    
    async def get_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events"""
        return self._events[-limit:]
    
    async def get_errors(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent errors"""
        return self._errors[-limit:]