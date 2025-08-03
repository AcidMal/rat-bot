import discord
from discord.ext import commands
import asyncio
import wavelink
import logging
import os
import sys
import subprocess
import psutil
from config import Config
from database.models import Database

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RatBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.PREFIX,
            intents=intents,
            help_command=None  # We'll use our custom help command
        )
        
        self.db = None
        self.lavalink_process = None
        
    async def setup_hook(self):
        """Initialize bot components"""
        logger.info("Setting up bot...")
        
        # Initialize database
        try:
            self.db = Database(Config.DATABASE_URL)
            await self.db.connect()
            logger.info("Database connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            sys.exit(1)
        
        # Start Lavalink server
        await self.start_lavalink()
        
        # Load cogs
        await self.load_cogs()
        
        logger.info("Bot setup complete!")
    
    async def start_lavalink(self):
        """Start Lavalink server as a child process"""
        try:
            # Check if Lavalink.jar exists
            if not os.path.exists('Lavalink.jar'):
                logger.warning("Lavalink.jar not found. Please download it from https://github.com/lavalink-devs/Lavalink/releases")
                return
            
            # Start Lavalink process
            self.lavalink_process = subprocess.Popen([
                'java', '-jar', 'Lavalink.jar'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            logger.info("Lavalink server started")
            
            # Wait a moment for Lavalink to start
            await asyncio.sleep(5)
            
        except Exception as e:
            logger.error(f"Failed to start Lavalink: {e}")
    
    async def load_cogs(self):
        """Load all bot cogs"""
        cogs = [
            'cogs.general',
            'cogs.music',
            'cogs.moderation'
        ]
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"Loaded cog: {cog}")
            except Exception as e:
                logger.error(f"Failed to load cog {cog}: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user.name} ({self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name=f"{Config.PREFIX}help"
            )
        )
        
        # Connect to Lavalink
        try:
            node = wavelink.Node(
                uri=f"http://{Config.LAVALINK_HOST}:{Config.LAVALINK_PORT}",
                password=Config.LAVALINK_PASSWORD
            )
            await wavelink.Pool.connect(nodes=[node], client=self)
            logger.info("Connected to Lavalink server")
        except Exception as e:
            logger.error(f"Failed to connect to Lavalink: {e}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission Error",
                description="You don't have permission to use this command!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: {error.param.name}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description="One or more arguments are invalid.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        logger.error(f"Command error in {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ Error",
            description="An unexpected error occurred. Please try again later.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    async def close(self):
        """Clean up resources when bot shuts down"""
        logger.info("Shutting down bot...")
        
        # Close database connection
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")
        
        # Stop Lavalink process
        if self.lavalink_process:
            self.lavalink_process.terminate()
            try:
                self.lavalink_process.wait(timeout=5)
                logger.info("Lavalink server stopped")
            except subprocess.TimeoutExpired:
                self.lavalink_process.kill()
                logger.warning("Force killed Lavalink server")
        
        await super().close()

def main():
    """Main function to run the bot"""
    if not Config.TOKEN:
        logger.error("Discord token not found! Please set DISCORD_TOKEN in your environment variables.")
        sys.exit(1)
    
    bot = RatBot()
    
    try:
        bot.run(Config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 