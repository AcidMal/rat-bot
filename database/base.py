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