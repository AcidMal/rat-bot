import discord
from discord.ext import commands
from discord import app_commands
import config

class Admin(commands.Cog):
    """Admin commands for server management."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='clear', description="Clear messages from the channel")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def clear(self, ctx, amount: int = 10):
        """Clear messages from the channel."""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please specify a number between 1 and 100.")
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            await ctx.send(f"✅ Deleted {len(deleted) - 1} messages.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages.")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {e}")
    
    @commands.hybrid_command(name='announce', description="Make an announcement")
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(message="The announcement message")
    async def announce(self, ctx, *, message: str):
        """Make an announcement."""
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Announced by {ctx.author.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='serverinfo', description="Display server information")
    async def serverinfo(self, ctx):
        """Display server information."""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name} Information",
            color=discord.Color.blue()
        )
        
        # Basic info
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        
        # Channel info
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Categories", value=categories, inline=True)
        
        # Role info
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
        
        # Server features
        if guild.features:
            features = ", ".join(guild.features)
            embed.add_field(name="Features", value=features, inline=False)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='userinfo', description="Display user information")
    @app_commands.describe(user="The user to get information about")
    async def userinfo(self, ctx, user: discord.Member = None):
        """Display user information."""
        if user is None:
            user = ctx.author
        
        embed = discord.Embed(
            title=f"👤 {user.display_name} Information",
            color=user.color
        )
        
        # Basic info
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Display Name", value=user.display_name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)
        
        # Member info
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="Top Role", value=user.top_role.mention, inline=True)
        
        # Status
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        status = status_emoji.get(user.status, "⚫")
        embed.add_field(name="Status", value=f"{status} {user.status.name.title()}", inline=True)
        
        # Roles
        roles = [role.mention for role in user.roles[1:]]  # Skip @everyone
        if roles:
            roles_text = ", ".join(roles[:10])  # Limit to 10 roles
            if len(roles) > 10:
                roles_text += f" and {len(roles) - 10} more..."
            embed.add_field(name="Roles", value=roles_text, inline=False)
        
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='roleinfo', description="Display role information")
    @app_commands.describe(role="The role to get information about")
    async def roleinfo(self, ctx, role: discord.Role):
        """Display role information."""
        embed = discord.Embed(
            title=f"🎭 {role.name} Information",
            color=role.color
        )
        
        embed.add_field(name="Name", value=role.name, inline=True)
        embed.add_field(name="ID", value=role.id, inline=True)
        embed.add_field(name="Color", value=str(role.color), inline=True)
        
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Mentionable", value="Yes" if role.mentionable else "No", inline=True)
        
        # Permissions
        permissions = []
        for perm, value in role.permissions:
            if value:
                permissions.append(perm.replace('_', ' ').title())
        
        if permissions:
            perms_text = ", ".join(permissions[:10])
            if len(permissions) > 10:
                perms_text += f" and {len(permissions) - 10} more..."
            embed.add_field(name="Key Permissions", value=perms_text, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='botinfo', description="Display bot information")
    async def botinfo(self, ctx):
        """Display bot information."""
        embed = discord.Embed(
            title=f"🤖 {config.BOT_NAME} Information",
            color=discord.Color.blue()
        )
        
        # Bot info
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=config.BOT_PREFIX, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        
        embed.add_field(name="Users", value=len(self.bot.users), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Commands", value=len(self.bot.commands), inline=True)
        
        # System info
        import platform
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Admin(bot)) 