import discord
from discord.ext import commands
from discord import app_commands
from database import db
import config

class Moderation(commands.Cog):
    """Moderation commands for server management."""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def send_mod_log(self, guild: discord.Guild, embed: discord.Embed):
        """Send moderation log to the configured channel."""
        mod_log_channel_id = db.get_server_setting(guild.id, "mod_log_channel")
        if mod_log_channel_id:
            channel = guild.get_channel(mod_log_channel_id)
            if channel:
                try:
                    await channel.send(embed=embed)
                except discord.Forbidden:
                    pass  # Silently fail if we can't send to the log channel
    
    @commands.hybrid_command(name='clear', description="Clear a specified number of messages")
    @app_commands.describe(amount="Number of messages to clear (default: 5, max: 100)")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Clear a specified number of messages (default: 5)."""
        if amount > 100:
            await ctx.send("❌ You can only delete up to 100 messages at once.")
            return
        
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 to include the command message
        
        # Log the action
        db.log_mod_action(ctx.guild.id, ctx.author.id, ctx.author.id, "clear", f"Cleared {len(deleted) - 1} messages")
        
        await ctx.send(f"🗑️ Deleted {len(deleted) - 1} messages.", delete_after=5)
    
    @commands.hybrid_command(name='kick', description="Kick a member from the server")
    @app_commands.describe(member="The member to kick", reason="Reason for kicking")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """Kick a member from the server."""
        if member == ctx.author:
            await ctx.send("❌ You cannot kick yourself.")
            return
        
        if member.guild_permissions.administrator:
            await ctx.send("❌ You cannot kick an administrator.")
            return
        
        try:
            await member.kick(reason=reason)
            
            # Log the action
            db.log_mod_action(ctx.guild.id, member.id, ctx.author.id, "kick", reason)
            
            embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member.display_name}** has been kicked from the server.",
                color=discord.Color.orange()
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Kicked by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
            # Send to mod log
            log_embed = discord.Embed(
                title="👢 Member Kicked",
                description=f"**{member.display_name}** ({member.id}) was kicked",
                color=discord.Color.orange()
            )
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="Reason", value=reason or "No reason provided", inline=True)
            log_embed.set_footer(text=f"User ID: {member.id}")
            
            await self.send_mod_log(ctx.guild, log_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to kick that member.")
    
    @commands.hybrid_command(name='ban', description="Ban a member from the server")
    @app_commands.describe(member="The member to ban", reason="Reason for banning")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """Ban a member from the server."""
        if member == ctx.author:
            await ctx.send("❌ You cannot ban yourself.")
            return
        
        if member.guild_permissions.administrator:
            await ctx.send("❌ You cannot ban an administrator.")
            return
        
        try:
            await member.ban(reason=reason)
            
            # Log the action
            db.log_mod_action(ctx.guild.id, member.id, ctx.author.id, "ban", reason)
            
            embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member.display_name}** has been banned from the server.",
                color=discord.Color.red()
            )
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Banned by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
            # Send to mod log
            log_embed = discord.Embed(
                title="🔨 Member Banned",
                description=f"**{member.display_name}** ({member.id}) was banned",
                color=discord.Color.red()
            )
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="Reason", value=reason or "No reason provided", inline=True)
            log_embed.set_footer(text=f"User ID: {member.id}")
            
            await self.send_mod_log(ctx.guild, log_embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to ban that member.")
    
    @commands.hybrid_command(name='unban', description="Unban a user by their ID")
    @app_commands.describe(user_id="The ID of the user to unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        """Unban a user by their ID."""
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            
            # Log the action
            db.log_mod_action(ctx.guild.id, user_id, ctx.author.id, "unban", "User unbanned")
            
            embed = discord.Embed(
                title="🔓 User Unbanned",
                description=f"**{user.display_name}** has been unbanned from the server.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Unbanned by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
            # Send to mod log
            log_embed = discord.Embed(
                title="🔓 User Unbanned",
                description=f"**{user.display_name}** ({user_id}) was unbanned",
                color=discord.Color.green()
            )
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.set_footer(text=f"User ID: {user_id}")
            
            await self.send_mod_log(ctx.guild, log_embed)
            
        except discord.NotFound:
            await ctx.send("❌ User not found or not banned.")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to unban that user.")
    
    @commands.hybrid_command(name='warn', description="Warn a member")
    @app_commands.describe(member="The member to warn", reason="Reason for the warning")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        """Warn a member."""
        if member == ctx.author:
            await ctx.send("❌ You cannot warn yourself.")
            return
        
        if member.guild_permissions.administrator:
            await ctx.send("❌ You cannot warn an administrator.")
            return
        
        # Add warning to database
        if db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason):
            embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**{member.display_name}** has been warned.",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.set_footer(text=f"Warned by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
            
            # Send to mod log
            log_embed = discord.Embed(
                title="⚠️ Member Warned",
                description=f"**{member.display_name}** ({member.id}) was warned",
                color=discord.Color.yellow()
            )
            log_embed.add_field(name="Moderator", value=ctx.author.mention, inline=True)
            log_embed.add_field(name="Reason", value=reason, inline=True)
            log_embed.set_footer(text=f"User ID: {member.id}")
            
            await self.send_mod_log(ctx.guild, log_embed)
        else:
            await ctx.send("❌ Failed to add warning to database.")
    
    @commands.hybrid_command(name='warnings', description="Check warnings for a member")
    @app_commands.describe(member="The member to check warnings for")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        """Check warnings for a member."""
        warnings = db.get_user_warnings(ctx.guild.id, member.id)
        
        if not warnings:
            embed = discord.Embed(
                title="📋 Warnings",
                description=f"**{member.display_name}** has no warnings.",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="📋 Warnings",
                description=f"**{member.display_name}** has {len(warnings)} warning(s):",
                color=discord.Color.yellow()
            )
            
            for i, warning in enumerate(warnings[:5], 1):  # Show last 5 warnings
                embed.add_field(
                    name=f"Warning #{i}",
                    value=f"**Reason:** {warning['reason']}\n**Date:** {warning['timestamp']}",
                    inline=False
                )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='clearwarnings', description="Clear all warnings for a member")
    @app_commands.describe(member="The member to clear warnings for")
    @commands.has_permissions(manage_messages=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear all warnings for a member."""
        warnings = db.get_user_warnings(ctx.guild.id, member.id)
        
        if not warnings:
            await ctx.send("❌ This user has no warnings to clear.")
            return
        
        if db.clear_user_warnings(ctx.guild.id, member.id):
            embed = discord.Embed(
                title="🧹 Warnings Cleared",
                description=f"**{member.display_name}**'s warnings have been cleared.",
                color=discord.Color.green()
            )
            embed.add_field(name="Warnings Removed", value=len(warnings), inline=True)
            embed.set_footer(text=f"Cleared by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to clear warnings.")
    
    @commands.hybrid_command(name='modlogs', description="View moderation logs")
    @app_commands.describe(member="Optional member to view logs for", limit="Number of logs to show (max: 25)")
    @commands.has_permissions(manage_messages=True)
    async def mod_logs(self, ctx, member: discord.Member = None, limit: int = 10):
        """View moderation logs for the server or a specific user."""
        if limit > 25:
            limit = 25
        
        if member:
            logs = db.get_mod_logs(ctx.guild.id, member.id, limit)
            title = f"📋 Mod Logs for {member.display_name}"
        else:
            logs = db.get_mod_logs(ctx.guild.id, limit=limit)
            title = "📋 Recent Mod Logs"
        
        if not logs:
            embed = discord.Embed(
                title=title,
                description="No moderation logs found.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title=title,
                description=f"Showing last {len(logs)} moderation actions:",
                color=discord.Color.blue()
            )
            
            for log in logs:
                action_emoji = {
                    "kick": "👢",
                    "ban": "🔨",
                    "unban": "🔓",
                    "warn": "⚠️",
                    "clear": "🗑️"
                }.get(log['action_type'], "📝")
                
                embed.add_field(
                    name=f"{action_emoji} {log['action_type'].title()}",
                    value=f"**User:** <@{log['user_id']}>\n**Moderator:** <@{log['moderator_id']}>\n**Reason:** {log['reason'] or 'No reason'}\n**Date:** {log['timestamp']}",
                    inline=False
                )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='setmodlog', description="Set the moderation log channel")
    @app_commands.describe(channel="The channel to send moderation logs to")
    @commands.has_permissions(administrator=True)
    async def set_mod_log(self, ctx, channel: discord.TextChannel):
        """Set the moderation log channel."""
        if db.set_server_setting(ctx.guild.id, "mod_log_channel", channel.id):
            embed = discord.Embed(
                title="✅ Mod Log Channel Set",
                description=f"Moderation logs will now be sent to {channel.mention}",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to set mod log channel.")

async def setup(bot):
    await bot.add_cog(Moderation(bot)) 