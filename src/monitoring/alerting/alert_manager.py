# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, Optional, Any, List

class AlertManager:
    """Alert manager for monitoring system"""
    
    def __init__(self):
        self._alerts = []
        self._alert_rules = []
    
    async def initialize(self):
        """Initialize alert manager"""
        # Add default alert rules
        await self.add_alert_rule({
            'name': 'high_failure_rate',
            'condition': lambda stats: stats['success_rate'] < 50,
            'severity': 'warning',
            'message': 'Failure rate is too high'
        })
        
        await self.add_alert_rule({
            'name': 'system_overload',
            'condition': lambda stats: stats['system']['cpu_usage'] > 80 or stats['system']['memory_usage'] > 80,
            'severity': 'warning',
            'message': 'System is overloaded'
        })
    
    async def add_alert_rule(self, rule: Dict[str, Any]):
        """Add alert rule"""
        self._alert_rules.append(rule)
    
    async def check_alerts(self, stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for alerts based on current stats"""
        triggered_alerts = []
        
        for rule in self._alert_rules:
            try:
                if rule['condition'](stats):
                    alert = {
                        'timestamp': stats.get('timestamp', 0),
                        'name': rule['name'],
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'stats': stats
                    }
                    triggered_alerts.append(alert)
                    self._alerts.append(alert)
            except Exception:
                pass
        
        return triggered_alerts
    
    async def get_alerts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        return self._alerts[-limit:]
    
    async def get_pending_alerts(self) -> List[Dict[str, Any]]:
        """Get pending alerts"""
        # Simplified - return all alerts
        return self._alerts
    
    async def clear_alerts(self):
        """Clear all alerts"""
        self._alerts.clear()