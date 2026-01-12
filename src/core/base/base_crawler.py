# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List, AsyncGenerator, Tuple

from playwright.async_api import BrowserContext, BrowserType, Playwright


class AbstractCrawler(ABC):

    @abstractmethod
    async def start(self):
        """
        Start crawler
        """
        pass

    @abstractmethod
    async def search(self, query: str, **kwargs):
        """
        Search content
        :param query: Search query
        :param kwargs: Additional search parameters
        """
        pass

    @abstractmethod
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], 
                            user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """
        Launch browser
        :param chromium: Chromium browser
        :param playwright_proxy: Playwright proxy configuration
        :param user_agent: User agent
        :param headless: Headless mode
        :return: Browser context
        """
        pass

    async def launch_browser_with_cdp(self, playwright: Playwright, playwright_proxy: Optional[Dict], 
                                     user_agent: Optional[str], headless: bool = True) -> BrowserContext:
        """
        Launch browser using CDP mode (optional implementation)
        :param playwright: Playwright instance
        :param playwright_proxy: Playwright proxy configuration
        :param user_agent: User agent
        :param headless: Headless mode
        :return: Browser context
        """
        # Default implementation: fallback to standard mode
        return await self.launch_browser(playwright.chromium, playwright_proxy, user_agent, headless)

    @abstractmethod
    async def get_content_detail(self, content_id: str) -> Dict[str, Any]:
        """
        Get content detail by ID
        :param content_id: Content ID
        :return: Content detail
        """
        pass

    @abstractmethod
    async def get_comments(self, content_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        """
        Get comments for content
        :param content_id: Content ID
        :param max_comments: Maximum number of comments to retrieve
        :return: List of comments
        """
        pass

    @abstractmethod
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile
        :param user_id: User ID
        :return: User profile
        """
        pass

    @abstractmethod
    async def get_user_content(self, user_id: str, max_items: int = 50) -> List[Dict[str, Any]]:
        """
        Get user's content
        :param user_id: User ID
        :param max_items: Maximum number of items to retrieve
        :return: List of user content
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """
        Get platform name
        :return: Platform name
        """
        pass

    @abstractmethod
    def get_supported_features(self) -> List[str]:
        """
        Get list of supported features
        :return: List of supported features
        """
        pass


class AbstractLogin(ABC):

    @abstractmethod
    async def begin(self):
        """
        Begin login process
        """
        pass

    @abstractmethod
    async def login_by_qrcode(self) -> Dict[str, Any]:
        """
        Login by QR code
        :return: Login result
        """
        pass

    @abstractmethod
    async def login_by_mobile(self, phone_number: str) -> Dict[str, Any]:
        """
        Login by mobile phone
        :param phone_number: Phone number
        :return: Login result
        """
        pass

    @abstractmethod
    async def login_by_cookies(self, cookies: Dict[str, str]) -> Dict[str, Any]:
        """
        Login by cookies
        :param cookies: Cookies dictionary
        :return: Login result
        """
        pass

    @abstractmethod
    async def login_by_token(self, token: str) -> Dict[str, Any]:
        """
        Login by token
        :param token: Authentication token
        :return: Login result
        """
        pass

    @abstractmethod
    async def is_logged_in(self) -> bool:
        """
        Check if logged in
        :return: True if logged in, False otherwise
        """
        pass

    @abstractmethod
    async def logout(self):
        """
        Logout
        """
        pass


class AbstractStore(ABC):

    @abstractmethod
    async def store_content(self, content_item: Dict[str, Any]):
        """
        Store content item
        :param content_item: Content item to store
        """
        pass

    @abstractmethod
    async def store_comment(self, comment_item: Dict[str, Any]):
        """
        Store comment item
        :param comment_item: Comment item to store
        """
        pass

    @abstractmethod
    async def store_creator(self, creator: Dict[str, Any]):
        """
        Store creator information
        :param creator: Creator information to store
        """
        pass

    @abstractmethod
    async def get_content_by_id(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get content by ID
        :param content_id: Content ID
        :return: Content if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_comments_by_content_id(self, content_id: str) -> List[Dict[str, Any]]:
        """
        Get comments by content ID
        :param content_id: Content ID
        :return: List of comments
        """
        pass

    @abstractmethod
    async def get_creator_by_id(self, creator_id: str) -> Optional[Dict[str, Any]]:
        """
        Get creator by ID
        :param creator_id: Creator ID
        :return: Creator if found, None otherwise
        """
        pass

    @abstractmethod
    async def close(self):
        """
        Close storage connection
        """
        pass


class AbstractStoreImage(ABC):

    @abstractmethod
    async def store_image(self, image_content_item: Dict[str, Any]):
        """
        Store image content
        :param image_content_item: Image content to store
        """
        pass

    @abstractmethod
    async def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """
        Get image by ID
        :param image_id: Image ID
        :return: Image if found, None otherwise
        """
        pass


class AbstractStoreVideo(ABC):

    @abstractmethod
    async def store_video(self, video_content_item: Dict[str, Any]):
        """
        Store video content
        :param video_content_item: Video content to store
        """
        pass

    @abstractmethod
    async def get_video_by_id(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video by ID
        :param video_id: Video ID
        :return: Video if found, None otherwise
        """
        pass


class AbstractApiClient(ABC):

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Make API request
        :param method: HTTP method
        :param url: API URL
        :param kwargs: Additional parameters
        :return: Response data
        """
        pass

    @abstractmethod
    async def update_cookies(self, browser_context: BrowserContext):
        """
        Update cookies from browser context
        :param browser_context: Browser context
        """
        pass

    @abstractmethod
    async def get_cookies(self) -> Dict[str, str]:
        """
        Get current cookies
        :return: Cookies dictionary
        """
        pass

    @abstractmethod
    async def set_cookies(self, cookies: Dict[str, str]):
        """
        Set cookies
        :param cookies: Cookies dictionary
        """
        pass

    @abstractmethod
    async def get_headers(self) -> Dict[str, str]:
        """
        Get current headers
        :return: Headers dictionary
        """
        pass

    @abstractmethod
    async def set_headers(self, headers: Dict[str, str]):
        """
        Set headers
        :param headers: Headers dictionary
        """
        pass


class AbstractProxyManager(ABC):

    @abstractmethod
    async def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Get a proxy
        :return: Proxy configuration
        """
        pass

    @abstractmethod
    async def validate_proxy(self, proxy: Dict[str, str]) -> bool:
        """
        Validate a proxy
        :param proxy: Proxy configuration
        :return: True if proxy is valid, False otherwise
        """
        pass

    @abstractmethod
    async def rotate_proxy(self):
        """
        Rotate to next proxy
        """
        pass

    @abstractmethod
    async def get_proxy_stats(self) -> Dict[str, Any]:
        """
        Get proxy statistics
        :return: Proxy statistics
        """
        pass


class AbstractMonitor(ABC):

    @abstractmethod
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log event
        :param event_type: Event type
        :param data: Event data
        """
        pass

    @abstractmethod
    async def log_error(self, error: Exception, context: Dict[str, Any]):
        """
        Log error
        :param error: Exception
        :param context: Error context
        """
        pass

    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics
        :return: Statistics
        """
        pass

    @abstractmethod
    async def check_health(self) -> Dict[str, Any]:
        """
        Check health status
        :return: Health status
        """
        pass


class AbstractScheduler(ABC):

    @abstractmethod
    async def schedule_task(self, task: Dict[str, Any], delay: int = 0):
        """
        Schedule a task
        :param task: Task configuration
        :param delay: Delay in seconds
        """
        pass

    @abstractmethod
    async def schedule_recurring_task(self, task: Dict[str, Any], interval: int):
        """
        Schedule a recurring task
        :param task: Task configuration
        :param interval: Interval in seconds
        """
        pass

    @abstractmethod
    async def cancel_task(self, task_id: str):
        """
        Cancel a task
        :param task_id: Task ID
        """
        pass

    @abstractmethod
    async def get_pending_tasks(self) -> List[Dict[str, Any]]:
        """
        Get pending tasks
        :return: List of pending tasks
        """
        pass


class AbstractPlugin(ABC):

    @abstractmethod
    async def initialize(self, crawler: AbstractCrawler):
        """
        Initialize plugin
        :param crawler: Crawler instance
        """
        pass

    @abstractmethod
    async def process_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process content
        :param content: Content to process
        :return: Processed content
        """
        pass

    @abstractmethod
    async def process_comment(self, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process comment
        :param comment: Comment to process
        :return: Processed comment
        """
        pass

    @abstractmethod
    async def process_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user
        :param user: User to process
        :return: Processed user
        """
        pass

    @abstractmethod
    async def cleanup(self):
        """
        Cleanup plugin resources
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get plugin name
        :return: Plugin name
        """
        pass

    @abstractmethod
    def get_version(self) -> str:
        """
        Get plugin version
        :return: Plugin version
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        Get plugin description
        :return: Plugin description
        """
        pass