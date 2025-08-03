import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def log_mod_action(self, ctx, action_type: str, target: discord.Member, reason: str = None, duration: str = None):
        """Log moderation action to database and send to modlog channel"""
        try:
            # Log to database
            await self.bot.db.add_modlog(
                guild_id=ctx.guild.id,
                user_id=target.id,
                moderator_id=ctx.author.id,
                action_type=action_type,
                reason=reason,
                additional_data={
                    'channel_id': ctx.channel.id,
                    'duration': duration,
                    'timestamp': datetime.utcnow().isoformat()
                }
            )
            
            # Send to modlog channel if configured
            settings = await self.bot.db.get_guild_settings(ctx.guild.id)
            if settings and settings.get('modlog_channel_id'):
                channel = self.bot.get_channel(settings['modlog_channel_id'])
                if channel:
                    embed = discord.Embed(
                        title=f"🛡️ {action_type.title()}",
                        description=f"**User:** {target.mention} (`{target.id}`)\n"
                                  f"**Moderator:** {ctx.author.mention} (`{ctx.author.id}`)\n"
                                  f"**Channel:** {ctx.channel.mention}",
                        color=0xff0000,
                        timestamp=datetime.utcnow()
                    )
                    
                    if reason:
                        embed.add_field(name="Reason", value=reason, inline=False)
                    
                    if duration:
                        embed.add_field(name="Duration", value=duration, inline=True)
                    
                    embed.set_thumbnail(url=target.display_avatar.url)
                    embed.set_footer(text=f"Case ID: {ctx.guild.id}-{target.id}")
                    
                    await channel.send(embed=embed)
        
        except Exception as e:
            print(f"Error logging mod action: {e}")
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a member from the server"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick yourself!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot kick an administrator!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.kick(reason=f"{ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="👢 Kicked",
                description=f"{member.mention} has been kicked from the server.",
                color=0xff0000
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=ctx.author.mention)
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_mod_action(ctx, "kick", member, reason)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to kick this member!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to kick member: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a member from the server"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot ban yourself!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot ban an administrator!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.ban(reason=f"{ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="🔨 Banned",
                description=f"{member.mention} has been banned from the server.",
                color=0xff0000
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=ctx.author.mention)
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_mod_action(ctx, "ban", member, reason)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to ban this member!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to ban member: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = "No reason provided"):
        """Unban a user by their ID"""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="🔓 Unbanned",
                description=f"{user.mention} has been unbanned from the server.",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=ctx.author.mention)
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_mod_action(ctx, "unban", user, reason)
            
        except discord.NotFound:
            embed = discord.Embed(
                title="❌ Error",
                description="User not found or not banned!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to unban this user!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to unban user: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='timeout', aliases=['mute'])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        """Timeout a member (duration format: 1m, 1h, 1d)"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot timeout yourself!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot timeout an administrator!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Parse duration
        try:
            time_value = int(duration[:-1])
            time_unit = duration[-1].lower()
            
            if time_unit == 'm':
                delta = timedelta(minutes=time_value)
            elif time_unit == 'h':
                delta = timedelta(hours=time_value)
            elif time_unit == 'd':
                delta = timedelta(days=time_value)
            else:
                raise ValueError("Invalid time unit")
            
            if delta.total_seconds() > 2419200:  # 28 days max
                embed = discord.Embed(
                    title="❌ Error",
                    description="Timeout duration cannot exceed 28 days!",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
        except (ValueError, IndexError):
            embed = discord.Embed(
                title="❌ Error",
                description="Invalid duration format! Use: 1m, 1h, 1d",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await member.timeout(delta, reason=f"{ctx.author}: {reason}")
            
            embed = discord.Embed(
                title="🔇 Timeout",
                description=f"{member.mention} has been timed out for {duration}.",
                color=0xffff00
            )
            embed.add_field(name="Reason", value=reason)
            embed.add_field(name="Moderator", value=ctx.author.mention)
            embed.add_field(name="Duration", value=duration)
            await ctx.send(embed=embed)
            
            # Log the action
            await self.log_mod_action(ctx, "timeout", member, reason, duration)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to timeout this member!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to timeout member: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='warn')
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a member"""
        if member == ctx.author:
            embed = discord.Embed(
                title="❌ Error",
                description="You cannot warn yourself!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="⚠️ Warning",
            description=f"{member.mention} has been warned.",
            color=0xffff00
        )
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Moderator", value=ctx.author.mention)
        await ctx.send(embed=embed)
        
        # Log the action
        await self.log_mod_action(ctx, "warn", member, reason)
    
    @commands.command(name='modlogs')
    @commands.has_permissions(kick_members=True)
    async def modlogs(self, ctx, member: discord.Member = None, limit: int = 10):
        """Show moderation logs for a member or the server"""
        if limit > 25:
            limit = 25
        
        if member:
            logs = await self.bot.db.get_modlogs(ctx.guild.id, member.id, limit)
            title = f"Moderation Logs for {member.display_name}"
        else:
            logs = await self.bot.db.get_modlogs(ctx.guild.id, limit=limit)
            title = "Recent Moderation Logs"
        
        if not logs:
            embed = discord.Embed(
                title=title,
                description="No moderation logs found.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title=title,
            color=0x00ff00
        )
        
        for log in logs[:10]:  # Show max 10 logs in embed
            moderator = self.bot.get_user(log['moderator_id'])
            user = self.bot.get_user(log['user_id'])
            
            moderator_name = moderator.display_name if moderator else f"Unknown ({log['moderator_id']})"
            user_name = user.display_name if user else f"Unknown ({log['user_id']})"
            
            embed.add_field(
                name=f"{log['action_type'].title()} - {log['timestamp'].strftime('%Y-%m-%d %H:%M')}",
                value=f"**User:** {user_name}\n"
                      f"**Moderator:** {moderator_name}\n"
                      f"**Reason:** {log['reason'] or 'No reason provided'}",
                inline=False
            )
        
        if len(logs) > 10:
            embed.set_footer(text=f"Showing 10 of {len(logs)} logs")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """Clear a specified number of messages"""
        if amount < 1 or amount > 100:
            embed = discord.Embed(
                title="❌ Error",
                description="Please specify a number between 1 and 100.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include command message
            
            embed = discord.Embed(
                title="🧹 Cleared",
                description=f"Deleted {len(deleted) - 1} messages.",
                color=0x00ff00
            )
            await ctx.send(embed=embed, delete_after=5)
            
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Error",
                description="I don't have permission to delete messages in this channel!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to clear messages: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 