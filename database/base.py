from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio

class DatabaseInterface(ABC):
    """Abstract base class for database implementations"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get guild configuration"""
        pass
    
    @abstractmethod
    async def set_guild_config(self, guild_id: int, config: Dict[str, Any]) -> None:
        """Set guild configuration"""
        pass
    
    @abstractmethod
    async def log_moderation_action(self, action_data: Dict[str, Any]) -> str:
        """Log a moderation action and return the log ID"""
        pass
    
    @abstractmethod
    async def get_moderation_logs(self, guild_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get moderation logs for a guild"""
        pass
    
    @abstractmethod
    async def get_user_infractions(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all infractions for a user in a guild"""
        pass
    
    @abstractmethod
    async def save_music_queue(self, guild_id: int, queue_data: List[Dict[str, Any]]) -> None:
        """Save music queue for a guild"""
        pass
    
    @abstractmethod
    async def load_music_queue(self, guild_id: int) -> List[Dict[str, Any]]:
        """Load music queue for a guild"""
        pass
    
    @abstractmethod
    async def add_to_queue(self, guild_id: int, track_data: Dict[str, Any]) -> int:
        """Add a track to the queue and return its position"""
        pass
    
    @abstractmethod
    async def get_next_in_queue(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get the next track in queue and remove it"""
        pass
    
    @abstractmethod
    async def get_queue_size(self, guild_id: int) -> int:
        """Get the current queue size"""
        pass
    
    @abstractmethod
    async def clear_queue(self, guild_id: int) -> int:
        """Clear the entire queue and return number of tracks removed"""
        pass
    
    @abstractmethod
    async def remove_from_queue(self, guild_id: int, position: int) -> bool:
        """Remove a track at specific position from queue"""
        pass
    
    @abstractmethod
    async def get_queue_preview(self, guild_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get a preview of the queue without removing tracks"""
        pass
    
    @abstractmethod
    async def set_user_data(self, user_id: int, data: Dict[str, Any]) -> None:
        """Set user data"""
        pass
    
    @abstractmethod
    async def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """Get user data"""
        pass
    
    @abstractmethod
    async def increment_user_stat(self, user_id: int, stat_name: str, amount: int = 1) -> int:
        """Increment a user statistic and return new value"""
        pass
    
    @abstractmethod
    async def get_global_stats(self) -> Dict[str, Any]:
        """Get global bot statistics"""
        pass
    
    @abstractmethod
    async def set_global_config(self, key: str, value: Any) -> None:
        """Set global configuration value"""
        pass
    
    @abstractmethod
    async def get_global_config(self, key: str, default: Any = None) -> Any:
        """Get global configuration value"""
        pass