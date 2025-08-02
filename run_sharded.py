#!/usr/bin/env python3
"""
Simple Sharded Bot Runner
This script runs the bot with automatic sharding enabled.
"""

import os
import sys
import asyncio
import logging
from bot import bot, load_extensions
import config

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sharded_bot')

async def main():
    """Main function to run the sharded bot."""
    try:
        logger.info("Starting sharded bot...")
        
        # Load extensions
        await load_extensions()
        
        # Run the bot with automatic sharding
        await bot.start(config.DISCORD_TOKEN)
        
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 