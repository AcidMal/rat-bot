import os
import json
import asyncio
import aiofiles
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from loguru import logger
from .base import DatabaseInterface

class JSONDatabase(DatabaseInterface):
    """JSON file-based database implementation"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.data = {
            "guild_configs": {},
            "moderation_logs": {},
            "music_queues": {},
            "user_data": {},
            "global_config": {},
            "global_stats": {}
        }
        self._lock = asyncio.Lock()
    
    async def connect(self) -> None:
        """Load data from JSON file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            if os.path.exists(self.file_path):
                async with aiofiles.open(self.file_path, 'r') as f:
                    content = await f.read()
                    if content.strip():
                        self.data = json.loads(content)
                        logger.info(f"Loaded data from {self.file_path}")
                    else:
                        logger.info(f"Empty file at {self.file_path}, using default data")
            else:
                logger.info(f"No existing database file at {self.file_path}, creating new one")
                await self._save_data()
        except Exception as e:
            logger.error(f"Failed to load JSON database: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Save data to JSON file"""
        await self._save_data()
        logger.info("JSON database disconnected")
    
    async def _save_data(self) -> None:
        """Save data to JSON file"""
        async with self._lock:
            try:
                # Convert datetime objects to ISO strings for JSON serialization
                serializable_data = self._make_serializable(self.data)
                
                async with aiofiles.open(self.file_path, 'w') as f:
                    await f.write(json.dumps(serializable_data, indent=2, default=str))
            except Exception as e:
                logger.error(f"Failed to save JSON database: {e}")
    
    def _make_serializable(self, obj):
        """Convert datetime objects to strings for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
    
    def _parse_datetime(self, obj):
        """Parse ISO datetime strings back to datetime objects"""
        if isinstance(obj, dict):
            return {k: self._parse_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._parse_datetime(item) for item in obj]
        elif isinstance(obj, str):
            try:
                # Try to parse as ISO datetime
                return datetime.fromisoformat(obj.replace('Z', '+00:00'))
            except ValueError:
                return obj
        else:
            return obj
    
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get guild configuration"""
        guild_id_str = str(guild_id)
        
        if guild_id_str in self.data["guild_configs"]:
            return self._parse_datetime(self.data["guild_configs"][guild_id_str])
        
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
                "max_song_length": 3600,
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
        
        await self.set_guild_config(guild_id, default_config)
        return default_config
    
    async def set_guild_config(self, guild_id: int, config: Dict[str, Any]) -> None:
        """Set guild configuration"""
        config["guild_id"] = guild_id
        config["updated_at"] = datetime.now(timezone.utc)
        
        self.data["guild_configs"][str(guild_id)] = config
        await self._save_data()
    
    async def log_moderation_action(self, action_data: Dict[str, Any]) -> str:
        """Log a moderation action and return the log ID"""
        action_data["timestamp"] = datetime.now(timezone.utc)
        log_id = f"{action_data['guild_id']}_{int(action_data['timestamp'].timestamp())}"
        action_data["log_id"] = log_id
        
        guild_id_str = str(action_data["guild_id"])
        if guild_id_str not in self.data["moderation_logs"]:
            self.data["moderation_logs"][guild_id_str] = []
        
        self.data["moderation_logs"][guild_id_str].append(action_data)
        await self._save_data()
        
        return log_id
    
    async def get_moderation_logs(self, guild_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get moderation logs for a guild"""
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self.data["moderation_logs"]:
            return []
        
        logs = self.data["moderation_logs"][guild_id_str]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Apply pagination
        end_index = offset + limit
        paginated_logs = logs[offset:end_index]
        
        return [self._parse_datetime(log) for log in paginated_logs]
    
    async def get_user_infractions(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all infractions for a user in a guild"""
        guild_id_str = str(guild_id)
        
        if guild_id_str not in self.data["moderation_logs"]:
            return []
        
        logs = self.data["moderation_logs"][guild_id_str]
        user_logs = [log for log in logs if log.get("target_user_id") == user_id]
        
        # Sort by timestamp (newest first)
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return [self._parse_datetime(log) for log in user_logs]
    
    async def save_music_queue(self, guild_id: int, queue_data: List[Dict[str, Any]]) -> None:
        """Save music queue for a guild"""
        self.data["music_queues"][str(guild_id)] = {
            "guild_id": guild_id,
            "queue": queue_data,
            "updated_at": datetime.now(timezone.utc)
        }
        await self._save_data()
    
    async def load_music_queue(self, guild_id: int) -> List[Dict[str, Any]]:
        """Load music queue for a guild"""
        guild_id_str = str(guild_id)
        
        if guild_id_str in self.data["music_queues"]:
            queue_data = self.data["music_queues"][guild_id_str]
            return queue_data.get("queue", [])
        
        return []
    
    async def set_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Set user data"""
        data["user_id"] = user_id
        data["updated_at"] = datetime.now(timezone.utc)
        
        self.data["user_data"][str(user_id)] = data
        await self._save_data()
    
    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data"""
        user_id_str = str(user_id)
        
        if user_id_str in self.data["user_data"]:
            return self._parse_datetime(self.data["user_data"][user_id_str])
        
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
        user_data = await self.get_user_data(user_id)
        
        if "stats" not in user_data:
            user_data["stats"] = {}
        
        current_value = user_data["stats"].get(stat_name, 0)
        new_value = current_value + amount
        user_data["stats"][stat_name] = new_value
        
        await self.set_user_data(user_id, user_data)
        return new_value
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics"""
        total_guilds = len(self.data["guild_configs"])
        total_commands_used = 0
        total_songs_played = 0
        total_messages = 0
        
        for user_data in self.data["user_data"].values():
            stats = user_data.get("stats", {})
            total_commands_used += stats.get("commands_used", 0)
            total_songs_played += stats.get("songs_played", 0)
            total_messages += stats.get("messages_sent", 0)
        
        return {
            "total_guilds": total_guilds,
            "total_commands_used": total_commands_used,
            "total_songs_played": total_songs_played,
            "total_messages": total_messages
        }
    
    async def set_global_config(self, key: str, value: Any) -> None:
        """Set global configuration value"""
        self.data["global_config"][key] = {
            "value": value,
            "updated_at": datetime.now(timezone.utc)
        }
        await self._save_data()
    
    async def get_global_config(self, key: str, default: Any = None) -> Any:
        """Get global configuration value"""
        if key in self.data["global_config"]:
            return self.data["global_config"][key]["value"]
        return default