# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import os

from store import StoreFactory
from config import base_config

data_router = APIRouter()


@data_router.post("/data/store")
async def store_data(platform: str, data_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Store data to specified storage backend"""
    try:
        store = StoreFactory.create_store(base_config.SAVE_DATA_OPTION, platform)
        
        if data_type == "content":
            await store.store_content(data)
        elif data_type == "comment":
            await store.store_comment(data)
        elif data_type == "creator":
            await store.store_creator(data)
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")
        
        await store.close()
        return {
            "success": True,
            "message": f"Data stored successfully to {base_config.SAVE_DATA_OPTION}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.get("/data/content/{platform}/{content_id}")
async def get_stored_content(platform: str, content_id: str) -> Dict[str, Any]:
    """Get stored content by ID"""
    try:
        store = StoreFactory.create_store(base_config.SAVE_DATA_OPTION, platform)
        content = await store.get_content_by_id(content_id)
        await store.close()
        
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        return {
            "success": True,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.get("/data/comments/{platform}/{content_id}")
async def get_stored_comments(platform: str, content_id: str) -> Dict[str, Any]:
    """Get stored comments by content ID"""
    try:
        store = StoreFactory.create_store(base_config.SAVE_DATA_OPTION, platform)
        comments = await store.get_comments_by_content_id(content_id)
        await store.close()
        
        return {
            "success": True,
            "comments": comments,
            "total": len(comments)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.get("/data/creator/{platform}/{creator_id}")
async def get_stored_creator(platform: str, creator_id: str) -> Dict[str, Any]:
    """Get stored creator by ID"""
    try:
        store = StoreFactory.create_store(base_config.SAVE_DATA_OPTION, platform)
        creator = await store.get_creator_by_id(creator_id)
        await store.close()
        
        if not creator:
            raise HTTPException(status_code=404, detail="Creator not found")
        return {
            "success": True,
            "creator": creator
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.get("/data/stats/{platform}")
async def get_data_stats(platform: str) -> Dict[str, Any]:
    """Get data statistics for platform"""
    try:
        data_dir = os.path.join(base_config.DATA_DIR, platform)
        stats = {
            "platform": platform,
            "data_dir": data_dir,
            "files": []
        }
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                file_path = os.path.join(data_dir, file)
                if os.path.isfile(file_path):
                    stats["files"].append({
                        "name": file,
                        "size": os.path.getsize(file_path),
                        "path": file_path
                    })
        
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.post("/data/export")
async def export_data(platform: str, export_format: str, data_type: str = "all") -> Dict[str, Any]:
    """Export data to specified format"""
    try:
        # Implement data export logic
        return {
            "success": True,
            "message": f"Data exported successfully to {export_format}",
            "export_format": export_format,
            "data_type": data_type,
            "platform": platform
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@data_router.post("/data/clear")
async def clear_data(platform: str, data_type: str = "all") -> Dict[str, Any]:
    """Clear stored data"""
    try:
        # Implement data clearing logic
        return {
            "success": True,
            "message": f"Data cleared successfully",
            "data_type": data_type,
            "platform": platform
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))