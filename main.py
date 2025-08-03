#!/usr/bin/env python3

import asyncio
import sys
import os
import signal
from loguru import logger
from core import create_bot
from config import config

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    level=config.log_level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

logger.add(
    config.log_file,
    level=config.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)

async def main():
    """Main function to run the bot"""
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(config.log_file), exist_ok=True)
    
    logger.info("Starting Advanced Discord Bot...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Configuration loaded from .env")
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logger.error("Configuration errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        logger.error("Please fix the configuration errors and restart the bot")
        sys.exit(1)
    
    # Create and run bot
    bot = create_bot()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        asyncio.create_task(bot.close())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        logger.info("Bot is starting up...")
        await bot.start(config.token)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
    finally:
        if not bot.is_closed():
            logger.info("Closing bot connection...")
            await bot.close()
        logger.info("Bot shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)