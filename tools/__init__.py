# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from .browser_launcher import (
    BrowserLauncher, browser_launcher, get_browser_launcher,
    launch_browser, close_browser, close_all_browsers, cleanup_browser_resources
)
from .cdp_browser import (
    CDPBrowser, CDPManager, cdp_manager, get_cdp_manager,
    create_cdp_browser, get_cdp_browser, close_cdp_browser, cleanup_cdp_resources
)

__all__ = [
    # Browser launcher
    "BrowserLauncher",
    "browser_launcher",
    "get_browser_launcher",
    "launch_browser",
    "close_browser",
    "close_all_browsers",
    "cleanup_browser_resources",
    # CDP browser
    "CDPBrowser",
    "CDPManager",
    "cdp_manager",
    "get_cdp_manager",
    "create_cdp_browser",
    "get_cdp_browser",
    "close_cdp_browser",
    "cleanup_cdp_resources"
]