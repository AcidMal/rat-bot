import discord
from discord.ext import commands
import time
import psutil
import platform
from datetime import datetime, timezone
from typing import Optional

class General(commands.Cog):
    """General utility commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="ping")
    async def ping(self, ctx):
        """Show bot latency"""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        # Calculate latencies
        api_latency = (end_time - start_time) * 1000
        websocket_latency = self.bot.latency * 1000
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        embed.add_field(name="API Latency", value=f"{api_latency:.2f}ms", inline=True)
        embed.add_field(name="WebSocket Latency", value=f"{websocket_latency:.2f}ms", inline=True)
        
        # Add shard info if sharded
        if hasattr(self.bot, 'shard_count') and self.bot.shard_count:
            shard_id = ctx.guild.shard_id if ctx.guild else 0
            embed.add_field(name="Shard", value=f"{shard_id}/{self.bot.shard_count}", inline=True)
        
        await message.edit(content="", embed=embed)
    
    @commands.command(name="info", aliases=["botinfo"])
    async def info(self, ctx):
        """Show bot information"""
        # Get system info
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        cpu_usage = process.cpu_percent()
        
        # Calculate uptime
        uptime = datetime.now(timezone.utc) - self.bot.start_time
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=0x7289da
        )
        
        # Bot stats
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Users", value=f"{len(self.bot.users):,}", inline=True)
        embed.add_field(name="Commands", value=f"{len(self.bot.commands)}", inline=True)
        
        # System stats
        embed.add_field(name="Memory Usage", value=f"{memory_usage:.1f} MB", inline=True)
        embed.add_field(name="CPU Usage", value=f"{cpu_usage:.1f}%", inline=True)
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        
        # Technical info
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        
        if hasattr(self.bot, 'shard_count') and self.bot.shard_count:
            embed.add_field(name="Shards", value=f"{self.bot.shard_count}", inline=True)
        
        # Database info
        if self.bot.db:
            try:
                stats = await self.bot.db.get_global_stats()
                embed.add_field(name="Commands Executed", value=f"{stats.get('total_commands_used', 0):,}", inline=True)
                embed.add_field(name="Songs Played", value=f"{stats.get('total_songs_played', 0):,}", inline=True)
            except:
                pass
        
        embed.set_footer(text=f"Made with ❤️ | Bot ID: {self.bot.user.id}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="serverinfo", aliases=["guildinfo"])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        """Show server information"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=0x7289da,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Basic info
        embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        embed.add_field(name="Members", value=f"{guild.member_count:,}", inline=True)
        
        # Counts
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(name="Text Channels", value=text_channels, inline=True)
        embed.add_field(name="Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="Categories", value=categories, inline=True)
        
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Emojis", value=len(guild.emojis), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count or 0, inline=True)
        
        # Features
        if guild.features:
            features = []
            feature_names = {
                'COMMUNITY': 'Community Server',
                'VERIFIED': 'Verified',
                'PARTNERED': 'Partnered',
                'DISCOVERABLE': 'Server Discovery',
                'FEATURABLE': 'Featurable',
                'INVITE_SPLASH': 'Invite Splash',
                'VIP_REGIONS': 'VIP Voice Regions',
                'VANITY_URL': 'Vanity URL',
                'MORE_EMOJI': 'More Emoji',
                'NEWS': 'News Channels',
                'BANNER': 'Server Banner',
                'ANIMATED_ICON': 'Animated Icon'
            }
            
            for feature in guild.features:
                features.append(feature_names.get(feature, feature.title().replace('_', ' ')))
            
            if features:
                embed.add_field(name="Features", value="\n".join(features[:5]), inline=False)
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", aliases=["whois"])
    async def userinfo(self, ctx, member: Optional[discord.Member] = None):
        """Show user information"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 {member}",
            color=member.color if member.color != discord.Color.default() else 0x7289da,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Basic info
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Created", value=f"<t:{int(member.created_at.timestamp())}:R>", inline=True)
        
        if isinstance(member, discord.Member):
            embed.add_field(name="Joined", value=f"<t:{int(member.joined_at.timestamp())}:R>", inline=True)
            
            # Roles
            if len(member.roles) > 1:
                roles = [role.mention for role in member.roles[1:]]  # Skip @everyone
                roles_text = " ".join(roles)
                if len(roles_text) > 1024:
                    roles_text = f"{len(roles)} roles"
                embed.add_field(name=f"Roles ({len(roles)})", value=roles_text, inline=False)
            
            # Permissions
            if member.guild_permissions.administrator:
                embed.add_field(name="Key Permissions", value="Administrator", inline=False)
            else:
                key_perms = []
                perms_to_check = [
                    ('manage_guild', 'Manage Server'),
                    ('manage_channels', 'Manage Channels'),
                    ('manage_messages', 'Manage Messages'),
                    ('manage_roles', 'Manage Roles'),
                    ('kick_members', 'Kick Members'),
                    ('ban_members', 'Ban Members'),
                    ('moderate_members', 'Timeout Members')
                ]
                
                for perm, name in perms_to_check:
                    if getattr(member.guild_permissions, perm):
                        key_perms.append(name)
                
                if key_perms:
                    embed.add_field(name="Key Permissions", value=", ".join(key_perms), inline=False)
        
        # Status and activity
        if hasattr(member, 'status') and member.status != discord.Status.offline:
            status_emoji = {
                discord.Status.online: "🟢",
                discord.Status.idle: "🟡",
                discord.Status.dnd: "🔴",
                discord.Status.offline: "⚫"
            }
            embed.add_field(name="Status", value=f"{status_emoji.get(member.status, '❓')} {member.status.name.title()}", inline=True)
        
        if hasattr(member, 'activities') and member.activities:
            activity = member.activities[0]
            if activity.type == discord.ActivityType.playing:
                embed.add_field(name="Playing", value=activity.name, inline=True)
            elif activity.type == discord.ActivityType.listening:
                embed.add_field(name="Listening to", value=activity.name, inline=True)
            elif activity.type == discord.ActivityType.watching:
                embed.add_field(name="Watching", value=activity.name, inline=True)
            elif activity.type == discord.ActivityType.custom:
                embed.add_field(name="Custom Status", value=str(activity), inline=True)
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, member: Optional[discord.Member] = None):
        """Show user's avatar"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {member}'s Avatar",
            color=member.color if hasattr(member, 'color') and member.color != discord.Color.default() else 0x7289da
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(name="Avatar URL", value=f"[Click here]({member.display_avatar.url})", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="invite")
    async def invite(self, ctx):
        """Get bot invite link"""
        permissions = discord.Permissions(
            read_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True,
            connect=True,
            speak=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
            manage_channels=True,
            manage_roles=True,
            use_slash_commands=True
        )
        
        invite_url = discord.utils.oauth_url(self.bot.user.id, permissions=permissions)
        
        embed = discord.Embed(
            title="🔗 Invite Me!",
            description=f"[Click here to invite me to your server!]({invite_url})",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Features",
            value="• Advanced Music System\n• Moderation Tools\n• Fun Commands\n• And much more!",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="help")
    async def help_command(self, ctx, *, command_name: str = None):
        """Show help information"""
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name.lower())
            if not command:
                embed = discord.Embed(
                    title="❌ Command Not Found",
                    description=f"No command named `{command_name}` found.",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            
            embed = discord.Embed(
                title=f"📖 Help: {command.name}",
                description=command.help or "No description available.",
                color=0x7289da
            )
            
            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(f"`{alias}`" for alias in command.aliases), inline=False)
            
            embed.add_field(name="Usage", value=f"`{ctx.prefix}{command.name} {command.signature}`", inline=False)
            
            await ctx.send(embed=embed)
        else:
            # Show general help
            embed = discord.Embed(
                title="📚 Help Menu",
                description=f"Use `{ctx.prefix}help <command>` for detailed info about a command.",
                color=0x7289da
            )
            
            # Group commands by cog
            cogs = {}
            for command in self.bot.commands:
                if command.cog_name:
                    if command.cog_name not in cogs:
                        cogs[command.cog_name] = []
                    cogs[command.cog_name].append(command)
                else:
                    if "Other" not in cogs:
                        cogs["Other"] = []
                    cogs["Other"].append(command)
            
            # Add fields for each cog
            for cog_name, commands_list in cogs.items():
                if cog_name == "Owner":  # Skip owner commands
                    continue
                
                command_names = [f"`{cmd.name}`" for cmd in commands_list if not cmd.hidden]
                if command_names:
                    embed.add_field(
                        name=f"🔹 {cog_name}",
                        value=" ".join(command_names),
                        inline=False
                    )
            
            embed.set_footer(text=f"Total Commands: {len([cmd for cmd in self.bot.commands if not cmd.hidden])}")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))