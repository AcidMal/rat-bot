import discord
from discord.ext import commands
import asyncio
from typing import Optional, Union, List
from datetime import datetime, timezone, timedelta
import re
from loguru import logger

class Moderation(commands.Cog):
    """Advanced moderation system with database logging"""
    
    def __init__(self, bot):
        self.bot = bot
        self.auto_mod_cache = {}  # Cache for auto-moderation settings
    
    async def log_action(self, guild_id: int, action_type: str, moderator: discord.Member, 
                        target: Union[discord.Member, discord.User], reason: str = None, 
                        duration: timedelta = None, evidence: str = None) -> str:
        """Log a moderation action to the database"""
        if not self.bot.db:
            return None
        
        action_data = {
            'guild_id': guild_id,
            'action_type': action_type,
            'moderator_id': moderator.id,
            'moderator_name': str(moderator),
            'target_user_id': target.id,
            'target_user_name': str(target),
            'reason': reason or 'No reason provided',
            'duration': duration.total_seconds() if duration else None,
            'evidence': evidence,
            'timestamp': datetime.now(timezone.utc)
        }
        
        try:
            log_id = await self.bot.db.log_moderation_action(action_data)
            logger.info(f"Logged moderation action: {action_type} by {moderator} on {target}")
            return log_id
        except Exception as e:
            logger.error(f"Failed to log moderation action: {e}")
            return None
    
    async def send_modlog(self, guild: discord.Guild, embed: discord.Embed):
        """Send moderation log to the configured channel"""
        try:
            guild_config = await self.bot.db.get_guild_config(guild.id)
            modlog_channel_id = guild_config.get('modlog_channel')
            
            if modlog_channel_id:
                channel = guild.get_channel(modlog_channel_id)
                if channel:
                    await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send modlog: {e}")
    
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """Kick a member from the server"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ You cannot kick someone with a higher or equal role!")
        
        if member == ctx.author:
            return await ctx.send("❌ You cannot kick yourself!")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot kick someone with a higher or equal role than me!")
        
        reason = reason or "No reason provided"
        
        # Log the action
        log_id = await self.log_action(
            ctx.guild.id, "kick", ctx.author, member, reason
        )
        
        try:
            # Send DM to the user
            try:
                dm_embed = discord.Embed(
                    title="🦶 You were kicked",
                    description=f"You were kicked from **{ctx.guild.name}**",
                    color=0xff6600
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                await member.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Kick the member
            await member.kick(reason=f"{ctx.author}: {reason}")
            
            # Confirmation embed
            embed = discord.Embed(
                title="🦶 Member Kicked",
                description=f"**{member}** has been kicked",
                color=0xff6600
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if log_id:
                embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await ctx.send(embed=embed)
            
            # Send to modlog
            modlog_embed = discord.Embed(
                title="🦶 Member Kicked",
                color=0xff6600,
                timestamp=datetime.now(timezone.utc)
            )
            modlog_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            if log_id:
                modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await self.send_modlog(ctx.guild, modlog_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick this member!")
        except Exception as e:
            await ctx.send(f"❌ Failed to kick member: {e}")
    
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Union[discord.Member, discord.User], 
                  delete_days: int = 0, *, reason: str = None):
        """Ban a member from the server"""
        if isinstance(member, discord.Member):
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send("❌ You cannot ban someone with a higher or equal role!")
            
            if member == ctx.author:
                return await ctx.send("❌ You cannot ban yourself!")
            
            if member.top_role >= ctx.guild.me.top_role:
                return await ctx.send("❌ I cannot ban someone with a higher or equal role than me!")
        
        if not 0 <= delete_days <= 7:
            return await ctx.send("❌ Delete days must be between 0 and 7!")
        
        reason = reason or "No reason provided"
        
        # Log the action
        log_id = await self.log_action(
            ctx.guild.id, "ban", ctx.author, member, reason
        )
        
        try:
            # Send DM to the user (if they're in the server)
            if isinstance(member, discord.Member):
                try:
                    dm_embed = discord.Embed(
                        title="🔨 You were banned",
                        description=f"You were banned from **{ctx.guild.name}**",
                        color=0xff0000
                    )
                    dm_embed.add_field(name="Reason", value=reason, inline=False)
                    dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                    await member.send(embed=dm_embed)
                except:
                    pass
            
            # Ban the member
            await ctx.guild.ban(member, delete_message_days=delete_days, reason=f"{ctx.author}: {reason}")
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member}** has been banned",
                color=0xff0000
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            embed.add_field(name="Messages Deleted", value=f"{delete_days} days", inline=True)
            if log_id:
                embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await ctx.send(embed=embed)
            
            # Send to modlog
            modlog_embed = discord.Embed(
                title="🔨 Member Banned",
                color=0xff0000,
                timestamp=datetime.now(timezone.utc)
            )
            modlog_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            modlog_embed.add_field(name="Messages Deleted", value=f"{delete_days} days", inline=True)
            if log_id:
                modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await self.send_modlog(ctx.guild, modlog_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban this member!")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban member: {e}")
    
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int, *, reason: str = None):
        """Unban a user from the server"""
        reason = reason or "No reason provided"
        
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
            
            # Log the action
            log_id = await self.log_action(
                ctx.guild.id, "unban", ctx.author, user, reason
            )
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔓 Member Unbanned",
                description=f"**{user}** has been unbanned",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if log_id:
                embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await ctx.send(embed=embed)
            
            # Send to modlog
            modlog_embed = discord.Embed(
                title="🔓 Member Unbanned",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            modlog_embed.add_field(name="User", value=f"{user} ({user.id})", inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            if log_id:
                modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await self.send_modlog(ctx.guild, modlog_embed)
            
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned!")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban members!")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban user: {e}")
    
    @commands.command(name="timeout", aliases=["mute"])
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, duration: str, *, reason: str = None):
        """Timeout a member for a specified duration"""
        if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            return await ctx.send("❌ You cannot timeout someone with a higher or equal role!")
        
        if member == ctx.author:
            return await ctx.send("❌ You cannot timeout yourself!")
        
        if member.top_role >= ctx.guild.me.top_role:
            return await ctx.send("❌ I cannot timeout someone with a higher or equal role than me!")
        
        # Parse duration
        try:
            duration_delta = self._parse_duration(duration)
            if duration_delta.total_seconds() > 2419200:  # 28 days max
                return await ctx.send("❌ Timeout duration cannot exceed 28 days!")
        except ValueError as e:
            return await ctx.send(f"❌ Invalid duration format: {e}")
        
        reason = reason or "No reason provided"
        
        # Log the action
        log_id = await self.log_action(
            ctx.guild.id, "timeout", ctx.author, member, reason, duration_delta
        )
        
        try:
            # Send DM to the user
            try:
                dm_embed = discord.Embed(
                    title="🔇 You were timed out",
                    description=f"You were timed out in **{ctx.guild.name}**",
                    color=0xffaa00
                )
                dm_embed.add_field(name="Duration", value=duration, inline=True)
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
                await member.send(embed=dm_embed)
            except:
                pass
            
            # Apply timeout
            until = datetime.now(timezone.utc) + duration_delta
            await member.timeout(until, reason=f"{ctx.author}: {reason}")
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔇 Member Timed Out",
                description=f"**{member}** has been timed out",
                color=0xffaa00
            )
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Until", value=f"<t:{int(until.timestamp())}:F>", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if log_id:
                embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await ctx.send(embed=embed)
            
            # Send to modlog
            modlog_embed = discord.Embed(
                title="🔇 Member Timed Out",
                color=0xffaa00,
                timestamp=datetime.now(timezone.utc)
            )
            modlog_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            modlog_embed.add_field(name="Duration", value=duration, inline=True)
            modlog_embed.add_field(name="Until", value=f"<t:{int(until.timestamp())}:F>", inline=True)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            if log_id:
                modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await self.send_modlog(ctx.guild, modlog_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to timeout this member!")
        except Exception as e:
            await ctx.send(f"❌ Failed to timeout member: {e}")
    
    @commands.command(name="untimeout", aliases=["unmute"])
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member, *, reason: str = None):
        """Remove timeout from a member"""
        if not member.is_timed_out():
            return await ctx.send("❌ This member is not timed out!")
        
        reason = reason or "No reason provided"
        
        # Log the action
        log_id = await self.log_action(
            ctx.guild.id, "untimeout", ctx.author, member, reason
        )
        
        try:
            await member.timeout(None, reason=f"{ctx.author}: {reason}")
            
            # Confirmation embed
            embed = discord.Embed(
                title="🔊 Timeout Removed",
                description=f"**{member}** is no longer timed out",
                color=0x00ff00
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            if log_id:
                embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await ctx.send(embed=embed)
            
            # Send to modlog
            modlog_embed = discord.Embed(
                title="🔊 Timeout Removed",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            modlog_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
            modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
            modlog_embed.add_field(name="Reason", value=reason, inline=False)
            if log_id:
                modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
            
            await self.send_modlog(ctx.guild, modlog_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove timeout from this member!")
        except Exception as e:
            await ctx.send(f"❌ Failed to remove timeout: {e}")
    
    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        """Warn a member"""
        if member == ctx.author:
            return await ctx.send("❌ You cannot warn yourself!")
        
        reason = reason or "No reason provided"
        
        # Log the action
        log_id = await self.log_action(
            ctx.guild.id, "warn", ctx.author, member, reason
        )
        
        # Get user's warning count
        if self.bot.db:
            infractions = await self.bot.db.get_user_infractions(ctx.guild.id, member.id)
            warning_count = len([i for i in infractions if i.get('action_type') == 'warn']) + 1
        else:
            warning_count = 1
        
        # Send DM to the user
        try:
            dm_embed = discord.Embed(
                title="⚠️ You received a warning",
                description=f"You received a warning in **{ctx.guild.name}**",
                color=0xffaa00
            )
            dm_embed.add_field(name="Reason", value=reason, inline=False)
            dm_embed.add_field(name="Moderator", value=str(ctx.author), inline=True)
            dm_embed.add_field(name="Warning Count", value=f"{warning_count}", inline=True)
            await member.send(embed=dm_embed)
        except:
            pass
        
        # Confirmation embed
        embed = discord.Embed(
            title="⚠️ Member Warned",
            description=f"**{member}** has been warned",
            color=0xffaa00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
        embed.add_field(name="Warning Count", value=f"{warning_count}", inline=True)
        if log_id:
            embed.add_field(name="Case ID", value=log_id, inline=True)
        
        await ctx.send(embed=embed)
        
        # Send to modlog
        modlog_embed = discord.Embed(
            title="⚠️ Member Warned",
            color=0xffaa00,
            timestamp=datetime.now(timezone.utc)
        )
        modlog_embed.add_field(name="User", value=f"{member} ({member.id})", inline=True)
        modlog_embed.add_field(name="Moderator", value=f"{ctx.author} ({ctx.author.id})", inline=True)
        modlog_embed.add_field(name="Warning Count", value=f"{warning_count}", inline=True)
        modlog_embed.add_field(name="Reason", value=reason, inline=False)
        if log_id:
            modlog_embed.add_field(name="Case ID", value=log_id, inline=True)
        
        await self.send_modlog(ctx.guild, modlog_embed)
        
        # Check for auto-moderation based on warning count
        if self.bot.db:
            guild_config = await self.bot.db.get_guild_config(ctx.guild.id)
            max_warnings = guild_config.get('moderation_settings', {}).get('max_warnings', 3)
            
            if warning_count >= max_warnings:
                # Auto-timeout for 1 hour
                try:
                    until = datetime.now(timezone.utc) + timedelta(hours=1)
                    await member.timeout(until, reason="Automatic timeout: Too many warnings")
                    
                    auto_embed = discord.Embed(
                        title="🔇 Automatic Timeout",
                        description=f"**{member}** has been automatically timed out for 1 hour due to {warning_count} warnings",
                        color=0xff0000
                    )
                    await ctx.send(embed=auto_embed)
                    
                    # Log auto-action
                    await self.log_action(
                        ctx.guild.id, "auto_timeout", ctx.guild.me, member, 
                        f"Automatic timeout after {warning_count} warnings", timedelta(hours=1)
                    )
                except:
                    pass
    
    @commands.command(name="modlogs", aliases=["logs"])
    @commands.has_permissions(manage_messages=True)
    async def modlogs(self, ctx, member: discord.Member = None, limit: int = 10):
        """View moderation logs for a member or the server"""
        if not self.bot.db:
            return await ctx.send("❌ Database not available")
        
        if limit > 50:
            limit = 50
        
        try:
            if member:
                # Get logs for specific member
                logs = await self.bot.db.get_user_infractions(ctx.guild.id, member.id)
                title = f"📋 Moderation Logs for {member}"
            else:
                # Get general server logs
                logs = await self.bot.db.get_moderation_logs(ctx.guild.id, limit)
                title = f"📋 Recent Moderation Logs"
            
            if not logs:
                return await ctx.send("📭 No moderation logs found")
            
            # Create embed
            embed = discord.Embed(title=title, color=0x00aaff)
            
            for i, log in enumerate(logs[:limit]):
                action_type = log.get('action_type', 'Unknown')
                target_name = log.get('target_user_name', 'Unknown')
                moderator_name = log.get('moderator_name', 'Unknown')
                reason = log.get('reason', 'No reason')
                timestamp = log.get('timestamp')
                
                if isinstance(timestamp, str):
                    try:
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    except:
                        timestamp = None
                
                time_str = f"<t:{int(timestamp.timestamp())}:R>" if timestamp else "Unknown time"
                
                value = f"**Action:** {action_type.title()}\n"
                value += f"**Target:** {target_name}\n"
                value += f"**Moderator:** {moderator_name}\n"
                value += f"**Reason:** {reason}\n"
                value += f"**Time:** {time_str}"
                
                if log.get('duration'):
                    duration_seconds = log.get('duration')
                    duration_str = self._format_duration(duration_seconds)
                    value += f"\n**Duration:** {duration_str}"
                
                embed.add_field(
                    name=f"Case #{i+1}",
                    value=value,
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error fetching modlogs: {e}")
            await ctx.send("❌ Failed to fetch moderation logs")
    
    @commands.command(name="purge", aliases=["clear_messages"])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 10, member: discord.Member = None):
        """Clear messages from the channel"""
        if amount > 100:
            return await ctx.send("❌ Cannot delete more than 100 messages at once!")
        
        if amount < 1:
            return await ctx.send("❌ Amount must be at least 1!")
        
        def check(message):
            if member:
                return message.author == member
            return True
        
        try:
            deleted = await ctx.channel.purge(limit=amount, check=check)
            
            # Log the action
            reason = f"Cleared {len(deleted)} messages"
            if member:
                reason += f" from {member}"
            
            await self.log_action(
                ctx.guild.id, "clear", ctx.author, member or ctx.author, reason
            )
            
            # Confirmation message (auto-delete after 5 seconds)
            embed = discord.Embed(
                title="🗑️ Messages Cleared",
                description=f"Deleted {len(deleted)} messages",
                color=0x00ff00
            )
            if member:
                embed.add_field(name="From User", value=member.mention, inline=True)
            embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            
            msg = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete messages!")
        except Exception as e:
            await ctx.send(f"❌ Failed to clear messages: {e}")
    
    def _parse_duration(self, duration_str: str) -> timedelta:
        """Parse duration string like '1h30m' into timedelta"""
        duration_regex = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
        match = duration_regex.match(duration_str.lower())
        
        if not match or not any(match.groups()):
            raise ValueError("Invalid duration format. Use format like: 1d2h30m45s")
        
        days, hours, minutes, seconds = match.groups()
        
        total_seconds = 0
        if days:
            total_seconds += int(days) * 86400
        if hours:
            total_seconds += int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        
        if total_seconds == 0:
            raise ValueError("Duration must be greater than 0")
        
        return timedelta(seconds=total_seconds)
    
    def _format_duration(self, seconds: float) -> str:
        """Format seconds into readable duration"""
        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs:
            parts.append(f"{secs}s")
        
        return " ".join(parts) if parts else "0s"
    
    # Auto-moderation features
    @commands.Cog.listener()
    async def on_message(self, message):
        """Auto-moderation message handler"""
        if not message.guild or message.author.bot:
            return
        
        if not self.bot.db:
            return
        
        # Check if auto-mod is enabled
        guild_config = await self.bot.db.get_guild_config(message.guild.id)
        auto_mod_settings = guild_config.get('moderation_settings', {})
        
        if not auto_mod_settings.get('auto_mod_enabled', False):
            return
        
        # Skip if user has manage messages permission
        if message.author.guild_permissions.manage_messages:
            return
        
        # Word filter
        if auto_mod_settings.get('word_filter'):
            await self._check_word_filter(message, auto_mod_settings['word_filter'])
        
        # Link filter
        if auto_mod_settings.get('link_filter'):
            await self._check_link_filter(message)
        
        # Spam detection
        if auto_mod_settings.get('spam_detection'):
            await self._check_spam(message)
    
    async def _check_word_filter(self, message, word_filter: List[str]):
        """Check message against word filter"""
        content_lower = message.content.lower()
        
        for word in word_filter:
            if word.lower() in content_lower:
                try:
                    await message.delete()
                    
                    # Send warning
                    embed = discord.Embed(
                        title="🚫 Message Filtered",
                        description=f"{message.author.mention}, your message contained filtered content.",
                        color=0xff0000
                    )
                    warning_msg = await message.channel.send(embed=embed)
                    
                    # Auto-delete warning after 5 seconds
                    await asyncio.sleep(5)
                    await warning_msg.delete()
                    
                    # Log the action
                    await self.log_action(
                        message.guild.id, "auto_filter", message.guild.me, 
                        message.author, f"Message contained filtered word: {word}"
                    )
                    
                except discord.Forbidden:
                    pass
                break
    
    async def _check_link_filter(self, message):
        """Check message for links"""
        url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        
        if url_pattern.search(message.content):
            try:
                await message.delete()
                
                embed = discord.Embed(
                    title="🔗 Link Filtered",
                    description=f"{message.author.mention}, links are not allowed in this channel.",
                    color=0xff0000
                )
                warning_msg = await message.channel.send(embed=embed)
                
                await asyncio.sleep(5)
                await warning_msg.delete()
                
                # Log the action
                await self.log_action(
                    message.guild.id, "auto_filter", message.guild.me, 
                    message.author, "Message contained unauthorized link"
                )
                
            except discord.Forbidden:
                pass
    
    async def _check_spam(self, message):
        """Check for spam (basic implementation)"""
        user_id = message.author.id
        guild_id = message.guild.id
        
        # Simple spam detection: 5 messages in 10 seconds
        current_time = datetime.now(timezone.utc)
        
        if guild_id not in self.auto_mod_cache:
            self.auto_mod_cache[guild_id] = {}
        
        if user_id not in self.auto_mod_cache[guild_id]:
            self.auto_mod_cache[guild_id][user_id] = []
        
        # Clean old messages
        user_messages = self.auto_mod_cache[guild_id][user_id]
        user_messages = [msg_time for msg_time in user_messages if (current_time - msg_time).total_seconds() < 10]
        
        # Add current message
        user_messages.append(current_time)
        self.auto_mod_cache[guild_id][user_id] = user_messages
        
        # Check if spam threshold exceeded
        if len(user_messages) >= 5:
            try:
                # Timeout for 5 minutes
                until = current_time + timedelta(minutes=5)
                await message.author.timeout(until, reason="Automatic timeout: Spam detection")
                
                embed = discord.Embed(
                    title="🚫 Spam Detected",
                    description=f"{message.author.mention} has been timed out for 5 minutes due to spam.",
                    color=0xff0000
                )
                await message.channel.send(embed=embed)
                
                # Log the action
                await self.log_action(
                    guild_id, "auto_timeout", message.guild.me, 
                    message.author, "Automatic timeout: Spam detection", timedelta(minutes=5)
                )
                
                # Clear user's message cache
                self.auto_mod_cache[guild_id][user_id] = []
                
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Moderation(bot))