import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Bot configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    raise ValueError("No Discord token found. Please set DISCORD_TOKEN in your .env file")

# Bot settings
BOT_PREFIX = "`"
BOT_NAME = "Rat Bot"
BOT_VERSION = "1.0.0"

# Sharding configuration
# Set these values if you want to use sharding
# SHARD_COUNT = 2  # Total number of shards
# SHARD_IDS = [0, 1]  # Which shards this instance should run

# For automatic sharding, leave these as None
# The bot will automatically determine the number of shards needed
SHARD_COUNT = 5  # Set to a number if you want manual sharding
SHARD_IDS = [0, 1, 2, 3, 4]    # Set to a list of shard IDs if you want manual sharding

# Database configuration
DATABASE_PATH = "data/bot.db"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s" 