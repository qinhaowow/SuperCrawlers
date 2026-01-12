#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import time
import psutil
import os
from typing import Dict, Optional, List
import json
from datetime import datetime

from config import base_config


class Monitor:
    """Monitoring system for SuperCrawler"""
    
    def __init__(self):
        """Initialize monitor"""
        self.start_time = time.time()
        self.metrics = {
            "requests": {
                "total": 0,
                "success": 0,
                "failed": 0,
                "rate": 0.0
            },
            "crawling": {
                "items_processed": 0,
                "items_failed": 0,
                "current_rate": 0.0
            },
            "system": {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "network_sent": 0,
                "network_recv": 0
            },
            "timing": {
                "total_time": 0.0,
                "average_response_time": 0.0,
                "max_response_time": 0.0
            }
        }
        self.process = psutil.Process(os.getpid())
        self.monitoring_task: Optional[asyncio.Task] = None
        self.running = False
        self.log_file = os.path.join(base_config.DATA_DIR, "monitoring.log")
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    async def initialize(self):
        """Initialize monitoring system"""
        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        print("[Monitoring] Initialized monitoring system")
    
    async def cleanup(self):
        """Cleanup monitoring resources"""
        self.running = False
        if self.monitoring_task:
            try:
                self.monitoring_task.cancel()
                await asyncio.wait([self.monitoring_task], timeout=5.0)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"[Monitoring] Error cleaning up: {e}")
        print("[Monitoring] Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await self._collect_metrics()
                await self._log_metrics()
                await asyncio.sleep(base_config.MONITORING_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[Monitoring] Error in monitoring loop: {e}")
                await asyncio.sleep(1)
    
    async def _collect_metrics(self):
        """Collect system and crawling metrics"""
        # System metrics
        self.metrics["system"]["cpu_usage"] = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        self.metrics["system"]["memory_usage"] = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage(os.getcwd())
        self.metrics["system"]["disk_usage"] = disk.percent
        
        # Network metrics
        net_io = psutil.net_io_counters()
        self.metrics["system"]["network_sent"] = net_io.bytes_sent
        self.metrics["system"]["network_recv"] = net_io.bytes_recv
        
        # Timing metrics
        self.metrics["timing"]["total_time"] = time.time() - self.start_time
    
    async def _log_metrics(self):
        """Log metrics to file"""
        try:
            timestamp = datetime.now().isoformat()
            log_entry = {
                "timestamp": timestamp,
                "metrics": self.metrics
            }
            
            with open(self.log_file, "a", encoding="utf-8") as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write("\n")
        except Exception as e:
            print(f"[Monitoring] Error logging metrics: {e}")
    
    def record_request(self, success: bool, response_time: float = 0.0):
        """Record request metrics"""
        self.metrics["requests"]["total"] += 1
        if success:
            self.metrics["requests"]["success"] += 1
        else:
            self.metrics["requests"]["failed"] += 1
        
        # Update response time metrics
        if response_time > 0:
            self.metrics["timing"]["max_response_time"] = max(
                self.metrics["timing"]["max_response_time"],
                response_time
            )
            # Simple moving average
            total_requests = self.metrics["requests"]["total"]
            current_avg = self.metrics["timing"]["average_response_time"]
            self.metrics["timing"]["average_response_time"] = (
                (current_avg * (total_requests - 1)) + response_time
            ) / total_requests
    
    def record_item(self, success: bool):
        """Record item processing metrics"""
        if success:
            self.metrics["crawling"]["items_processed"] += 1
        else:
            self.metrics["crawling"]["items_failed"] += 1
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_summary(self) -> Dict:
        """Get monitoring summary"""
        total_requests = self.metrics["requests"]["total"]
        success_rate = (
            (self.metrics["requests"]["success"] / total_requests * 100)
            if total_requests > 0 else 0
        )
        
        total_items = (
            self.metrics["crawling"]["items_processed"] + 
            self.metrics["crawling"]["items_failed"]
        )
        item_success_rate = (
            (self.metrics["crawling"]["items_processed"] / total_items * 100)
            if total_items > 0 else 0
        )
        
        return {
            "uptime": self.metrics["timing"]["total_time"],
            "requests": {
                "total": total_requests,
                "success": self.metrics["requests"]["success"],
                "failed": self.metrics["requests"]["failed"],
                "success_rate": success_rate
            },
            "crawling": {
                "total_items": total_items,
                "processed": self.metrics["crawling"]["items_processed"],
                "failed": self.metrics["crawling"]["items_failed"],
                "success_rate": item_success_rate
            },
            "system": self.metrics["system"],
            "timing": self.metrics["timing"]
        }
    
    async def export_metrics(self, output_file: Optional[str] = None) -> str:
        """Export metrics to JSON file"""
        if not output_file:
            output_file = os.path.join(
                base_config.DATA_DIR,
                f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "summary": self.get_summary(),
                "detailed_metrics": self.metrics,
                "config": {
                    "monitoring_interval": base_config.MONITORING_INTERVAL,
                    "data_dir": base_config.DATA_DIR
                }
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"[Monitoring] Metrics exported to: {output_file}")
            return output_file
        except Exception as e:
            print(f"[Monitoring] Error exporting metrics: {e}")
            raise


# Global monitor instance for easy access
monitor = None


def get_monitor() -> Monitor:
    """Get global monitor instance"""
    global monitor
    if not monitor:
        monitor = Monitor()
    return monitor