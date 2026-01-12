# -*- coding: utf-8 -*-
# Copyright (c) 2025 SuperCrawler Project
# Licensed under NON-COMMERCIAL LEARNING LICENSE 1.1

from typing import Dict, Type, Optional, Any

from src.storage.base.base_store import BaseStore, BaseStoreImage, BaseStoreVideo
from src.storage.file_storage.file_store import FileStore, FileStoreImage, FileStoreVideo
from src.storage.database.sqlite_store import SQLiteStore, SQLiteStoreImage, SQLiteStoreVideo
from src.storage.database.mongodb_store import MongoDBStore, MongoDBStoreImage, MongoDBStoreVideo


class StoreFactory:
    """Store factory for creating storage instances"""
    
    # Store implementations mapping
    STORES: Dict[str, Type[BaseStore]] = {
        "file": FileStore,
        "sqlite": SQLiteStore,
        "mongodb": MongoDBStore
    }
    
    # Image store implementations mapping
    IMAGE_STORES: Dict[str, Type[BaseStoreImage]] = {
        "file": FileStoreImage,
        "sqlite": SQLiteStoreImage,
        "mongodb": MongoDBStoreImage
    }
    
    # Video store implementations mapping
    VIDEO_STORES: Dict[str, Type[BaseStoreVideo]] = {
        "file": FileStoreVideo,
        "sqlite": SQLiteStoreVideo,
        "mongodb": MongoDBStoreVideo
    }
    
    @staticmethod
    def create_store(store_type: str, **kwargs) -> BaseStore:
        """Create a store instance"""
        store_class = StoreFactory.STORES.get(store_type)
        if not store_class:
            supported = ", ".join(sorted(StoreFactory.STORES))
            raise ValueError(f"Invalid store type: {store_type!r}. Supported: {supported}")
        return store_class(**kwargs)
    
    @staticmethod
    def create_image_store(store_type: str, **kwargs) -> BaseStoreImage:
        """Create an image store instance"""
        store_class = StoreFactory.IMAGE_STORES.get(store_type)
        if not store_class:
            supported = ", ".join(sorted(StoreFactory.IMAGE_STORES))
            raise ValueError(f"Invalid image store type: {store_type!r}. Supported: {supported}")
        return store_class(**kwargs)
    
    @staticmethod
    def create_video_store(store_type: str, **kwargs) -> BaseStoreVideo:
        """Create a video store instance"""
        store_class = StoreFactory.VIDEO_STORES.get(store_type)
        if not store_class:
            supported = ", ".join(sorted(StoreFactory.VIDEO_STORES))
            raise ValueError(f"Invalid video store type: {store_type!r}. Supported: {supported}")
        return store_class(**kwargs)
    
    @staticmethod
    def get_supported_store_types() -> list:
        """Get list of supported store types"""
        return list(StoreFactory.STORES.keys())
    
    @staticmethod
    def is_store_type_supported(store_type: str) -> bool:
        """Check if a store type is supported"""
        return store_type in StoreFactory.STORES