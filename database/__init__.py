from .base import DatabaseInterface
from .mongodb import MongoDatabase
from .json_db import JSONDatabase
from config import config
from loguru import logger

async def get_database() -> DatabaseInterface:
    """Factory function to get the appropriate database implementation"""
    
    if config.database.type == "mongodb":
        db = MongoDatabase(config.database.mongodb_uri, config.database.database_name)
    elif config.database.type == "json":
        db = JSONDatabase(config.database.json_file_path)
    else:
        logger.error(f"Unknown database type: {config.database.type}")
        raise ValueError(f"Unknown database type: {config.database.type}")
    
    await db.connect()
    return db

__all__ = ['DatabaseInterface', 'MongoDatabase', 'JSONDatabase', 'get_database']