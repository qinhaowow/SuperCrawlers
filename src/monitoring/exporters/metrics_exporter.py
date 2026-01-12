# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import json
from typing import Dict, Optional, Any, List

class MetricsExporter:
    """Metrics exporter for monitoring system"""
    
    def __init__(self):
        self._exporters = []
    
    async def initialize(self):
        """Initialize metrics exporter"""
        pass
    
    async def add_exporter(self, exporter: 'BaseExporter'):
        """Add exporter"""
        self._exporters.append(exporter)
    
    async def export_metrics(self, metrics: Dict[str, Any]):
        """Export metrics to all registered exporters"""
        for exporter in self._exporters:
            await exporter.export(metrics)


class BaseExporter:
    """Base exporter class"""
    
    async def export(self, metrics: Dict[str, Any]):
        """Export metrics"""
        pass


class FileExporter(BaseExporter):
    """File exporter"""
    
    def __init__(self, file_path: str = "./metrics.json"):
        self._file_path = file_path
    
    async def export(self, metrics: Dict[str, Any]):
        """Export metrics to file"""
        try:
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(metrics, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


class ConsoleExporter(BaseExporter):
    """Console exporter"""
    
    async def export(self, metrics: Dict[str, Any]):
        """Export metrics to console"""
        try:
            print(json.dumps(metrics, ensure_ascii=False, indent=2))
        except Exception:
            pass