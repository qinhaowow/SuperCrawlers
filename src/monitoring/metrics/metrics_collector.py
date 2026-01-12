# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import time
from typing import Dict, Optional, Any, List

class MetricsCollector:
    """Metrics collector for monitoring system"""
    
    def __init__(self):
        self._metrics = {
            'crawler': {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'response_times': []
            },
            'system': {
                'cpu_usage': [],
                'memory_usage': [],
                'disk_usage': []
            },
            'proxy': {
                'used': 0,
                'failed': 0,
                'success_rate': 0
            }
        }
    
    async def initialize(self):
        """Initialize metrics collector"""
        pass
    
    async def collect_metric(self, category: str, name: str, value: Any):
        """Collect a metric"""
        if category not in self._metrics:
            self._metrics[category] = {}
        
        if isinstance(self._metrics[category].get(name), list):
            # Append to list
            self._metrics[category][name].append(value)
            # Keep only last 100 values
            if len(self._metrics[category][name]) > 100:
                self._metrics[category][name] = self._metrics[category][name][-100:]
        else:
            # Set value
            self._metrics[category][name] = value
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self._metrics
    
    async def get_metric(self, category: str, name: str) -> Optional[Any]:
        """Get a specific metric"""
        if category in self._metrics:
            return self._metrics[category].get(name)
        return None
    
    async def reset_metrics(self):
        """Reset all metrics"""
        self._metrics = {
            'crawler': {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'response_times': []
            },
            'system': {
                'cpu_usage': [],
                'memory_usage': [],
                'disk_usage': []
            },
            'proxy': {
                'used': 0,
                'failed': 0,
                'success_rate': 0
            }
        }