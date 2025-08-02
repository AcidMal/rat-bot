import discord
from discord.ext import commands
from discord import app_commands
import config
import platform
import psutil
import time

class Utility(commands.Cog):
    """Utility commands for various helpful functions."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='ping', description="Check the bot's latency")
    async def ping(self, ctx):
        """Check the bot's latency."""
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='uptime', description="Show bot uptime")
    async def uptime(self, ctx):
        """Show bot uptime."""
        uptime = time.time() - self.bot.start_time
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        
        uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"**{uptime_str}**",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='system', description="Show system information")
    async def system(self, ctx):
        """Show system information."""
        embed = discord.Embed(
            title="💻 System Information",
            color=discord.Color.blue()
        )
        
        # CPU info
        cpu_percent = psutil.cpu_percent()
        embed.add_field(name="CPU Usage", value=f"{cpu_percent}%", inline=True)
        
        # Memory info
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_used = memory.used / (1024**3)  # GB
        memory_total = memory.total / (1024**3)  # GB
        
        embed.add_field(name="Memory Usage", value=f"{memory_percent}% ({memory_used:.1f}GB / {memory_total:.1f}GB)", inline=True)
        
        # Disk info
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_used = disk.used / (1024**3)  # GB
        disk_total = disk.total / (1024**3)  # GB
        
        embed.add_field(name="Disk Usage", value=f"{disk_percent}% ({disk_used:.1f}GB / {disk_total:.1f}GB)", inline=True)
        
        # Platform info
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='invite', description="Get bot invite link")
    async def invite(self, ctx):
        """Get bot invite link."""
        embed = discord.Embed(
            title="🔗 Bot Invite Link",
            description="Click the link below to invite the bot to your server!",
            color=discord.Color.blue()
        )
        
        # Generate invite link with necessary permissions
        permissions = discord.Permissions(
            send_messages=True,
            read_message_history=True,
            use_slash_commands=True,
            connect=True,
            speak=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            embed_links=True,
            attach_files=True,
            read_messages=True
        )
        
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions
        )
        
        embed.add_field(name="Invite Link", value=f"[Click here to invite]({invite_url})", inline=False)
        embed.add_field(name="Required Permissions", value="Send Messages, Read Message History, Use Slash Commands, Connect, Speak, Manage Messages, Kick Members, Ban Members", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='support', description="Get support information")
    async def support(self, ctx):
        """Get support information."""
        embed = discord.Embed(
            title="🆘 Support Information",
            description="Need help with the bot? Here's how to get support:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Bot Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=config.BOT_PREFIX, inline=True)
        embed.add_field(name="Commands", value=f"`{config.BOT_PREFIX}help`", inline=True)
        
        embed.add_field(
            name="Common Issues",
            value="• **Commands not working**: Check bot permissions\n• **Music not playing**: Ensure LavaLink is running\n• **Slash commands missing**: Wait a few minutes for sync",
            inline=False
        )
        
        embed.add_field(
            name="Getting Help",
            value="• Use `/help` to see all commands\n• Check bot permissions in server settings\n• Ensure the bot has the required permissions",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='about', description="Show information about the bot")
    async def about(self, ctx):
        """Show information about the bot."""
        embed = discord.Embed(
            title=f"🤖 About {config.BOT_NAME}",
            description="A feature-rich Discord bot with moderation, music, and utility commands.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=config.BOT_PREFIX, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
        embed.add_field(
            name="Features",
            value="• **Moderation**: Kick, ban, warn, clear messages\n• **Music**: High-quality audio with LavaLink\n• **Utility**: Server info, user info, system stats\n• **Fun**: Games, random generators, entertainment\n• **Custom Commands**: Server-specific commands",
            inline=False
        )
        
        embed.add_field(
            name="Commands",
            value=f"Use `{config.BOT_PREFIX}help` to see all available commands!",
            inline=False
        )
        
        embed.set_footer(text="Built with Discord.py and LavaLink")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot)) 