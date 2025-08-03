import discord
from discord.ext import commands
import platform
import psutil
import time
from datetime import datetime

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.utcnow()
    
    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check the bot's latency"""
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000)
        api_latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        embed.add_field(name="Bot Latency", value=f"{latency}ms", inline=True)
        embed.add_field(name="API Latency", value=f"{api_latency}ms", inline=True)
        
        if latency < 100:
            status = "🟢 Excellent"
        elif latency < 200:
            status = "🟡 Good"
        else:
            status = "🔴 Poor"
        
        embed.add_field(name="Status", value=status, inline=True)
        await message.edit(content="", embed=embed)
    
    @commands.command(name='info')
    async def info(self, ctx):
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=0x00ff00
        )
        
        # Bot info
        embed.add_field(
            name="Bot",
            value=f"**Name:** {self.bot.user.name}\n"
                  f"**ID:** {self.bot.user.id}\n"
                  f"**Created:** {self.bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            inline=False
        )
        
        # System info
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        embed.add_field(
            name="System",
            value=f"**CPU:** {cpu_percent}%\n"
                  f"**Memory:** {memory.percent}%\n"
                  f"**Disk:** {disk.percent}%",
            inline=True
        )
        
        # Bot stats
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        embed.add_field(
            name="Statistics",
            value=f"**Servers:** {len(self.bot.guilds)}\n"
                  f"**Users:** {len(self.bot.users)}\n"
                  f"**Uptime:** {days}d {hours}h {minutes}m",
            inline=True
        )
        
        # Python info
        embed.add_field(
            name="Python",
            value=f"**Version:** {platform.python_version()}\n"
                  f"**Discord.py:** {discord.__version__}",
            inline=True
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='serverinfo', aliases=['server'])
    async def serverinfo(self, ctx):
        """Show server information"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name}",
            color=0x00ff00
        )
        
        # General info
        embed.add_field(
            name="General",
            value=f"**Owner:** {guild.owner.mention}\n"
                  f"**Created:** {guild.created_at.strftime('%Y-%m-%d')}\n"
                  f"**Members:** {guild.member_count}",
            inline=True
        )
        
        # Channel info
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="Channels",
            value=f"**Text:** {text_channels}\n"
                  f"**Voice:** {voice_channels}\n"
                  f"**Categories:** {categories}",
            inline=True
        )
        
        # Role info
        embed.add_field(
            name="Roles",
            value=f"**Total:** {len(guild.roles)}\n"
                  f"**Boosts:** {guild.premium_subscription_count}\n"
                  f"**Boost Level:** {guild.premium_tier}",
            inline=True
        )
        
        # Features
        features = []
        if guild.features:
            for feature in guild.features:
                features.append(f"✅ {feature.replace('_', ' ').title()}")
        
        if features:
            embed.add_field(
                name="Features",
                value="\n".join(features[:5]),  # Show first 5 features
                inline=False
            )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.set_footer(text=f"Server ID: {guild.id}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='userinfo', aliases=['user'])
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show user information"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"👤 {member.display_name}",
            color=member.color if member.color != discord.Color.default() else 0x00ff00
        )
        
        # User info
        embed.add_field(
            name="User",
            value=f"**Name:** {member.name}\n"
                  f"**ID:** {member.id}\n"
                  f"**Created:** {member.created_at.strftime('%Y-%m-%d')}",
            inline=True
        )
        
        # Member info
        embed.add_field(
            name="Member",
            value=f"**Joined:** {member.joined_at.strftime('%Y-%m-%d') if member.joined_at else 'Unknown'}\n"
                  f"**Top Role:** {member.top_role.mention}\n"
                  f"**Status:** {str(member.status).title()}",
            inline=True
        )
        
        # Roles
        roles = [role.mention for role in member.roles[1:]]  # Exclude @everyone
        roles_text = " ".join(roles[:10]) if roles else "No roles"
        if len(roles) > 10:
            roles_text += f"\n... and {len(roles) - 10} more"
        
        embed.add_field(
            name=f"Roles ({len(roles)})",
            value=roles_text,
            inline=False
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='avatar', aliases=['av'])
    async def avatar(self, ctx, member: discord.Member = None):
        """Show user's avatar"""
        member = member or ctx.author
        
        embed = discord.Embed(
            title=f"🖼️ {member.display_name}'s Avatar",
            color=0x00ff00
        )
        
        embed.set_image(url=member.display_avatar.url)
        embed.add_field(
            name="Links",
            value=f"[PNG]({member.display_avatar.replace(format='png').url}) | "
                  f"[JPG]({member.display_avatar.replace(format='jpg').url}) | "
                  f"[WEBP]({member.display_avatar.replace(format='webp').url})",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='invite')
    async def invite(self, ctx):
        """Get bot invite link"""
        embed = discord.Embed(
            title="🔗 Invite Link",
            description="Click the link below to invite me to your server!",
            color=0x00ff00
        )
        
        # Generate invite link with necessary permissions
        permissions = discord.Permissions(
            send_messages=True,
            read_messages=True,
            manage_messages=True,
            kick_members=True,
            ban_members=True,
            moderate_members=True,
            connect=True,
            speak=True,
            use_voice_activation=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            add_reactions=True
        )
        
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permissions
        )
        
        embed.add_field(
            name="Invite Link",
            value=f"[Click here to invite me!]({invite_url})",
            inline=False
        )
        
        embed.add_field(
            name="Required Permissions",
            value="• Send Messages\n"
                  "• Read Messages\n"
                  "• Manage Messages\n"
                  "• Kick Members\n"
                  "• Ban Members\n"
                  "• Moderate Members\n"
                  "• Connect\n"
                  "• Speak\n"
                  "• Use Voice Activity\n"
                  "• Embed Links\n"
                  "• Attach Files\n"
                  "• Read Message History\n"
                  "• Add Reactions",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help(self, ctx, command_name: str = None):
        """Show help information"""
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name)
            if not command:
                embed = discord.Embed(
                    title="❌ Error",
                    description=f"Command `{command_name}` not found.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title=f"📖 Help: {command.name}",
                description=command.help or "No description available.",
                color=0x00ff00
            )
            
            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(command.aliases),
                    inline=False
                )
            
            if command.usage:
                embed.add_field(
                    name="Usage",
                    value=f"`{ctx.prefix}{command.name} {command.usage}`",
                    inline=False
                )
            
            await ctx.send(embed=embed)
        else:
            # Show general help
            embed = discord.Embed(
                title="🤖 Bot Help",
                description="Here are the available commands:",
                color=0x00ff00
            )
            
            # Group commands by cog
            for cog_name, cog in self.bot.cogs.items():
                if cog_name.lower() in ['general', 'music', 'moderation']:
                    commands_list = []
                    for command in cog.get_commands():
                        if not command.hidden:
                            commands_list.append(f"`{command.name}`")
                    
                    if commands_list:
                        embed.add_field(
                            name=f"{cog_name.title()} Commands",
                            value=", ".join(commands_list),
                            inline=False
                        )
            
            embed.add_field(
                name="More Information",
                value=f"Use `{ctx.prefix}help <command>` for detailed information about a specific command.",
                inline=False
            )
            
            embed.set_footer(text=f"Requested by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot)) 