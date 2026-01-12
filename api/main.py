# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import os
import subprocess
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routers import crawler_router, data_router, websocket_router
from config import base_config

app = FastAPI(
    title="SuperCrawler WebAPI",
    description="API for controlling SuperCrawler from WebUI",
    version="1.0.0"
)

# Get webui static files directory
WEBUI_DIR = os.path.join(os.path.dirname(__file__), "webui")

# CORS configuration - allow frontend dev server access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Backup port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(crawler_router, prefix="/api")
app.include_router(data_router, prefix="/api")
app.include_router(websocket_router, prefix="/api")


@app.get("/")
async def serve_frontend():
    """Return frontend page"""
    index_path = os.path.join(WEBUI_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "message": "SuperCrawler WebAPI",
        "version": "1.0.0",
        "docs": "/docs",
        "note": "WebUI not found, please build it first: cd webui && npm run build"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


@app.get("/api/env/check")
async def check_environment():
    """Check if SuperCrawler environment is configured correctly"""
    try:
        # Run python main.py --help command to check environment
        process = await asyncio.create_subprocess_exec(
            "python", "main.py", "--help",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=".."  # Project root directory
        )
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=30.0  # 30 seconds timeout
        )

        if process.returncode == 0:
            return {
                "success": True,
                "message": "SuperCrawler environment configured correctly",
                "output": stdout.decode("utf-8", errors="ignore")[:500]  # Truncate to first 500 characters
            }
        else:
            error_msg = stderr.decode("utf-8", errors="ignore") or stdout.decode("utf-8", errors="ignore")
            return {
                "success": False,
                "message": "Environment check failed",
                "error": error_msg[:500]
            }
    except asyncio.TimeoutError:
        return {
            "success": False,
            "message": "Environment check timeout",
            "error": "Command execution exceeded 30 seconds"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "message": "python command not found",
            "error": "Please ensure Python is installed and configured in system PATH"
        }
    except Exception as e:
        return {
            "success": False,
            "message": "Environment check error",
            "error": str(e)
        }


@app.get("/api/config/platforms")
async def get_platforms():
    """Get list of supported platforms"""
    from main import CrawlerFactory
    platforms = []
    for code, crawler_class in CrawlerFactory.CRAWLERS.items():
        try:
            crawler = crawler_class()
            platforms.append({
                "value": code,
                "label": crawler.get_platform_name(),
                "features": crawler.get_supported_features()
            })
        except Exception:
            platforms.append({
                "value": code,
                "label": code.capitalize(),
                "features": []
            })
    return {"platforms": platforms}


@app.get("/api/config/options")
async def get_config_options():
    """Get all configuration options"""
    return {
        "login_types": [
            {"value": "qrcode", "label": "QR Code Login"},
            {"value": "mobile", "label": "Mobile Login"},
            {"value": "cookie", "label": "Cookie Login"},
            {"value": "token", "label": "Token Login"},
        ],
        "crawler_types": [
            {"value": "search", "label": "Search Mode"},
            {"value": "detail", "label": "Detail Mode"},
            {"value": "creator", "label": "Creator Mode"},
        ],
        "save_options": [
            {"value": "json", "label": "JSON File"},
            {"value": "csv", "label": "CSV File"},
            {"value": "excel", "label": "Excel File"},
            {"value": "sqlite", "label": "SQLite Database"},
            {"value": "db", "label": "MySQL Database"},
            {"value": "mongodb", "label": "MongoDB Database"},
        ],
        "proxy_providers": [
            {"value": "none", "label": "No Proxy"},
            {"value": "wandou", "label": "Wandou HTTP Proxy"},
            {"value": "kuaidl", "label": "Kuaidl Proxy"},
            {"value": "jishu", "label": "Jishu HTTP Proxy"},
        ],
    }


@app.get("/api/config/current")
async def get_current_config():
    """Get current configuration"""
    return {
        "project": {
            "name": base_config.PROJECT_NAME,
            "version": base_config.PROJECT_VERSION,
            "debug": base_config.DEBUG,
        },
        "storage": {
            "save_data_option": base_config.SAVE_DATA_OPTION,
            "data_dir": base_config.DATA_DIR,
        },
        "proxy": {
            "use_proxy": base_config.USE_PROXY,
            "proxy_provider": base_config.PROXY_PROVIDER,
            "proxy_pool_size": base_config.PROXY_POOL_SIZE,
        },
        "browser": {
            "headless": base_config.HEADLESS,
            "use_cdp": base_config.USE_CDP,
            "browser_timeout": base_config.BROWSER_TIMEOUT,
        },
        "rate_limiting": {
            "request_interval": base_config.REQUEST_INTERVAL,
            "max_requests_per_minute": base_config.MAX_REQUESTS_PER_MINUTE,
            "max_concurrent_requests": base_config.MAX_CONCURRENT_REQUESTS,
        },
        "login": {
            "login_type": base_config.LOGIN_TYPE,
            "cookies_dir": base_config.COOKIES_DIR,
        },
        "api": {
            "host": base_config.API_HOST,
            "port": base_config.API_PORT,
        },
    }


# Mount static resources - must be placed after all routes
if os.path.exists(WEBUI_DIR):
    assets_dir = os.path.join(WEBUI_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    # Mount logos directory
    logos_dir = os.path.join(WEBUI_DIR, "logos")
    if os.path.exists(logos_dir):
        app.mount("/logos", StaticFiles(directory=logos_dir), name="logos")
    # Mount other static files
    app.mount("/static", StaticFiles(directory=WEBUI_DIR), name="webui-static")


if __name__ == "__main__":
    uvicorn.run(app, host=base_config.API_HOST, port=base_config.API_PORT)