import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Configuration
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Handle guild_id with proper fallback
    guild_id_str = os.getenv('GUILD_ID', '0')
    try:
        GUILD_ID = int(guild_id_str) if guild_id_str != 'your_guild_id_here' else 0
    except ValueError:
        GUILD_ID = 0
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/ratbot')
    
    # Lavalink Configuration
    LAVALINK_HOST = os.getenv('LAVALINK_HOST', 'localhost')
    LAVALINK_PORT = int(os.getenv('LAVALINK_PORT', 2333))
    LAVALINK_PASSWORD = os.getenv('LAVALINK_PASSWORD', 'youshallnotpass')
    
    # Bot Configuration
    PREFIX = os.getenv('PREFIX', '!')
    # Handle hex color values properly
    embed_color_str = os.getenv('EMBED_COLOR', '0x00ff00')
    if embed_color_str.startswith('0x'):
        EMBED_COLOR = int(embed_color_str, 16)
    else:
        EMBED_COLOR = int(embed_color_str)
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # ModLog Configuration
    modlog_channel_str = os.getenv('MODLOG_CHANNEL_ID', '0')
    try:
        MODLOG_CHANNEL_ID = int(modlog_channel_str) if modlog_channel_str != 'your_modlog_channel_id_here' else 0
    except ValueError:
        MODLOG_CHANNEL_ID = 0 