import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Configuration
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD_ID = int(os.getenv('GUILD_ID', 0))
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/ratbot')
    
    # Lavalink Configuration
    LAVALINK_HOST = os.getenv('LAVALINK_HOST', 'localhost')
    LAVALINK_PORT = int(os.getenv('LAVALINK_PORT', 2333))
    LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')
    
    # Bot Configuration
    PREFIX = os.getenv('PREFIX', '!')
    EMBED_COLOR = int(os.getenv('EMBED_COLOR', 0x00ff00))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # ModLog Configuration
    MODLOG_CHANNEL_ID = int(os.getenv('MODLOG_CHANNEL_ID', 0)) 