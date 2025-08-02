import discord
from discord.ext import commands
from discord import app_commands
import config

class General(commands.Cog):
    """General utility commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='info', description="Display bot information")
    async def info(self, ctx):
        """Display bot information."""
        embed = discord.Embed(
            title=f"🤖 {config.BOT_NAME} Information",
            color=discord.Color.blue()
        )
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=config.BOT_PREFIX, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Uptime", value="Online", inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='help', description="Show help menu")
    async def help_command(self, ctx):
        """Display help information."""
        embed = discord.Embed(
            title=f"📚 {config.BOT_NAME} Help",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        
        # Get all cogs and their commands
        for cog_name, cog in self.bot.cogs.items():
            if cog_name.lower() not in ["general", "utility"]:  # Skip general and utility cogs as we handle them separately
                cog_commands = [cmd.name for cmd in cog.get_commands() if not cmd.hidden]
                if cog_commands:
                    embed.add_field(
                        name=f"**{cog_name}**",
                        value=", ".join([f"`{config.BOT_PREFIX}{cmd}`" for cmd in cog_commands]),
                        inline=False
                    )
        
        # Add general commands
        general_commands = ["info", "help", "echo"]
        embed.add_field(
            name="**General**",
            value=", ".join([f"`{config.BOT_PREFIX}{cmd}`" for cmd in general_commands]),
            inline=False
        )
        
        # Add utility commands
        utility_commands = ["ping", "uptime", "system", "invite", "support", "about"]
        embed.add_field(
            name="**Utility**",
            value=", ".join([f"`{config.BOT_PREFIX}{cmd}`" for cmd in utility_commands]),
            inline=False
        )
        
        embed.add_field(
            name="**Need Help?**",
            value=f"• Use `{config.BOT_PREFIX}help <command>` for detailed help\n• Use `/help` for slash command help\n• Use `{config.BOT_PREFIX}support` for troubleshooting",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='echo', description="Make the bot repeat your message")
    @app_commands.describe(message="The message to repeat")
    async def echo(self, ctx, *, message: str):
        """Make the bot repeat your message."""
        await ctx.send(message)

async def setup(bot):
    await bot.add_cog(General(bot)) 