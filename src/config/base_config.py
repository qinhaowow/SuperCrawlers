# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

import os
import json
from typing import Dict, Optional, Any, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class BaseConfig(BaseSettings):
    """Base configuration class"""
    
    # Project settings
    PROJECT_NAME: str = "SuperCrawler"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Storage settings
    SAVE_DATA_OPTION: str = "json"  # json, csv, excel, sqlite, db, mongodb
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    # Proxy settings
    USE_PROXY: bool = False
    PROXY_PROVIDER: str = "none"  # none, wandou, kuaidl, jishu
    PROXY_API_KEY: Optional[str] = None
    PROXY_POOL_SIZE: int = 50
    PROXY_VALIDATION_TIMEOUT: int = 10
    
    # Browser settings
    HEADLESS: bool = True
    USE_CDP: bool = False
    BROWSER_TIMEOUT: int = 30
    PAGE_LOAD_TIMEOUT: int = 60
    
    # Rate limiting
    REQUEST_INTERVAL: float = 1.0  # Seconds between requests
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_CONCURRENT_REQUESTS: int = 5
    
    # Login settings
    LOGIN_TYPE: str = "cookie"  # qrcode, mobile, cookie, token
    COOKIES_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cookies")
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_KEY: Optional[str] = None
    
    # Database settings
    DB_TYPE: str = "sqlite"  # sqlite, mysql, postgresql
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "supercrawler"
    
    # MongoDB settings
    MONGODB_URI: Optional[str] = None
    MONGODB_DB: str = "supercrawler"
    
    # Redis settings (for caching)
    REDIS_URL: Optional[str] = None
    REDIS_DB: int = 0
    
    # Monitoring settings
    ENABLE_MONITORING: bool = True
    MONITORING_INTERVAL: int = 60  # Seconds
    
    # Scheduler settings
    ENABLE_SCHEDULER: bool = True
    SCHEDULER_INTERVAL: int = 60  # Seconds
    
    # Plugins settings
    ENABLE_PLUGINS: bool = True
    PLUGINS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
    
    # Data processing settings
    ENABLE_DATA_PROCESSING: bool = True
    DATA_PROCESSING_QUEUE_SIZE: int = 1000
    
    # Cloud settings
    ENABLE_CLOUD_INTEGRATION: bool = False
    CLOUD_PROVIDER: str = "aws"  # aws, gcp, azure
    
    @validator("DATA_DIR", "COOKIES_DIR", "PLUGINS_DIR", pre=True)
    def ensure_dirs_exist(cls, v: str) -> str:
        """Ensure directories exist"""
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class PlatformConfig(BaseSettings):
    """Base platform configuration"""
    
    PLATFORM_NAME: str
    PLATFORM_ENABLED: bool = True
    PLATFORM_BASE_URL: str
    PLATFORM_API_URL: Optional[str] = None
    
    # Authentication
    AUTH_REQUIRED: bool = True
    AUTH_ENDPOINT: Optional[str] = None
    
    # Rate limiting
    PLATFORM_REQUEST_INTERVAL: float = 1.0
    PLATFORM_MAX_REQUESTS_PER_MINUTE: int = 60
    
    # Features
    SUPPORTED_FEATURES: List[str] = []
    
    # Headers
    DEFAULT_HEADERS: Dict[str, str] = {}
    
    # Cookies
    COOKIE_KEYS: List[str] = []
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class XiaohongshuConfig(PlatformConfig):
    """Xiaohongshu configuration"""
    
    PLATFORM_NAME: str = "xhs"
    PLATFORM_BASE_URL: str = "https://www.xiaohongshu.com"
    PLATFORM_API_URL: str = "https://www.xiaohongshu.com/api/sns"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
    }
    
    COOKIE_KEYS: List[str] = [
        "abRequestId", "xsecappid", "a1", "webId", 
        "gid", "webBuild", "acw_tc", "web_session"
    ]


class DouyinConfig(PlatformConfig):
    """Douyin configuration"""
    
    PLATFORM_NAME: str = "dy"
    PLATFORM_BASE_URL: str = "https://www.douyin.com"
    PLATFORM_API_URL: str = "https://www.douyin.com/aweme/v1"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "tt_webid", "tt_webid_v2", "odin_tt", 
        "sessionid", "uid_tt", "uid_tt_ss"
    ]


class KuaishouConfig(PlatformConfig):
    """Kuaishou configuration"""
    
    PLATFORM_NAME: str = "ks"
    PLATFORM_BASE_URL: str = "https://www.kuaishou.com"
    PLATFORM_API_URL: str = "https://www.kuaishou.com/graphql"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "clientid", "userId", "kuaishou.server.web_st", 
        "kuaishou.server.web_ph", "sessionid"
    ]


class BilibiliConfig(PlatformConfig):
    """Bilibili configuration"""
    
    PLATFORM_NAME: str = "bili"
    PLATFORM_BASE_URL: str = "https://www.bilibili.com"
    PLATFORM_API_URL: str = "https://api.bilibili.com"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "SESSDATA", "bili_jct", "DedeUserID", 
        "DedeUserID__ckMd5", "sid"
    ]


class WeiboConfig(PlatformConfig):
    """Weibo configuration"""
    
    PLATFORM_NAME: str = "wb"
    PLATFORM_BASE_URL: str = "https://weibo.com"
    PLATFORM_API_URL: str = "https://weibo.com/ajax"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login",
        "store_image", "store_video"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "SUB", "SUBP", "XSRF-TOKEN", 
        "WEIBOCN_FROM", "login_sid_t"
    ]


class TiebaConfig(PlatformConfig):
    """Baidu Tieba configuration"""
    
    PLATFORM_NAME: str = "tieba"
    PLATFORM_BASE_URL: str = "https://tieba.baidu.com"
    PLATFORM_API_URL: str = "https://tieba.baidu.com/f"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "BDUSS", "STOKEN", "BAIDUID", 
        "BAIDUID_BFESS", "BDORZ"
    ]


class ZhihuConfig(PlatformConfig):
    """Zhihu configuration"""
    
    PLATFORM_NAME: str = "zhihu"
    PLATFORM_BASE_URL: str = "https://www.zhihu.com"
    PLATFORM_API_URL: str = "https://www.zhihu.com/api/v4"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    
    COOKIE_KEYS: List[str] = [
        "_zap", "d_c0", "z_c0", 
        "tst", "q_c1"
    ]


class FacebookConfig(PlatformConfig):
    """Facebook configuration"""
    
    PLATFORM_NAME: str = "facebook"
    PLATFORM_BASE_URL: str = "https://www.facebook.com"
    PLATFORM_API_URL: str = "https://graph.facebook.com/v18.0"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    COOKIE_KEYS: List[str] = [
        "c_user", "xs", "fr", 
        "datr", "wd"
    ]


class TwitterConfig(PlatformConfig):
    """Twitter configuration"""
    
    PLATFORM_NAME: str = "twitter"
    PLATFORM_BASE_URL: str = "https://twitter.com"
    PLATFORM_API_URL: str = "https://api.twitter.com/2"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    COOKIE_KEYS: List[str] = [
        "auth_token", "ct0", "twid", 
        "guest_id", "personalization_id"
    ]


class InstagramConfig(PlatformConfig):
    """Instagram configuration"""
    
    PLATFORM_NAME: str = "instagram"
    PLATFORM_BASE_URL: str = "https://www.instagram.com"
    PLATFORM_API_URL: str = "https://www.instagram.com/api/v1"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    COOKIE_KEYS: List[str] = [
        "sessionid", "ds_user_id", "csrftoken", 
        "ig_did", "ig_nrcb"
    ]


class YoutubeConfig(PlatformConfig):
    """YouTube configuration"""
    
    PLATFORM_NAME: str = "youtube"
    PLATFORM_BASE_URL: str = "https://www.youtube.com"
    PLATFORM_API_URL: str = "https://www.googleapis.com/youtube/v3"
    
    SUPPORTED_FEATURES: List[str] = [
        "search", "content_detail", "comments", 
        "user_profile", "user_content", "login"
    ]
    
    DEFAULT_HEADERS: Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    COOKIE_KEYS: List[str] = [
        "SID", "HSID", "SSID", 
        "APISID", "SAPISID"
    ]


# Create configuration instances
base_config = BaseConfig()

# Platform configurations
platform_configs = {
    "xhs": XiaohongshuConfig(),
    "dy": DouyinConfig(),
    "ks": KuaishouConfig(),
    "bili": BilibiliConfig(),
    "wb": WeiboConfig(),
    "tieba": TiebaConfig(),
    "zhihu": ZhihuConfig(),
    "facebook": FacebookConfig(),
    "twitter": TwitterConfig(),
    "instagram": InstagramConfig(),
    "youtube": YoutubeConfig(),
}


def get_config(platform: Optional[str] = None) -> Any:
    """Get configuration for a specific platform or base config"""
    if platform and platform in platform_configs:
        return platform_configs[platform]
    return base_config


def get_platform_config(platform: str) -> PlatformConfig:
    """Get platform-specific configuration"""
    if platform not in platform_configs:
        raise ValueError(f"Platform {platform} not supported")
    return platform_configs[platform]


def load_config_from_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config_to_file(config_data: Dict[str, Any], file_path: str):
    """Save configuration to JSON file"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(config_data, f, indent=2, ensure_ascii=False)


# Ensure data directories exist
os.makedirs(base_config.DATA_DIR, exist_ok=True)
os.makedirs(base_config.COOKIES_DIR, exist_ok=True)