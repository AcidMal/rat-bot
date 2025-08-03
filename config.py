import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """Database configuration"""
    type: str = "mongodb"  # mongodb, json, or sqlite
    mongodb_uri: str = ""
    database_name: str = "discord_bot"
    json_file_path: str = "data/database.json"

@dataclass
class LavalinkConfig:
    """Lavalink server configuration"""
    host: str = "localhost"
    port: int = 2333
    password: str = "youshallnotpass"
    ssl: bool = False
    heartbeat: int = 30
    timeout: int = 10

@dataclass
class RedisConfig:
    """Redis configuration for node communication"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    db: int = 0

@dataclass
class WebConfig:
    """Web API configuration"""
    enabled: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    secret_key: str = ""
    cors_origins: list = field(default_factory=lambda: ["*"])

@dataclass
class ShardingConfig:
    """Bot sharding configuration"""
    enabled: bool = False
    shard_count: Optional[int] = None
    shard_ids: Optional[list] = None
    auto_shard: bool = True

@dataclass
class NodeConfig:
    """Node meshing configuration"""
    node_id: str = "node-1"
    cluster_name: str = "discord-bot-cluster"
    is_primary: bool = True
    heartbeat_interval: int = 30

class Config:
    """Main configuration class"""
    
    def __init__(self):
        # Discord Bot Configuration
        self.token = os.getenv('DISCORD_TOKEN', '')
        self.prefix = os.getenv('PREFIX', '!')
        self.owner_ids = self._parse_list(os.getenv('OWNER_IDS', ''))
        
        # Embed color handling
        embed_color_str = os.getenv('EMBED_COLOR', '0x7289da')
        if embed_color_str.startswith('0x'):
            self.embed_color = int(embed_color_str, 16)
        else:
            self.embed_color = int(embed_color_str)
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/bot.log')
        
        # Component configurations
        self.database = DatabaseConfig(
            type=os.getenv('DATABASE_TYPE', 'mongodb'),
            mongodb_uri=os.getenv('MONGODB_URI', 'mongodb://localhost:27017'),
            database_name=os.getenv('DATABASE_NAME', 'discord_bot'),
            json_file_path=os.getenv('JSON_DATABASE_PATH', 'data/database.json')
        )
        
        self.lavalink = LavalinkConfig(
            host=os.getenv('LAVALINK_HOST', 'localhost'),
            port=int(os.getenv('LAVALINK_PORT', 2333)),
            password=os.getenv('LAVALINK_PASSWORD', 'youshallnotpass'),
            ssl=os.getenv('LAVALINK_SSL', 'false').lower() == 'true',
            heartbeat=int(os.getenv('LAVALINK_HEARTBEAT', 30)),
            timeout=int(os.getenv('LAVALINK_TIMEOUT', 10))
        )
        
        self.redis = RedisConfig(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB', 0))
        )
        
        self.web = WebConfig(
            enabled=os.getenv('WEB_API_ENABLED', 'false').lower() == 'true',
            host=os.getenv('WEB_HOST', '0.0.0.0'),
            port=int(os.getenv('WEB_PORT', 8080)),
            secret_key=os.getenv('WEB_SECRET_KEY', ''),
            cors_origins=self._parse_list(os.getenv('CORS_ORIGINS', '*'))
        )
        
        self.sharding = ShardingConfig(
            enabled=os.getenv('SHARDING_ENABLED', 'false').lower() == 'true',
            shard_count=self._parse_int(os.getenv('SHARD_COUNT')),
            shard_ids=self._parse_list(os.getenv('SHARD_IDS')),
            auto_shard=os.getenv('AUTO_SHARD', 'true').lower() == 'true'
        )
        
        self.node = NodeConfig(
            node_id=os.getenv('NODE_ID', 'node-1'),
            cluster_name=os.getenv('CLUSTER_NAME', 'discord-bot-cluster'),
            is_primary=os.getenv('IS_PRIMARY_NODE', 'true').lower() == 'true',
            heartbeat_interval=int(os.getenv('NODE_HEARTBEAT', 30))
        )
    
    def _parse_list(self, value: str) -> list:
        """Parse comma-separated string to list"""
        if not value:
            return []
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _parse_int(self, value: str) -> Optional[int]:
        """Parse string to int or return None"""
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            'token': '***HIDDEN***',  # Don't expose token
            'prefix': self.prefix,
            'owner_ids': self.owner_ids,
            'embed_color': hex(self.embed_color),
            'log_level': self.log_level,
            'database': self.database.__dict__,
            'lavalink': self.lavalink.__dict__,
            'redis': self.redis.__dict__,
            'web': self.web.__dict__,
            'sharding': self.sharding.__dict__,
            'node': self.node.__dict__
        }
    
    def validate(self) -> list:
        """Validate configuration and return list of errors"""
        errors = []
        
        if not self.token:
            errors.append("Discord token is required")
        
        if self.database.type == "mongodb" and not self.database.mongodb_uri:
            errors.append("MongoDB URI is required when using MongoDB")
        
        if self.web.enabled and not self.web.secret_key:
            errors.append("Web secret key is required when web API is enabled")
        
        return errors

# Global config instance
config = Config()