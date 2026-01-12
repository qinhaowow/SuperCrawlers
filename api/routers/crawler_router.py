# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List, Optional

from main import CrawlerFactory
from config import get_platform_config

crawler_router = APIRouter()


@crawler_router.post("/crawler/start")
async def start_crawler(platform: str, query: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Start crawler for specified platform"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        await crawler.start()
        
        if query:
            results = await crawler.search(query, **kwargs)
            return {
                "success": True,
                "message": f"Started {crawler.get_platform_name()} crawler",
                "results": results[:10]  # Return first 10 results
            }
        
        return {
            "success": True,
            "message": f"Started {crawler.get_platform_name()} crawler"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.post("/crawler/search")
async def search_crawler(platform: str, query: str, **kwargs) -> Dict[str, Any]:
    """Search content on specified platform"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        results = await crawler.search(query, **kwargs)
        return {
            "success": True,
            "message": f"Search completed on {crawler.get_platform_name()}",
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.get("/crawler/content/{platform}/{content_id}")
async def get_content_detail(platform: str, content_id: str) -> Dict[str, Any]:
    """Get content detail by ID"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        content = await crawler.get_content_detail(content_id)
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


@crawler_router.get("/crawler/comments/{platform}/{content_id}")
async def get_comments(platform: str, content_id: str, max_comments: int = 100) -> Dict[str, Any]:
    """Get comments for content"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        comments = await crawler.get_comments(content_id, max_comments)
        return {
            "success": True,
            "comments": comments,
            "total": len(comments)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.get("/crawler/user/{platform}/{user_id}")
async def get_user_profile(platform: str, user_id: str) -> Dict[str, Any]:
    """Get user profile"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        profile = await crawler.get_user_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "success": True,
            "profile": profile
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.get("/crawler/user/content/{platform}/{user_id}")
async def get_user_content(platform: str, user_id: str, max_items: int = 50) -> Dict[str, Any]:
    """Get user's content"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        content = await crawler.get_user_content(user_id, max_items)
        return {
            "success": True,
            "content": content,
            "total": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.get("/crawler/features/{platform}")
async def get_crawler_features(platform: str) -> Dict[str, Any]:
    """Get crawler features for specified platform"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        return {
            "success": True,
            "platform": crawler.get_platform_name(),
            "features": crawler.get_supported_features()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@crawler_router.post("/crawler/login")
async def login_crawler(platform: str, login_type: str, **credentials) -> Dict[str, Any]:
    """Login to platform"""
    try:
        crawler = CrawlerFactory.create_crawler(platform)
        
        if not hasattr(crawler, "login_manager"):
            raise HTTPException(status_code=400, detail="Login not supported for this platform")
        
        login_manager = crawler.login_manager
        
        if login_type == "qrcode":
            result = await login_manager.login_by_qrcode()
        elif login_type == "mobile":
            phone_number = credentials.get("phone_number")
            if not phone_number:
                raise HTTPException(status_code=400, detail="Phone number required")
            result = await login_manager.login_by_mobile(phone_number)
        elif login_type == "cookie":
            cookies = credentials.get("cookies", {})
            result = await login_manager.login_by_cookies(cookies)
        elif login_type == "token":
            token = credentials.get("token")
            if not token:
                raise HTTPException(status_code=400, detail="Token required")
            result = await login_manager.login_by_token(token)
        else:
            raise HTTPException(status_code=400, detail="Invalid login type")
        
        return {
            "success": True,
            "message": f"Login completed on {crawler.get_platform_name()}",
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))