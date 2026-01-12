#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import signal
import sys
import traceback
from typing import Optional, Callable, Awaitable
import os
import platform

from config import base_config


async def run(
    main_func: Callable[[], Awaitable[None]],
    cleanup_func: Optional[Callable[[], Awaitable[None]]] = None,
    cleanup_timeout_seconds: float = 30.0,
    on_first_interrupt: Optional[Callable[[], None]] = None
):
    """
    Run the application with proper signal handling and cleanup
    
    Args:
        main_func: Main function to run
        cleanup_func: Cleanup function to call on exit
        cleanup_timeout_seconds: Timeout for cleanup operations
        on_first_interrupt: Function to call on first interrupt signal
    """
    print("[AppRunner] Starting SuperCrawler application")
    
    # Create event loop
    loop = asyncio.get_event_loop()
    
    # Set up signal handlers
    setup_signal_handlers(loop, on_first_interrupt)
    
    try:
        # Run main function
        await main_func()
        print("[AppRunner] Main function completed successfully")
        
    except KeyboardInterrupt:
        print("\n[AppRunner] Received KeyboardInterrupt, shutting down...")
        
    except Exception as e:
        print(f"[AppRunner] Unexpected error: {e}")
        traceback.print_exc()
        
    finally:
        # Cleanup resources
        if cleanup_func:
            print("[AppRunner] Running cleanup operations...")
            try:
                # Run cleanup with timeout
                await asyncio.wait_for(cleanup_func(), timeout=cleanup_timeout_seconds)
                print("[AppRunner] Cleanup completed successfully")
            except asyncio.TimeoutError:
                print(f"[AppRunner] Cleanup timed out after {cleanup_timeout_seconds} seconds")
            except Exception as e:
                print(f"[AppRunner] Error during cleanup: {e}")
        
        # Close the event loop
        loop.close()
        print("[AppRunner] Application shutdown complete")


def setup_signal_handlers(loop: asyncio.AbstractEventLoop, on_first_interrupt: Optional[Callable[[], None]] = None):
    """
    Set up signal handlers for graceful shutdown
    
    Args:
        loop: Asyncio event loop
        on_first_interrupt: Function to call on first interrupt signal
    """
    interrupt_count = 0
    
    def signal_handler(sig: int, frame):
        nonlocal interrupt_count
        interrupt_count += 1
        
        if interrupt_count == 1:
            print("\n[AppRunner] Received interrupt signal. Press Ctrl+C again to force exit.")
            if on_first_interrupt:
                try:
                    on_first_interrupt()
                except Exception as e:
                    print(f"[AppRunner] Error in interrupt handler: {e}")
            
            # Schedule shutdown
            loop.create_task(shutdown(loop))
            
        elif interrupt_count == 2:
            print("\n[AppRunner] Forcing immediate exit...")
            sys.exit(1)
    
    def shutdown(loop: asyncio.AbstractEventLoop):
        """Schedule shutdown of the event loop"""
        async def _shutdown():
            # Cancel all running tasks
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            
            # Wait for tasks to cancel
            if tasks:
                print(f"[AppRunner] Cancelling {len(tasks)} running tasks...")
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception:
                    pass
            
            # Stop the loop
            loop.stop()
        
        loop.create_task(_shutdown())
    
    # Register signal handlers
    if platform.system() != "Windows":
        # Windows doesn't support SIGTERM and SIGINT handling the same way
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    else:
        # For Windows, we'll rely on KeyboardInterrupt
        print("[AppRunner] Running on Windows, using KeyboardInterrupt for shutdown")


def check_dependencies():
    """Check if required dependencies are installed"""
    required_modules = [
        "pydantic",
        "pydantic_settings",
        "playwright",
        "psutil",
        "aiofiles",
        "fastapi",
        "uvicorn",
        "websockets"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("[AppRunner] Missing dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\n[AppRunner] Please install missing dependencies:")
        print(f"  pip install {' '.join(missing_modules)}")
        return False
    
    print("[AppRunner] All required dependencies are installed")
    return True


def get_application_info():
    """Get application information"""
    return {
        "name": base_config.PROJECT_NAME,
        "version": base_config.PROJECT_VERSION,
        "python_version": sys.version,
        "platform": platform.platform(),
        "cwd": os.getcwd(),
        "data_dir": base_config.DATA_DIR,
        "debug": base_config.DEBUG
    }


def print_application_info():
    """Print application information"""
    info = get_application_info()
    print("[AppRunner] Application Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")


async def run_with_retry(
    func: Callable[[], Awaitable[Any]],
    max_retries: int = 3,
    retry_delay_seconds: float = 1.0,
    error_message: str = "Operation failed"
) -> Any:
    """
    Run a function with retry logic
    
    Args:
        func: Function to run
        max_retries: Maximum number of retries
        retry_delay_seconds: Delay between retries
        error_message: Error message to print
        
    Returns:
        Result of the function
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                print(f"[AppRunner] {error_message} (attempt {attempt + 1}/{max_retries}): {e}")
                await asyncio.sleep(retry_delay_seconds)
            else:
                print(f"[AppRunner] {error_message} after {max_retries} attempts: {e}")
                raise
    
    # This line should never be reached
    raise last_error or Exception("Unknown error")


class AppContext:
    """Application context manager"""
    
    def __init__(self):
        """Initialize application context"""
        self.resources = []
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize application context"""
        if self.is_initialized:
            return
        
        print("[AppRunner] Initializing application context")
        
        # Initialize resources here
        # Example: database connections, message queues, etc.
        
        self.is_initialized = True
        print("[AppRunner] Application context initialized")
    
    async def cleanup(self):
        """Cleanup application context"""
        if not self.is_initialized:
            return
        
        print("[AppRunner] Cleaning up application context")
        
        # Cleanup resources
        for resource in reversed(self.resources):
            try:
                if hasattr(resource, "close"):
                    if asyncio.iscoroutinefunction(resource.close):
                        await resource.close()
                    else:
                        resource.close()
                elif hasattr(resource, "cleanup"):
                    if asyncio.iscoroutinefunction(resource.cleanup):
                        await resource.cleanup()
                    else:
                        resource.cleanup()
            except Exception as e:
                print(f"[AppRunner] Error cleaning up resource: {e}")
        
        self.resources = []
        self.is_initialized = False
        print("[AppRunner] Application context cleaned up")
    
    def add_resource(self, resource):
        """Add resource to context"""
        self.resources.append(resource)
    
    def get_resource(self, resource_type):
        """Get resource by type"""
        for resource in self.resources:
            if isinstance(resource, resource_type):
                return resource
        return None


# Global application context
app_context = AppContext()


def get_app_context() -> AppContext:
    """Get global application context"""
    return app_context


if __name__ == "__main__":
    """Test the app runner"""
    async def test_main():
        print("Test main function running...")
        await asyncio.sleep(2)
        print("Test main function completed")
    
    async def test_cleanup():
        print("Test cleanup function running...")
        await asyncio.sleep(1)
        print("Test cleanup function completed")
    
    def test_interrupt():
        print("Test interrupt handler called")
    
    # Print application info
    print_application_info()
    
    # Check dependencies
    check_dependencies()
    
    # Run test
    asyncio.run(run(test_main, test_cleanup, on_first_interrupt=test_interrupt))