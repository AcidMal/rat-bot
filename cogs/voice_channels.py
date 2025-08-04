import discord
from discord.ext import commands
from typing import Dict, Set, Optional
from loguru import logger
import asyncio

class DynamicVoiceChannels(commands.Cog):
    """Dynamic voice channel creation system"""
    
    def __init__(self, bot):
        self.bot = bot
        # Guild ID -> {trigger_channel_id: category_id}
        self.trigger_channels: Dict[int, Dict[int, int]] = {}
        # Guild ID -> Set of created channel IDs
        self.created_channels: Dict[int, Set[int]] = {}
        # Channel ID -> Owner ID
        self.channel_owners: Dict[int, int] = {}
        
        # Load configuration from database if available
        if hasattr(bot, 'db') and bot.db:
            asyncio.create_task(self._load_config())
    
    async def _load_config(self):
        """Load dynamic voice channel configuration from database"""
        try:
            if hasattr(self.bot.db, 'get_guild_config'):
                # This would load from database - implement based on your database structure
                pass
        except Exception as e:
            logger.error(f"Failed to load voice channel config: {e}")
    
    async def _save_config(self, guild_id: int):
        """Save dynamic voice channel configuration to database"""
        try:
            if hasattr(self.bot.db, 'set_guild_config'):
                config = {
                    'trigger_channels': self.trigger_channels.get(guild_id, {}),
                    'created_channels': list(self.created_channels.get(guild_id, set())),
                    'channel_owners': {k: v for k, v in self.channel_owners.items() 
                                     if k in self.created_channels.get(guild_id, set())}
                }
                # Save to database - implement based on your database structure
                # await self.bot.db.set_guild_config(guild_id, 'dynamic_voice', config)
        except Exception as e:
            logger.error(f"Failed to save voice channel config: {e}")
    
    @commands.group(name="voice", aliases=["vc"])
    @commands.has_permissions(manage_channels=True)
    async def voice(self, ctx):
        """Dynamic voice channel management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🎤 Dynamic Voice Channels",
                description="Manage auto-creating voice channels",
                color=0x0099ff
            )
            
            embed.add_field(
                name="Commands",
                value="`!voice setup <trigger_channel> [category]` - Set up auto-creation\n"
                      "`!voice remove <trigger_channel>` - Remove auto-creation\n"
                      "`!voice list` - List configured channels\n"
                      "`!voice cleanup` - Clean up empty created channels",
                inline=False
            )
            
            embed.add_field(
                name="How it works",
                value="• Users join the trigger channel\n"
                      "• A new channel is created for them\n"
                      "• They're moved to their new channel\n"
                      "• They get permissions to manage their channel\n"
                      "• Channel is deleted when empty",
                inline=False
            )
            
            await ctx.send(embed=embed)
    
    @voice.command(name="setup")
    @commands.has_permissions(manage_channels=True)
    async def setup_trigger(self, ctx, trigger_channel: discord.VoiceChannel, category: discord.CategoryChannel = None):
        """Set up a trigger channel for dynamic voice creation"""
        guild_id = ctx.guild.id
        
        # Initialize guild data if needed
        if guild_id not in self.trigger_channels:
            self.trigger_channels[guild_id] = {}
        if guild_id not in self.created_channels:
            self.created_channels[guild_id] = set()
        
        # Use the same category as the trigger channel if none specified
        if category is None:
            category = trigger_channel.category
        
        # Set up the trigger channel
        self.trigger_channels[guild_id][trigger_channel.id] = category.id if category else None
        
        # Save configuration
        await self._save_config(guild_id)
        
        embed = discord.Embed(
            title="✅ Dynamic Voice Channel Configured",
            description=f"**Trigger Channel:** {trigger_channel.mention}\n"
                       f"**Category:** {category.name if category else 'Same as trigger channel'}\n\n"
                       f"When users join {trigger_channel.mention}, a new voice channel will be created for them!",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Features",
            value="• Auto-creation when joined\n"
                  "• User gets channel permissions\n"
                  "• Auto-deletion when empty\n"
                  "• Customizable channel name",
            inline=False
        )
        
        await ctx.send(embed=embed)
        logger.info(f"Dynamic voice channel configured: {trigger_channel.name} in {ctx.guild.name}")
    
    @voice.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def remove_trigger(self, ctx, trigger_channel: discord.VoiceChannel):
        """Remove a trigger channel configuration"""
        guild_id = ctx.guild.id
        
        if guild_id in self.trigger_channels and trigger_channel.id in self.trigger_channels[guild_id]:
            del self.trigger_channels[guild_id][trigger_channel.id]
            await self._save_config(guild_id)
            
            embed = discord.Embed(
                title="✅ Trigger Channel Removed",
                description=f"Dynamic voice creation disabled for {trigger_channel.mention}",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            logger.info(f"Dynamic voice channel removed: {trigger_channel.name} in {ctx.guild.name}")
        else:
            await ctx.send(f"❌ {trigger_channel.mention} is not configured as a trigger channel!")
    
    @voice.command(name="list")
    @commands.has_permissions(manage_channels=True)
    async def list_triggers(self, ctx):
        """List all configured trigger channels"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.trigger_channels or not self.trigger_channels[guild_id]:
            return await ctx.send("❌ No dynamic voice channels configured!")
        
        embed = discord.Embed(
            title="🎤 Dynamic Voice Channels",
            color=0x0099ff
        )
        
        trigger_info = ""
        created_info = ""
        
        for channel_id, category_id in self.trigger_channels[guild_id].items():
            channel = ctx.guild.get_channel(channel_id)
            category = ctx.guild.get_channel(category_id) if category_id else None
            
            if channel:
                trigger_info += f"• {channel.mention} → {category.name if category else 'Same category'}\n"
        
        # Show created channels
        created_count = len(self.created_channels.get(guild_id, set()))
        for channel_id in self.created_channels.get(guild_id, set()):
            channel = ctx.guild.get_channel(channel_id)
            owner_id = self.channel_owners.get(channel_id)
            owner = ctx.guild.get_member(owner_id) if owner_id else None
            
            if channel:
                created_info += f"• {channel.mention} (Owner: {owner.mention if owner else 'Unknown'})\n"
        
        if trigger_info:
            embed.add_field(name="Trigger Channels", value=trigger_info, inline=False)
        
        if created_info:
            embed.add_field(name=f"Active Created Channels ({created_count})", value=created_info[:1024], inline=False)
        else:
            embed.add_field(name="Active Created Channels", value="None", inline=False)
        
        await ctx.send(embed=embed)
    
    @voice.command(name="cleanup")
    @commands.has_permissions(manage_channels=True)
    async def cleanup_channels(self, ctx):
        """Clean up empty created channels"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.created_channels:
            return await ctx.send("❌ No created channels to clean up!")
        
        cleaned = 0
        channels_to_remove = []
        
        for channel_id in self.created_channels[guild_id].copy():
            channel = ctx.guild.get_channel(channel_id)
            
            if not channel:
                # Channel doesn't exist anymore
                channels_to_remove.append(channel_id)
                cleaned += 1
            elif len(channel.members) == 0:
                # Channel is empty
                try:
                    await channel.delete(reason="Dynamic voice channel cleanup - empty")
                    channels_to_remove.append(channel_id)
                    cleaned += 1
                    logger.info(f"Cleaned up empty voice channel: {channel.name} in {ctx.guild.name}")
                except Exception as e:
                    logger.error(f"Failed to delete channel {channel.name}: {e}")
        
        # Remove from tracking
        for channel_id in channels_to_remove:
            self.created_channels[guild_id].discard(channel_id)
            self.channel_owners.pop(channel_id, None)
        
        await self._save_config(guild_id)
        
        embed = discord.Embed(
            title="🧹 Cleanup Complete",
            description=f"Cleaned up {cleaned} empty voice channels",
            color=0x00ff00 if cleaned > 0 else 0xffaa00
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Handle voice state updates for dynamic channel creation and cleanup"""
        guild_id = member.guild.id
        
        # Check if user joined a trigger channel
        if after.channel and guild_id in self.trigger_channels:
            if after.channel.id in self.trigger_channels[guild_id]:
                await self._create_dynamic_channel(member, after.channel)
        
        # Check if user left a created channel (cleanup)
        if before.channel and guild_id in self.created_channels:
            if before.channel.id in self.created_channels[guild_id]:
                await self._check_channel_cleanup(before.channel)
    
    async def _create_dynamic_channel(self, member: discord.Member, trigger_channel: discord.VoiceChannel):
        """Create a new dynamic voice channel for the user"""
        try:
            guild_id = member.guild.id
            category_id = self.trigger_channels[guild_id][trigger_channel.id]
            category = member.guild.get_channel(category_id) if category_id else trigger_channel.category
            
            # Generate channel name
            channel_name = f"{member.display_name}'s Channel"
            
            # Create the new channel
            overwrites = {
                member.guild.default_role: discord.PermissionOverwrite(connect=True, speak=True, view_channel=True),
                member: discord.PermissionOverwrite(
                    manage_channels=True,
                    manage_permissions=True,
                    move_members=True,
                    mute_members=True,
                    deafen_members=True,
                    priority_speaker=True,
                    manage_messages=True
                )
            }
            
            new_channel = await member.guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                reason=f"Dynamic voice channel for {member.display_name}"
            )
            
            # Track the new channel
            if guild_id not in self.created_channels:
                self.created_channels[guild_id] = set()
            
            self.created_channels[guild_id].add(new_channel.id)
            self.channel_owners[new_channel.id] = member.id
            
            # Move the user to their new channel
            await member.move_to(new_channel, reason="Moved to dynamic voice channel")
            
            # Save configuration
            await self._save_config(guild_id)
            
            logger.info(f"Created dynamic voice channel '{channel_name}' for {member.display_name} in {member.guild.name}")
            
            # Send a welcome message (optional)
            try:
                embed = discord.Embed(
                    title="🎤 Your Voice Channel Created!",
                    description=f"Welcome to your personal voice channel: **{new_channel.name}**",
                    color=0x00ff00
                )
                embed.add_field(
                    name="Your Permissions",
                    value="• Manage channel settings\n"
                          "• Move/mute/deafen users\n"
                          "• Set channel permissions\n"
                          "• Priority speaker",
                    inline=False
                )
                embed.add_field(
                    name="Channel Commands",
                    value="`!voice rename <name>` - Rename your channel\n"
                          "`!voice limit <number>` - Set user limit\n"
                          "`!voice lock` - Lock your channel\n"
                          "`!voice unlock` - Unlock your channel",
                    inline=False
                )
                embed.set_footer(text="This channel will be deleted when empty")
                
                await member.send(embed=embed)
            except discord.Forbidden:
                pass  # User has DMs disabled
                
        except Exception as e:
            logger.error(f"Failed to create dynamic voice channel for {member.display_name}: {e}")
    
    async def _check_channel_cleanup(self, channel: discord.VoiceChannel):
        """Check if a created channel should be cleaned up"""
        try:
            # Wait a moment to ensure all voice state updates are processed
            await asyncio.sleep(2)
            
            if len(channel.members) == 0:
                guild_id = channel.guild.id
                
                # Remove from tracking
                if guild_id in self.created_channels:
                    self.created_channels[guild_id].discard(channel.id)
                self.channel_owners.pop(channel.id, None)
                
                # Delete the channel
                await channel.delete(reason="Dynamic voice channel cleanup - empty")
                
                # Save configuration
                await self._save_config(guild_id)
                
                logger.info(f"Auto-deleted empty dynamic voice channel: {channel.name} in {channel.guild.name}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup channel {channel.name}: {e}")
    
    # User commands for managing their own channels
    @commands.command(name="rename")
    async def rename_channel(self, ctx, *, name: str):
        """Rename your dynamic voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        
        # Check if this is a created channel and user is the owner
        if channel.id not in self.channel_owners:
            return await ctx.send("❌ This is not a dynamic voice channel!")
        
        if self.channel_owners[channel.id] != ctx.author.id:
            return await ctx.send("❌ You don't own this voice channel!")
        
        if len(name) > 100:
            return await ctx.send("❌ Channel name must be 100 characters or less!")
        
        try:
            old_name = channel.name
            await channel.edit(name=name, reason=f"Renamed by {ctx.author.display_name}")
            
            embed = discord.Embed(
                title="✅ Channel Renamed",
                description=f"**{old_name}** → **{name}**",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to rename channel: {e}")
    
    @commands.command(name="limit")
    async def set_user_limit(self, ctx, limit: int):
        """Set user limit for your dynamic voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        
        # Check if this is a created channel and user is the owner
        if channel.id not in self.channel_owners:
            return await ctx.send("❌ This is not a dynamic voice channel!")
        
        if self.channel_owners[channel.id] != ctx.author.id:
            return await ctx.send("❌ You don't own this voice channel!")
        
        if not 0 <= limit <= 99:
            return await ctx.send("❌ User limit must be between 0 and 99! (0 = no limit)")
        
        try:
            await channel.edit(user_limit=limit, reason=f"User limit set by {ctx.author.display_name}")
            
            embed = discord.Embed(
                title="✅ User Limit Updated",
                description=f"User limit set to: **{limit if limit > 0 else 'No limit'}**",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to set user limit: {e}")
    
    @commands.command(name="lock")
    async def lock_channel(self, ctx):
        """Lock your dynamic voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        
        # Check if this is a created channel and user is the owner
        if channel.id not in self.channel_owners:
            return await ctx.send("❌ This is not a dynamic voice channel!")
        
        if self.channel_owners[channel.id] != ctx.author.id:
            return await ctx.send("❌ You don't own this voice channel!")
        
        try:
            # Deny connect permission for @everyone
            await channel.set_permissions(
                ctx.guild.default_role,
                connect=False,
                reason=f"Channel locked by {ctx.author.display_name}"
            )
            
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description="Your voice channel is now locked. Only current members can stay.",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to lock channel: {e}")
    
    @commands.command(name="unlock")
    async def unlock_channel(self, ctx):
        """Unlock your dynamic voice channel"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        
        # Check if this is a created channel and user is the owner
        if channel.id not in self.channel_owners:
            return await ctx.send("❌ This is not a dynamic voice channel!")
        
        if self.channel_owners[channel.id] != ctx.author.id:
            return await ctx.send("❌ You don't own this voice channel!")
        
        try:
            # Allow connect permission for @everyone
            await channel.set_permissions(
                ctx.guild.default_role,
                connect=True,
                reason=f"Channel unlocked by {ctx.author.display_name}"
            )
            
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="Your voice channel is now unlocked. Anyone can join.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to unlock channel: {e}")


async def setup(bot):
    await bot.add_cog(DynamicVoiceChannels(bot))