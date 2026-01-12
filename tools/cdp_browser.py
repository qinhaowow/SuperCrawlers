# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import asyncio
import json
from typing import Dict, Optional, Any, List
import websockets

from config import base_config


class CDPBrowser:
    """CDP browser implementation using Chrome DevTools Protocol"""
    
    def __init__(self, ws_url: str):
        self.ws_url = ws_url
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.session_id: Optional[str] = None
        self.target_id: Optional[str] = None
        self.command_id = 1
    
    async def connect(self):
        """Connect to CDP WebSocket"""
        self.websocket = await websockets.connect(self.ws_url)
        await self._initialize_session()
    
    async def _initialize_session(self):
        """Initialize CDP session"""
        # Get targets
        targets = await self.send_command("Target.getTargets")
        if targets and "result" in targets and "targetInfos" in targets["result"]:
            # Find the first page target
            for target in targets["result"]["targetInfos"]:
                if target.get("type") == "page":
                    self.target_id = target.get("targetId")
                    break
        
        if self.target_id:
            # Attach to target
            session = await self.send_command("Target.attachToTarget", {
                "targetId": self.target_id,
                "flatten": True
            })
            if session and "result" in session:
                self.session_id = session["result"].get("sessionId")
    
    async def send_command(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send CDP command"""
        if not self.websocket:
            raise Exception("Not connected to CDP")
        
        command = {
            "id": self.command_id,
            "method": method,
            "params": params or {}
        }
        
        if self.session_id:
            command["sessionId"] = self.session_id
        
        await self.websocket.send(json.dumps(command))
        self.command_id += 1
        
        response = await self.websocket.recv()
        return json.loads(response)
    
    async def evaluate(self, expression: str, return_by_value: bool = True) -> Any:
        """Evaluate JavaScript expression"""
        result = await self.send_command("Runtime.evaluate", {
            "expression": expression,
            "returnByValue": return_by_value
        })
        if result and "result" in result:
            return result["result"].get("value")
        return None
    
    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL"""
        return await self.send_command("Page.navigate", {
            "url": url
        })
    
    async def set_user_agent(self, user_agent: str, accept_language: str = "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"):
        """Set user agent"""
        return await self.send_command("Network.setUserAgentOverride", {
            "userAgent": user_agent,
            "acceptLanguage": accept_language
        })
    
    async def set_geolocation(self, latitude: float, longitude: float, accuracy: float = 100):
        """Set geolocation"""
        return await self.send_command("Emulation.setGeolocationOverride", {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy
        })
    
    async def set_timezone(self, timezone_id: str):
        """Set timezone"""
        return await self.send_command("Emulation.setTimezoneOverride", {
            "timezoneId": timezone_id
        })
    
    async def disable_automation(self):
        """Disable automation detection"""
        # Remove webdriver flag
        await self.evaluate("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """)
        
        # Remove Chrome automation flags
        await self.evaluate("""
        if (window.chrome) {
            delete window.chrome.loadTimes;
            delete window.chrome.csi;
            delete window.chrome.app;
        }
        """)
        
        # Mock navigator.languages
        await self.evaluate("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        """)
        
        # Mock navigator.plugins and navigator.mimeTypes
        await self.evaluate("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [{}]
        });
        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => [{}]
        });
        """)
        
        # Mock screen orientation
        await self.evaluate("""
        Object.defineProperty(screen, 'orientation', {
            get: () => ({
                angle: 0,
                type: 'landscape-primary',
                onchange: null
            })
        });
        """)
        
        # Mock window.outerWidth and window.outerHeight
        await self.evaluate("""
        Object.defineProperty(window, 'outerWidth', {
            get: () => window.innerWidth
        });
        Object.defineProperty(window, 'outerHeight', {
            get: () => window.innerHeight
        });
        """)
    
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Get cookies"""
        result = await self.send_command("Network.getCookies")
        if result and "result" in result:
            return result["result"].get("cookies", [])
        return []
    
    async def set_cookie(self, name: str, value: str, url: str, domain: Optional[str] = None, 
                        path: str = "/", secure: bool = False, http_only: bool = False):
        """Set cookie"""
        cookie = {
            "name": name,
            "value": value,
            "url": url,
            "path": path,
            "secure": secure,
            "httpOnly": http_only
        }
        if domain:
            cookie["domain"] = domain
        
        return await self.send_command("Network.setCookie", cookie)
    
    async def delete_cookie(self, name: str, url: str):
        """Delete cookie"""
        return await self.send_command("Network.deleteCookie", {
            "name": name,
            "url": url
        })
    
    async def clear_cookies(self):
        """Clear all cookies"""
        return await self.send_command("Network.clearBrowserCookies")
    
    async def get_local_storage(self, origin: str) -> Dict[str, str]:
        """Get local storage"""
        result = await self.send_command("Storage.getDOMStorageItems", {
            "storageId": {
                "isLocalStorage": True,
                "securityOrigin": origin
            }
        })
        if result and "result" in result and "entries" in result["result"]:
            return dict(result["result"]["entries"])
        return {}
    
    async def set_local_storage(self, origin: str, key: str, value: str):
        """Set local storage item"""
        return await self.send_command("Storage.setDOMStorageItem", {
            "storageId": {
                "isLocalStorage": True,
                "securityOrigin": origin
            },
            "key": key,
            "value": value
        })
    
    async def close(self):
        """Close CDP connection"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None


class CDPManager:
    """CDP browser manager"""
    
    def __init__(self):
        self.browsers: Dict[str, CDPBrowser] = {}
    
    async def create_browser(self, platform: str, ws_url: str) -> CDPBrowser:
        """Create CDP browser instance"""
        browser = CDPBrowser(ws_url)
        await browser.connect()
        await browser.disable_automation()
        self.browsers[platform] = browser
        return browser
    
    async def get_browser(self, platform: str) -> Optional[CDPBrowser]:
        """Get CDP browser instance"""
        return self.browsers.get(platform)
    
    async def close_browser(self, platform: str):
        """Close CDP browser"""
        if platform in self.browsers:
            browser = self.browsers[platform]
            try:
                await browser.close()
            except Exception:
                pass
            del self.browsers[platform]
    
    async def close_all(self):
        """Close all CDP browsers"""
        for platform in list(self.browsers.keys()):
            await self.close_browser(platform)
    
    async def cleanup(self, force: bool = False):
        """Cleanup CDP resources"""
        await self.close_all()


# Global CDP manager instance
cdp_manager = CDPManager()


async def get_cdp_manager() -> CDPManager:
    """Get CDP manager instance"""
    return cdp_manager


async def create_cdp_browser(platform: str, ws_url: str) -> CDPBrowser:
    """Create CDP browser instance"""
    return await cdp_manager.create_browser(platform, ws_url)


async def get_cdp_browser(platform: str) -> Optional[CDPBrowser]:
    """Get CDP browser instance"""
    return await cdp_manager.get_browser(platform)


async def close_cdp_browser(platform: str):
    """Close CDP browser"""
    await cdp_manager.close_browser(platform)


async def cleanup_cdp_resources():
    """Cleanup CDP resources"""
    await cdp_manager.cleanup()