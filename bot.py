import asyncio
import logging
import os
import discord
from discord.ext import commands
import config
from database import db
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord_bot')

# Define Gateway Intents
intents = discord.Intents.default()
intents.message_content = True  # Required for accessing message.content
intents.members = True          # Required for member-related events and info

# Initialize bot with sharding support
bot = commands.Bot(
    command_prefix=config.BOT_PREFIX, 
    intents=intents,
    shard_count=config.SHARD_COUNT if hasattr(config, 'SHARD_COUNT') else None,
    shard_ids=config.SHARD_IDS if hasattr(config, 'SHARD_IDS') else None
)

# Track bot start time for uptime command
bot.start_time = time.time()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot ID: {bot.user.id}')
    logger.info(f'Connected to {len(bot.guilds)} guilds.')
    
    # Log shard information
    if bot.shard_count:
        logger.info(f'Running on shard {bot.shard_id} of {bot.shard_count}')
        total_guilds = sum(len(shard.guilds) for shard in bot.shards.values())
        logger.info(f'Total guilds across all shards: {total_guilds}')
    else:
        logger.info('Running without sharding')
    
    # Set bot status
    await bot.change_presence(activity=discord.Game(name=f"{config.BOT_PREFIX}help | {config.BOT_NAME}"))

    # Sync slash commands
    logger.info("Syncing slash commands...")
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.event
async def on_guild_join(guild):
    """Event triggered when the bot joins a new guild."""
    logger.info(f'Joined guild: {guild.name} (id: {guild.id}) on shard {guild.shard_id}')
    # Sync commands for the new guild
    try:
        await bot.tree.sync(guild=guild)
        logger.info(f"Synced commands for guild: {guild.name}")
    except Exception as e:
        logger.error(f"Failed to sync commands for guild {guild.name}: {e}")

@bot.event
async def on_guild_remove(guild):
    """Event triggered when the bot leaves a guild."""
    logger.info(f'Left guild: {guild.name} (id: {guild.id}) from shard {guild.shard_id}')

@bot.event
async def on_shard_ready(shard_id):
    """Event triggered when a shard is ready."""
    logger.info(f'Shard {shard_id} is ready!')

@bot.event
async def on_shard_disconnect(shard_id):
    """Event triggered when a shard disconnects."""
    logger.warning(f'Shard {shard_id} disconnected!')

@bot.event
async def on_shard_resumed(shard_id):
    """Event triggered when a shard resumes."""
    logger.info(f'Shard {shard_id} resumed!')

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for prefix commands."""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Type `!help` for a list of commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(f"❌ You don't have permission to use this command. Missing: {', '.join(error.missing_permissions)}")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}. Please check `!help {ctx.command.name}`.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument provided: {error}. Please check `!help {ctx.command.name}`.")
    else:
        logger.error(f'Unhandled command error: {error}')
        await ctx.send("❌ An error occurred while executing the command.")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    """Error handler for slash commands."""
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, discord.app_commands.BotMissingPermissions):
        await interaction.response.send_message("❌ I don't have the required permissions to execute this command.", ephemeral=True)
    else:
        logger.error(f'Slash command error: {error}')
        await interaction.response.send_message("❌ An error occurred while executing the command.", ephemeral=True)

@bot.event
async def on_command(ctx):
    """Track command usage in database."""
    try:
        db.increment_user_stats(ctx.author.id, ctx.guild.id, "commands")
    except Exception as e:
        logger.error(f"Error tracking command usage: {e}")

@bot.event
async def on_message(message):
    """Track message count and handle custom commands."""
    if not message.author.bot and message.guild:
        try:
            db.increment_user_stats(message.author.id, message.guild.id, "messages")
        except Exception as e:
            logger.error(f"Error tracking message: {e}")

    # Process commands (including custom commands)
    await bot.process_commands(message)

async def load_extensions():
    """Load all cog extensions."""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded extension: {filename}")
            except Exception as e:
                logger.error(f"Failed to load extension {filename}: {e}")

async def main():
    """Main function to run the bot."""
    try:
        logger.info("Starting bot...")
        # Load extensions before running the bot
        await load_extensions()
        await bot.start(config.DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 