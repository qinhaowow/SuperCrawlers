#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import argparse
from typing import Optional, Dict, Any
import config


async def parse_cmd() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="SuperCrawler - Multi-platform social media crawler",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Core arguments
    parser.add_argument(
        "--platform",
        "-p",
        type=str,
        default="xhs",
        choices=[
            "xhs", "dy", "ks", "bili", "wb", "tieba", "zhihu",
            "facebook", "twitter", "instagram", "youtube"
        ],
        help="Target platform to crawl\n"
             "xhs: Xiaohongshu\n"
             "dy: Douyin\n"
             "ks: Kuaishou\n"
             "bili: Bilibili\n"
             "wb: Weibo\n"
             "tieba: Baidu Tieba\n"
             "zhihu: Zhihu\n"
             "facebook: Facebook\n"
             "twitter: Twitter\n"
             "instagram: Instagram\n"
             "youtube: YouTube"
    )
    
    parser.add_argument(
        "--crawler-type",
        "-t",
        type=str,
        default="search",
        choices=["search", "detail", "creator"],
        help="Crawler type:\n"
             "search: Search for content\n"
             "detail: Get content details\n"
             "creator: Get creator information"
    )
    
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=None,
        help="Search query (required for search type)"
    )
    
    parser.add_argument(
        "--max-results",
        "-m",
        type=int,
        default=100,
        help="Maximum number of results to crawl (default: 100)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Output file path (default: auto-generated)"
    )
    
    # Database arguments
    parser.add_argument(
        "--init-db",
        type=str,
        default=None,
        choices=["sqlite", "mysql", "mongodb"],
        help="Initialize database schema\n"
             "sqlite: Initialize SQLite database\n"
             "mysql: Initialize MySQL database\n"
             "mongodb: Initialize MongoDB database"
    )
    
    # Proxy arguments
    parser.add_argument(
        "--use-proxy",
        action="store_true",
        default=False,
        help="Use proxy for requests"
    )
    
    parser.add_argument(
        "--proxy-provider",
        type=str,
        default="none",
        choices=["none", "wandou", "kuaidl", "jishu"],
        help="Proxy provider (default: none)"
    )
    
    parser.add_argument(
        "--proxy-api-key",
        type=str,
        default=None,
        help="API key for proxy provider"
    )
    
    # Browser arguments
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    
    parser.add_argument(
        "--use-cdp",
        action="store_true",
        default=False,
        help="Use Chrome DevTools Protocol for browser automation"
    )
    
    # Login arguments
    parser.add_argument(
        "--login-type",
        type=str,
        default="cookie",
        choices=["qrcode", "mobile", "cookie", "token"],
        help="Login method (default: cookie)"
    )
    
    parser.add_argument(
        "--cookies-file",
        type=str,
        default=None,
        help="Path to cookies file"
    )
    
    # Rate limiting arguments
    parser.add_argument(
        "--request-interval",
        type=float,
        default=1.0,
        help="Interval between requests in seconds (default: 1.0)"
    )
    
    parser.add_argument(
        "--max-requests-per-minute",
        type=int,
        default=60,
        help="Maximum requests per minute (default: 60)"
    )
    
    # Storage arguments
    parser.add_argument(
        "--save-data-option",
        type=str,
        default="json",
        choices=["json", "csv", "excel", "sqlite", "db", "mongodb"],
        help="Data storage format (default: json)"
    )
    
    # Debug arguments
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity level"
    )
    
    # Monitoring and scheduler arguments
    parser.add_argument(
        "--enable-monitoring",
        action="store_true",
        default=True,
        help="Enable monitoring system (default: True)"
    )
    
    parser.add_argument(
        "--enable-scheduler",
        action="store_true",
        default=True,
        help="Enable scheduler system (default: True)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Update configuration based on arguments
    await _update_config(args)
    
    # Validate arguments
    await _validate_args(args)
    
    return args


async def _update_config(args: argparse.Namespace) -> None:
    """Update configuration based on command-line arguments"""
    config.base_config.PLATFORM = args.platform
    config.base_config.SAVE_DATA_OPTION = args.save_data_option
    config.base_config.USE_PROXY = args.use_proxy
    config.base_config.PROXY_PROVIDER = args.proxy_provider
    config.base_config.PROXY_API_KEY = args.proxy_api_key
    config.base_config.HEADLESS = args.headless
    config.base_config.USE_CDP = args.use_cdp
    config.base_config.LOGIN_TYPE = args.login_type
    config.base_config.REQUEST_INTERVAL = args.request_interval
    config.base_config.MAX_REQUESTS_PER_MINUTE = args.max_requests_per_minute
    config.base_config.DEBUG = args.debug
    config.base_config.ENABLE_MONITORING = args.enable_monitoring
    config.base_config.ENABLE_SCHEDULER = args.enable_scheduler


async def _validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments"""
    # Validate search query
    if args.crawler_type == "search" and not args.query:
        raise ValueError("Search query is required for search type crawler")
    
    # Validate proxy configuration
    if args.use_proxy and args.proxy_provider == "none":
        raise ValueError("Proxy provider must be specified when using proxy")
    
    # Validate proxy API key
    if args.use_proxy and args.proxy_provider != "none" and not args.proxy_api_key:
        raise ValueError("Proxy API key is required for proxy provider")


def get_arg_dict(args: argparse.Namespace) -> Dict[str, Any]:
    """Convert arguments to dictionary"""
    return {
        "platform": args.platform,
        "crawler_type": args.crawler_type,
        "query": args.query,
        "max_results": args.max_results,
        "output": args.output,
        "init_db": args.init_db,
        "use_proxy": args.use_proxy,
        "proxy_provider": args.proxy_provider,
        "proxy_api_key": args.proxy_api_key,
        "headless": args.headless,
        "use_cdp": args.use_cdp,
        "login_type": args.login_type,
        "cookies_file": args.cookies_file,
        "request_interval": args.request_interval,
        "max_requests_per_minute": args.max_requests_per_minute,
        "save_data_option": args.save_data_option,
        "debug": args.debug,
        "verbose": args.verbose,
        "enable_monitoring": args.enable_monitoring,
        "enable_scheduler": args.enable_scheduler
    }


if __name__ == "__main__":
    """Test command-line argument parsing"""
    import asyncio
    
    async def test_parse():
        args = await parse_cmd()
        print("Parsed arguments:")
        print(args)
        print("\nArgument dictionary:")
        print(get_arg_dict(args))
    
    asyncio.run(test_parse())