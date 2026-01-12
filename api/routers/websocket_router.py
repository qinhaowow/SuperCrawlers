# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List
import json

websocket_router = APIRouter()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Remove disconnected clients
                self.active_connections.remove(connection)

manager = ConnectionManager()


@websocket_router.websocket("/ws/crawler")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for crawler updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await websocket.send_json({"action": "pong", "timestamp": message.get("timestamp")})
                
                elif action == "subscribe":
                    # Subscribe to specific platform updates
                    platform = message.get("platform")
                    await websocket.send_json({
                        "action": "subscribed",
                        "platform": platform,
                        "message": f"Subscribed to {platform} updates"
                    })
                
                elif action == "unsubscribe":
                    # Unsubscribe from updates
                    platform = message.get("platform")
                    await websocket.send_json({
                        "action": "unsubscribed",
                        "platform": platform,
                        "message": f"Unsubscribed from {platform} updates"
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "action": "error",
                    "message": "Invalid JSON format"
                })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def send_crawler_update(platform: str, status: str, data: Dict[str, Any] = None):
    """Send crawler update to all connected clients"""
    update_message = {
        "action": "crawler_update",
        "platform": platform,
        "status": status,
        "data": data or {},
        "timestamp": str(pow(10, 10) * __import__('time').time())[:13]
    }
    await manager.broadcast(update_message)


async def send_progress_update(platform: str, task_id: str, progress: float, message: str = None):
    """Send progress update for a specific task"""
    progress_message = {
        "action": "progress_update",
        "platform": platform,
        "task_id": task_id,
        "progress": progress,
        "message": message,
        "timestamp": str(pow(10, 10) * __import__('time').time())[:13]
    }
    await manager.broadcast(progress_message)


async def send_error_update(platform: str, error: str, context: Dict[str, Any] = None):
    """Send error update to all connected clients"""
    error_message = {
        "action": "error_update",
        "platform": platform,
        "error": error,
        "context": context or {},
        "timestamp": str(pow(10, 10) * __import__('time').time())[:13]
    }
    await manager.broadcast(error_message)


async def send_task_completed(platform: str, task_id: str, result: Dict[str, Any] = None):
    """Send task completed message"""
    completion_message = {
        "action": "task_completed",
        "platform": platform,
        "task_id": task_id,
        "result": result or {},
        "timestamp": str(pow(10, 10) * __import__('time').time())[:13]
    }
    await manager.broadcast(completion_message)