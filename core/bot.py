import discord
from discord.ext import commands, tasks
import asyncio
import sys
import os
from typing import Optional, List
from datetime import datetime, timezone
import wavelink
import redis.asyncio as aioredis
from loguru import logger

from config import config
from database import get_database
from core.node_manager import NodeManager
from core.shard_manager import ShardManager

class AdvancedBot(commands.AutoShardedBot if config.sharding.enabled else commands.Bot):
    """Advanced Discord Bot with sharding, node meshing, and database integration"""
    
    def __init__(self):
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        intents.presences = True
        
        # Initialize bot with sharding if enabled
        if config.sharding.enabled:
            super().__init__(
                command_prefix=self._get_prefix,
                intents=intents,
                help_command=None,
                shard_count=config.sharding.shard_count,
                shard_ids=config.sharding.shard_ids
            )
        else:
            super().__init__(
                command_prefix=self._get_prefix,
                intents=intents,
                help_command=None
            )
        
        # Core components
        self.db = None
        self.redis = None
        self.node_manager = None
        self.shard_manager = None
        
        # Bot state
        self.start_time = datetime.now(timezone.utc)
        self.is_ready = False
        
        # Music system
        self.lavalink_nodes = []
        
        # Statistics
        self.stats = {
            'commands_executed': 0,
            'songs_played': 0,
            'guilds_joined': 0,
            'guilds_left': 0
        }
    
    async def _get_prefix(self, bot, message):
        """Dynamic prefix getter"""
        if not message.guild:
            return config.prefix
        
        try:
            guild_config = await self.db.get_guild_config(message.guild.id)
            return guild_config.get('prefix', config.prefix)
        except:
            return config.prefix
    
    async def setup_hook(self):
        """Initialize bot components"""
        logger.info("🚀 Starting bot setup...")
        
        # Initialize database
        await self._setup_database()
        
        # Initialize Redis for node communication
        await self._setup_redis()
        
        # Initialize node manager
        await self._setup_node_manager()
        
        # Initialize shard manager if sharding is enabled
        if config.sharding.enabled:
            await self._setup_shard_manager()
        
        # Setup Lavalink
        await self._setup_lavalink()
        
        # Load extensions
        await self._load_extensions()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("✅ Bot setup completed!")
    
    async def _setup_database(self):
        """Initialize database connection"""
        try:
            self.db = await get_database()
            logger.info("📊 Database connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    async def _setup_redis(self):
        """Initialize Redis connection for node communication"""
        try:
            self.redis = aioredis.from_url(
                f"redis://{config.redis.host}:{config.redis.port}",
                password=config.redis.password,
                db=config.redis.db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("🔗 Redis connected successfully")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            self.redis = None
    
    async def _setup_node_manager(self):
        """Initialize node manager for clustering"""
        if self.redis:
            self.node_manager = NodeManager(self, self.redis)
            await self.node_manager.initialize()
            logger.info("🌐 Node manager initialized")
    
    async def _setup_shard_manager(self):
        """Initialize shard manager"""
        self.shard_manager = ShardManager(self)
        await self.shard_manager.initialize()
        logger.info("⚡ Shard manager initialized")
    
    async def _setup_lavalink(self):
        """Setup Lavalink connection"""
        try:
            # Create Lavalink node
            node = wavelink.Node(
                uri=f"{'https' if config.lavalink.ssl else 'http'}://{config.lavalink.host}:{config.lavalink.port}",
                password=config.lavalink.password,
                heartbeat=config.lavalink.heartbeat
            )
            
            # Connect to Lavalink
            await wavelink.Pool.connect(nodes=[node], client=self)
            self.lavalink_nodes.append(node)
            
            logger.info(f"🎵 Connected to Lavalink: {config.lavalink.host}:{config.lavalink.port}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to connect to Lavalink: {e}")
    
    async def _load_extensions(self):
        """Load all bot extensions"""
        extensions = [
            'cogs.music',
            'cogs.moderation',
            'cogs.general',
            'cogs.admin',
            'cogs.fun',
            'cogs.utility',
            'cogs.voice_channels'
        ]
        
        for extension in extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"📦 Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"❌ Failed to load extension {extension}: {e}")
    
    def _start_background_tasks(self):
        """Start background tasks"""
        self.status_updater.start()
        self.stats_updater.start()
        
        if self.node_manager:
            self.node_heartbeat.start()
    
    @tasks.loop(minutes=5)
    async def status_updater(self):
        """Update bot status periodically"""
        try:
            guild_count = len(self.guilds)
            user_count = sum(guild.member_count for guild in self.guilds if guild.member_count)
            
            activities = [
                discord.Activity(type=discord.ActivityType.listening, name=f"{config.prefix}help | {guild_count} servers"),
                discord.Activity(type=discord.ActivityType.watching, name=f"{user_count:,} users"),
                discord.Activity(type=discord.ActivityType.playing, name="Advanced Discord Bot"),
            ]
            
            activity = activities[self.stats['commands_executed'] % len(activities)]
            await self.change_presence(activity=activity)
        except Exception as e:
            logger.error(f"Error updating status: {e}")
    
    @tasks.loop(minutes=10)
    async def stats_updater(self):
        """Update global statistics"""
        try:
            if self.db:
                await self.db.set_global_config('bot_stats', {
                    'guilds': len(self.guilds),
                    'users': sum(guild.member_count for guild in self.guilds if guild.member_count),
                    'uptime': (datetime.now(timezone.utc) - self.start_time).total_seconds(),
                    'commands_executed': self.stats['commands_executed'],
                    'songs_played': self.stats['songs_played'],
                    'last_updated': datetime.now(timezone.utc).isoformat()
                })
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    @tasks.loop(seconds=30)
    async def node_heartbeat(self):
        """Send heartbeat to other nodes"""
        if self.node_manager:
            await self.node_manager.send_heartbeat()
    
    @status_updater.before_loop
    @stats_updater.before_loop
    @node_heartbeat.before_loop
    async def wait_until_ready(self):
        """Wait until bot is ready before starting tasks"""
        await super().wait_until_ready()
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.is_ready = True
        logger.info(f"🤖 {self.user.name} is ready!")
        logger.info(f"📊 Connected to {len(self.guilds)} guilds")
        logger.info(f"👥 Serving {sum(guild.member_count for guild in self.guilds if guild.member_count):,} users")
        
        if config.sharding.enabled:
            logger.info(f"⚡ Shards: {self.shard_count}")
        
        # Register with node manager
        if self.node_manager:
            await self.node_manager.register_node()
    
    async def on_guild_join(self, guild):
        """Called when bot joins a guild"""
        logger.info(f"📈 Joined guild: {guild.name} ({guild.id})")
        self.stats['guilds_joined'] += 1
        
        # Initialize guild config
        if self.db:
            await self.db.get_guild_config(guild.id)
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        logger.info(f"📉 Left guild: {guild.name} ({guild.id})")
        self.stats['guilds_left'] += 1
    
    async def on_command(self, ctx):
        """Called before command execution"""
        self.stats['commands_executed'] += 1
        
        # Log command usage
        logger.info(f"💻 Command: {ctx.command.name} | User: {ctx.author} | Guild: {ctx.guild}")
        
        # Update user stats
        if self.db:
            await self.db.increment_user_stat(ctx.author.id, 'commands_used')
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Missing Permissions",
                description="You don't have permission to use this command.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: `{error.param.name}`",
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
        
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="⏰ Command on Cooldown",
                description=f"Try again in {error.retry_after:.1f} seconds.",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        logger.error(f"Command error in {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred. The developers have been notified.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    async def on_wavelink_track_end(self, payload):
        """Handle track end events"""
        self.stats['songs_played'] += 1
    
    async def close(self):
        """Clean shutdown"""
        logger.info("🛑 Shutting down bot...")
        
        # Stop background tasks
        if hasattr(self, 'status_updater'):
            self.status_updater.cancel()
        if hasattr(self, 'stats_updater'):
            self.stats_updater.cancel()
        if hasattr(self, 'node_heartbeat'):
            self.node_heartbeat.cancel()
        
        # Cleanup components
        if self.node_manager:
            await self.node_manager.cleanup()
        
        if self.redis:
            await self.redis.close()
        
        if self.db:
            await self.db.disconnect()
        
        await super().close()
        logger.info("✅ Bot shutdown complete")

def create_bot() -> AdvancedBot:
    """Factory function to create bot instance"""
    return AdvancedBot()