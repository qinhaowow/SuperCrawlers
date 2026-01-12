# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import sys
import io
import asyncio
import scrapy
from typing import Optional, Type, Dict, Any

# Force UTF-8 encoding for stdout/stderr to prevent encoding errors
# when outputting Chinese characters in non-UTF-8 terminals
if sys.stdout and hasattr(sys.stdout, 'buffer'):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr and hasattr(sys.stderr, 'buffer'):
    if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import src.api.cli.commands as cmd_arg
import src.config as config
from src.core.base.base_crawler import AbstractCrawler
from src.spiders.platforms.bilibili import BilibiliCrawler
from src.spiders.platforms.douyin import DouYinCrawler
from src.spiders.platforms.kuaishou import KuaishouCrawler
from src.spiders.platforms.tieba import TieBaCrawler
from src.spiders.platforms.weibo import WeiboCrawler
from src.spiders.platforms.xhs import XiaoHongShuCrawler
from src.spiders.platforms.zhihu import ZhihuCrawler
from src.spiders.platforms.facebook import FacebookCrawler
from src.spiders.platforms.twitter import TwitterCrawler
from src.spiders.platforms.instagram import InstagramCrawler
from src.spiders.platforms.youtube import YoutubeCrawler
from src.utils.async_file_writer import AsyncFileWriter
from src.utils.app_runner import run
from src.monitoring.monitor import Monitor
from src.scheduler.scheduler import Scheduler


class CrawlerFactory:
    """Crawler factory for creating platform-specific crawlers"""
    
    CRAWLERS: Dict[str, Type[AbstractCrawler]] = {
        # Chinese platforms
        "xhs": XiaoHongShuCrawler,
        "dy": DouYinCrawler,
        "ks": KuaishouCrawler,
        "bili": BilibiliCrawler,
        "wb": WeiboCrawler,
        "tieba": TieBaCrawler,
        "zhihu": ZhihuCrawler,
        # International platforms
        "facebook": FacebookCrawler,
        "twitter": TwitterCrawler,
        "instagram": InstagramCrawler,
        "youtube": YoutubeCrawler,
    }
    
    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        """Create a crawler for the specified platform"""
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            supported = ", ".join(sorted(CrawlerFactory.CRAWLERS))
            raise ValueError(f"Invalid media platform: {platform!r}. Supported: {supported}")
        return crawler_class()
    
    @staticmethod
    def get_supported_platforms() -> Dict[str, Dict[str, Any]]:
        """Get list of supported platforms with their features"""
        platforms = {}
        for platform_code, crawler_class in CrawlerFactory.CRAWLERS.items():
            try:
                crawler = crawler_class()
                platforms[platform_code] = {
                    "name": crawler.get_platform_name(),
                    "features": crawler.get_supported_features(),
                    "enabled": True
                }
            except Exception:
                platforms[platform_code] = {
                    "name": platform_code.capitalize(),
                    "features": [],
                    "enabled": False
                }
        return platforms
    
    @staticmethod
    def is_platform_supported(platform: str) -> bool:
        """Check if a platform is supported"""
        return platform in CrawlerFactory.CRAWLERS
    
    @staticmethod
    def get_platform_crawler_class(platform: str) -> Optional[Type[AbstractCrawler]]:
        """Get crawler class for a specific platform"""
        return CrawlerFactory.CRAWLERS.get(platform)


crawler: Optional[AbstractCrawler] = None
monitor: Optional[Monitor] = None
scheduler: Optional[Scheduler] = None


async def _flush_excel_if_needed() -> None:
    """Flush Excel data if needed"""
    if config.base_config.SAVE_DATA_OPTION != "excel":
        return
    
    try:
        from store.excel_store_base import ExcelStoreBase
        ExcelStoreBase.flush_all()
        print("[Main] Excel files saved successfully")
    except Exception as e:
        print(f"[Main] Error flushing Excel data: {e}")


async def _generate_wordcloud_if_needed() -> None:
    """Generate wordcloud if needed"""
    if config.base_config.SAVE_DATA_OPTION != "json":
        return
    
    try:
        file_writer = AsyncFileWriter(
            platform=config.base_config.PLATFORM,
            crawler_type="search",
        )
        await file_writer.generate_wordcloud_from_comments()
    except Exception as e:
        print(f"[Main] Error generating wordcloud: {e}")


async def _initialize_monitoring() -> None:
    """Initialize monitoring system"""
    global monitor
    if config.base_config.ENABLE_MONITORING:
        from src.monitoring.monitor import Monitor
        monitor = Monitor()
        await monitor.initialize()
        print("[Main] Monitoring system initialized")


async def _initialize_scheduler() -> None:
    """Initialize scheduler system"""
    global scheduler
    if config.base_config.ENABLE_SCHEDULER:
        from src.scheduler.scheduler import Scheduler
        scheduler = Scheduler()
        await scheduler.initialize()
        print("[Main] Scheduler system initialized")


async def _cleanup_resources() -> None:
    """Cleanup resources"""
    global crawler, monitor, scheduler
    
    # Cleanup crawler
    if crawler:
        if hasattr(crawler, "cdp_manager"):
            try:
                await crawler.cdp_manager.cleanup(force=True)
            except Exception as e:
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[Main] Error cleaning up CDP browser: {e}")
        
        elif hasattr(crawler, "browser_context"):
            try:
                await crawler.browser_context.close()
            except Exception as e:
                error_msg = str(e).lower()
                if "closed" not in error_msg and "disconnected" not in error_msg:
                    print(f"[Main] Error closing browser context: {e}")
    
    # Cleanup monitoring
    if monitor:
        try:
            await monitor.cleanup()
        except Exception as e:
            print(f"[Main] Error cleaning up monitor: {e}")
    
    # Cleanup scheduler
    if scheduler:
        try:
            await scheduler.cleanup()
        except Exception as e:
            print(f"[Main] Error cleaning up scheduler: {e}")
    
    # Cleanup database connections
    if config.base_config.SAVE_DATA_OPTION in ("db", "sqlite", "mongodb"):
        try:
            from src.storage.database.db import close
            await close()
        except Exception as e:
            print(f"[Main] Error closing database connections: {e}")


async def main() -> None:
    """Main function"""
    global crawler
    
    # Parse command-line arguments
    args = await cmd_arg.parse_cmd()
    
    # Initialize monitoring
    await _initialize_monitoring()
    
    # Initialize scheduler
    await _initialize_scheduler()
    
    # Handle database initialization
    if args.init_db:
        try:
            from src.storage.database.db import init_db
            await init_db(args.init_db)
            print(f"Database {args.init_db} initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
        return
    
    # Create crawler
    platform = config.base_config.PLATFORM
    print(f"[Main] Creating crawler for platform: {platform}")
    
    try:
        crawler = CrawlerFactory.create_crawler(platform=platform)
        print(f"[Main] Created crawler: {crawler.get_platform_name()}")
        print(f"[Main] Supported features: {', '.join(crawler.get_supported_features())}")
        
        # Start crawler
        await crawler.start()
        
        # Flush Excel data if needed
        await _flush_excel_if_needed()
        
        # Generate wordcloud if needed
        await _generate_wordcloud_if_needed()
        
    except Exception as e:
        print(f"[Main] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup resources
        await _cleanup_resources()


async def async_cleanup() -> None:
    """Async cleanup function for app runner"""
    await _cleanup_resources()


if __name__ == "__main__":
    """Entry point"""
    def _force_stop() -> None:
        """Force stop function"""
        c = crawler
        if not c:
            return
        cdp_manager = getattr(c, "cdp_manager", None)
        launcher = getattr(cdp_manager, "launcher", None)
        if not launcher:
            return
        try:
            launcher.cleanup()
        except Exception:
            pass
    
    # Run the application
    run(main, async_cleanup, cleanup_timeout_seconds=30.0, on_first_interrupt=_force_stop)