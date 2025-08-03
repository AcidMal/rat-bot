import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from loguru import logger
from .base import DatabaseInterface

class MongoDatabase(DatabaseInterface):
    """MongoDB implementation of the database interface"""
    
    def __init__(self, mongodb_uri: str, database_name: str):
        self.mongodb_uri = mongodb_uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
    
    async def connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongodb_uri)
            self.db = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create database indexes for better performance"""
        try:
            # Guild configs index
            await self.db.guild_configs.create_index("guild_id", unique=True)
            
            # Moderation logs indexes
            await self.db.moderation_logs.create_index([
                ("guild_id", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            await self.db.moderation_logs.create_index([
                ("guild_id", ASCENDING),
                ("target_user_id", ASCENDING),
                ("timestamp", DESCENDING)
            ])
            
            # Music queues index
            await self.db.music_queues.create_index("guild_id", unique=True)
            
            # User data index
            await self.db.user_data.create_index("user_id", unique=True)
            
            # Global config index
            await self.db.global_config.create_index("key", unique=True)
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {e}")
    
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get guild configuration"""
        result = await self.db.guild_configs.find_one({"guild_id": guild_id})
        if result:
            result.pop('_id', None)  # Remove MongoDB ObjectId
            return result
        
        # Return default config
        default_config = {
            "guild_id": guild_id,
            "prefix": "!",
            "modlog_channel": None,
            "music_channel": None,
            "auto_role": None,
            "welcome_channel": None,
            "welcome_message": None,
            "leave_message": None,
            "music_settings": {
                "max_queue_size": 100,
                "max_song_length": 3600,  # 1 hour
                "allow_duplicates": False,
                "vote_skip_threshold": 0.5
            },
            "moderation_settings": {
                "auto_mod_enabled": False,
                "spam_detection": False,
                "link_filter": False,
                "word_filter": [],
                "max_warnings": 3
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Save default config
        await self.set_guild_config(guild_id, default_config)
        return default_config
    
    async def set_guild_config(self, guild_id: int, config: Dict[str, Any]) -> None:
        """Set guild configuration"""
        config["guild_id"] = guild_id
        config["updated_at"] = datetime.now(timezone.utc)
        
        await self.db.guild_configs.update_one(
            {"guild_id": guild_id},
            {"$set": config},
            upsert=True
        )
    
    async def log_moderation_action(self, action_data: Dict[str, Any]) -> str:
        """Log a moderation action and return the log ID"""
        action_data["timestamp"] = datetime.now(timezone.utc)
        action_data["_id"] = f"{action_data['guild_id']}_{int(action_data['timestamp'].timestamp())}"
        
        result = await self.db.moderation_logs.insert_one(action_data)
        return str(result.inserted_id)
    
    async def get_moderation_logs(self, guild_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get moderation logs for a guild"""
        cursor = self.db.moderation_logs.find(
            {"guild_id": guild_id}
        ).sort("timestamp", DESCENDING).skip(offset).limit(limit)
        
        logs = []
        async for log in cursor:
            log.pop('_id', None)
            logs.append(log)
        
        return logs
    
    async def get_user_infractions(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all infractions for a user in a guild"""
        cursor = self.db.moderation_logs.find({
            "guild_id": guild_id,
            "target_user_id": user_id
        }).sort("timestamp", DESCENDING)
        
        infractions = []
        async for infraction in cursor:
            infraction.pop('_id', None)
            infractions.append(infraction)
        
        return infractions
    
    async def save_music_queue(self, guild_id: int, queue_data: List[Dict[str, Any]]) -> None:
        """Save music queue for a guild"""
        await self.db.music_queues.update_one(
            {"guild_id": guild_id},
            {
                "$set": {
                    "guild_id": guild_id,
                    "queue": queue_data,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
    
    async def load_music_queue(self, guild_id: int) -> List[Dict[str, Any]]:
        """Load music queue for a guild"""
        result = await self.db.music_queues.find_one({"guild_id": guild_id})
        if result and "queue" in result:
            return result["queue"]
        return []
    
    async def set_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Set user data"""
        data["user_id"] = user_id
        data["updated_at"] = datetime.now(timezone.utc)
        
        await self.db.user_data.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
    
    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data"""
        result = await self.db.user_data.find_one({"user_id": user_id})
        if result:
            result.pop('_id', None)
            return result
        
        # Return default user data
        default_data = {
            "user_id": user_id,
            "stats": {
                "commands_used": 0,
                "songs_played": 0,
                "messages_sent": 0
            },
            "preferences": {
                "music_volume": 100,
                "auto_play": False
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.set_user_data(user_id, default_data)
        return default_data
    
    async def increment_user_stat(self, user_id: int, stat_name: str, amount: int = 1) -> int:
        """Increment a user statistic and return new value"""
        result = await self.db.user_data.update_one(
            {"user_id": user_id},
            {
                "$inc": {f"stats.{stat_name}": amount},
                "$set": {"updated_at": datetime.now(timezone.utc)},
                "$setOnInsert": {
                    "user_id": user_id,
                    "created_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        # Get the updated value
        user_data = await self.get_user_data(user_id)
        return user_data.get("stats", {}).get(stat_name, 0)
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_guilds": {"$sum": 1},
                    "total_commands_used": {"$sum": "$stats.commands_used"},
                    "total_songs_played": {"$sum": "$stats.songs_played"},
                    "total_messages": {"$sum": "$stats.messages_sent"}
                }
            }
        ]
        
        result = await self.db.user_data.aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            stats.pop('_id', None)
            return stats
        
        return {
            "total_guilds": 0,
            "total_commands_used": 0,
            "total_songs_played": 0,
            "total_messages": 0
        }
    
    async def set_global_config(self, key: str, value: Any) -> None:
        """Set global configuration value"""
        await self.db.global_config.update_one(
            {"key": key},
            {
                "$set": {
                    "key": key,
                    "value": value,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
    
    async def get_global_config(self, key: str, default: Any = None) -> Any:
        """Get global configuration value"""
        result = await self.db.global_config.find_one({"key": key})
        if result:
            return result.get("value", default)
        return default