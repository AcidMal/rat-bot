import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Info(commands.Cog):
    """Information commands for users and servers."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='userinfo', description="Get information about a user")
    @app_commands.describe(member="The member to get information about")
    async def userinfo(self, ctx, member: discord.Member = None):
        """Get information about a user."""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 User Information",
            color=member.color
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        embed.add_field(name="Name", value=member.display_name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Created", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown", inline=True)
        embed.add_field(name="Status", value=str(member.status).title(), inline=True)
        embed.add_field(name="Top Role", value=member.top_role.mention, inline=True)
        
        # Add roles
        roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
        if roles:
            roles_text = " ".join(roles[:10])  # Limit to first 10 roles
            if len(roles) > 10:
                roles_text += f" and {len(roles) - 10} more..."
            embed.add_field(name="Roles", value=roles_text, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='serverinfo', description="Get information about the current server")
    async def serverinfo(self, ctx):
        """Get information about the current server."""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"🏠 Server Information",
            color=discord.Color.blue()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="Name", value=guild.name, inline=True)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        
        # Channel breakdown
        text_channels = len([c for c in guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len([c for c in guild.channels if isinstance(c, discord.CategoryChannel)])
        
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Categories", value=categories, inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='roleinfo', description="Get information about a role")
    @app_commands.describe(role="The role to get information about")
    async def roleinfo(self, ctx, role: discord.Role):
        """Get information about a role."""
        embed = discord.Embed(
            title=f"🎭 Role Information",
            color=role.color
        )
        
        embed.add_field(name="Name", value=role.name, inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        embed.add_field(name="Hoisted", value="Yes" if role.hoist else "No", inline=True)
        embed.add_field(name="Created", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
        
        # Permissions
        perms = []
        for perm, value in role.permissions:
            if value:
                perms.append(perm.replace('_', ' ').title())
        
        if perms:
            embed.add_field(name="Key Permissions", value=", ".join(perms[:5]), inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='channelinfo', description="Get information about a channel")
    @app_commands.describe(channel="The channel to get information about")
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        """Get information about a channel."""
        channel = channel or ctx.channel
        
        embed = discord.Embed(
            title=f"📺 Channel Information",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Name", value=channel.name, inline=True)
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(name="Type", value=str(channel.type).title(), inline=True)
        embed.add_field(name="Category", value=channel.category.name if channel.category else "None", inline=True)
        embed.add_field(name="Position", value=channel.position, inline=True)
        embed.add_field(name="Created", value=channel.created_at.strftime("%Y-%m-%d"), inline=True)
        
        # Topic
        if hasattr(channel, 'topic') and channel.topic:
            embed.add_field(name="Topic", value=channel.topic[:100] + "..." if len(channel.topic) > 100 else channel.topic, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='botinfo', description="Get detailed information about the bot")
    async def botinfo(self, ctx):
        """Get detailed information about the bot."""
        embed = discord.Embed(
            title=f"🤖 {self.bot.user.name} Information",
            color=discord.Color.blue()
        )
        
        if self.bot.user.avatar:
            embed.set_thumbnail(url=self.bot.user.avatar.url)
        
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Created", value=self.bot.user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Python Version", value="3.8+", inline=True)
        
        # Uptime calculation
        uptime = datetime.utcnow() - self.bot.user.created_at
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot)) 