# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import uvicorn

from src.spiders.factory import CrawlerFactory
from src.monitoring.monitor import Monitor
from src.storage.factory import StoreFactory


app = FastAPI(
    title="SuperCrawler API",
    description="Multi-platform social media crawler API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
monitor = Monitor()
store = StoreFactory.create_store("file")


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    await monitor.initialize()
    await store.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    await monitor.cleanup()
    await store.close()


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SuperCrawler API"}


@app.get("/platforms")
async def get_platforms():
    """Get supported platforms"""
    platforms = CrawlerFactory.get_supported_platforms()
    return {"platforms": platforms}


@app.post("/crawl")
async def crawl(
    platform: str = Body(..., description="Target platform"),
    crawler_type: str = Body(..., description="Crawler type"),
    query: Optional[str] = Body(None, description="Search query"),
    content_id: Optional[str] = Body(None, description="Content ID"),
    user_id: Optional[str] = Body(None, description="User ID"),
    max_results: int = Body(100, description="Maximum number of results"),
):
    """Crawl content"""
    try:
        # Create crawler
        crawler = CrawlerFactory.create_crawler(platform=platform)
        
        # Execute crawl based on type
        if crawler_type == "search":
            if not query:
                raise HTTPException(status_code=400, detail="Search query is required")
            results = await crawler.search(query, max_results=max_results)
        elif crawler_type == "detail":
            if not content_id:
                raise HTTPException(status_code=400, detail="Content ID is required")
            results = await crawler.get_content_detail(content_id)
        elif crawler_type == "comments":
            if not content_id:
                raise HTTPException(status_code=400, detail="Content ID is required")
            results = await crawler.get_comments(content_id, max_comments=max_results)
        elif crawler_type == "creator":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required")
            results = await crawler.get_user_profile(user_id)
        elif crawler_type == "user_content":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required")
            results = await crawler.get_user_content(user_id, max_items=max_results)
        else:
            raise HTTPException(status_code=400, detail="Invalid crawler type")
        
        # Log event
        await monitor.log_event("crawl", {
            "platform": platform,
            "crawler_type": crawler_type,
            "results_count": len(results) if isinstance(results, list) else 1
        })
        
        return {"results": results}
    except Exception as e:
        await monitor.log_error(e, {"platform": platform, "crawler_type": crawler_type})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    stats = await monitor.get_stats()
    return {"stats": stats}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    health = await monitor.check_health()
    return {"status": health["status"], "stats": health["stats"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)