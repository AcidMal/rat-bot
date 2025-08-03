import discord
from discord.ext import commands
import wavelink
from typing import Optional, List
import asyncio
from datetime import datetime
import json

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.queue: List[wavelink.Track] = []
        self.current_track: Optional[wavelink.Track] = None
        self.volume = 100
        self.loop_mode = 'none'  # none, single, queue
        self.is_playing = False
    
    def add_track(self, track: wavelink.Track):
        """Add a track to the queue"""
        self.queue.append(track)
    
    def get_next_track(self) -> Optional[wavelink.Track]:
        """Get the next track from queue"""
        if not self.queue:
            return None
        
        track = self.queue.pop(0)
        
        if self.loop_mode == 'single' and self.current_track:
            self.queue.insert(0, self.current_track)
        elif self.loop_mode == 'queue' and self.current_track:
            self.queue.append(self.current_track)
        
        return track

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}
    
    def get_player(self, guild_id: int) -> MusicPlayer:
        """Get or create a music player for a guild"""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(self.bot)
        return self.players[guild_id]
    
    @commands.command(name='join', aliases=['j'])
    async def join(self, ctx):
        """Join a voice channel"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Error",
                description="You need to be in a voice channel to use this command!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        channel = ctx.author.voice.channel
        try:
            await channel.connect(cls=wavelink.Player)
            embed = discord.Embed(
                title="✅ Connected",
                description=f"Joined {channel.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to join voice channel: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query: str):
        """Play a song"""
        if not ctx.author.voice:
            embed = discord.Embed(
                title="❌ Error",
                description="You need to be in a voice channel to use this command!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if not ctx.voice_client:
            await ctx.invoke(self.join)
        
        player = ctx.voice_client
        
        # Search for the track
        try:
            tracks = await wavelink.YouTubeTrack.search(query)
            if not tracks:
                embed = discord.Embed(
                    title="❌ Error",
                    description="No tracks found for your query.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            track = tracks[0]
            music_player = self.get_player(ctx.guild.id)
            
            if player.is_playing():
                # Add to queue
                music_player.add_track(track)
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{track.title}** has been added to the queue.",
                    color=0x00ff00
                )
                embed.add_field(name="Duration", value=str(track.duration))
                embed.add_field(name="Position in Queue", value=len(music_player.queue))
                await ctx.send(embed=embed)
            else:
                # Play immediately
                await player.play(track)
                music_player.current_track = track
                music_player.is_playing = True
                
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{track.title}**",
                    color=0x00ff00
                )
                embed.add_field(name="Duration", value=str(track.duration))
                embed.add_field(name="Requested by", value=ctx.author.mention)
                await ctx.send(embed=embed)
                
                # Save to database
                await self.bot.db.update_music_queue(
                    ctx.guild.id,
                    current_track={
                        'title': track.title,
                        'uri': track.uri,
                        'duration': track.duration,
                        'requester_id': ctx.author.id
                    }
                )
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to play track: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='pause')
    async def pause(self, ctx):
        """Pause the current track"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            embed = discord.Embed(
                title="❌ Error",
                description="Nothing is currently playing.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.pause()
        embed = discord.Embed(
            title="⏸️ Paused",
            description="The current track has been paused.",
            color=0xffff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='resume')
    async def resume(self, ctx):
        """Resume the current track"""
        if not ctx.voice_client or not ctx.voice_client.is_paused():
            embed = discord.Embed(
                title="❌ Error",
                description="Nothing is currently paused.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.resume()
        embed = discord.Embed(
            title="▶️ Resumed",
            description="The current track has been resumed.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='stop')
    async def stop(self, ctx):
        """Stop playing and clear the queue"""
        if not ctx.voice_client:
            embed = discord.Embed(
                title="❌ Error",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.disconnect()
        music_player = self.get_player(ctx.guild.id)
        music_player.queue.clear()
        music_player.current_track = None
        music_player.is_playing = False
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Playback has been stopped and the queue has been cleared.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='skip', aliases=['s'])
    async def skip(self, ctx):
        """Skip the current track"""
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            embed = discord.Embed(
                title="❌ Error",
                description="Nothing is currently playing.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.stop()
        embed = discord.Embed(
            title="⏭️ Skipped",
            description="The current track has been skipped.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        """Show the current queue"""
        music_player = self.get_player(ctx.guild.id)
        
        if not music_player.current_track and not music_player.queue:
            embed = discord.Embed(
                title="📋 Queue",
                description="The queue is empty.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Music Queue",
            color=0x00ff00
        )
        
        if music_player.current_track:
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{music_player.current_track.title}**",
                inline=False
            )
        
        if music_player.queue:
            queue_text = ""
            for i, track in enumerate(music_player.queue[:10], 1):
                queue_text += f"{i}. **{track.title}**\n"
            
            if len(music_player.queue) > 10:
                queue_text += f"\n... and {len(music_player.queue) - 10} more tracks"
            
            embed.add_field(
                name="📝 Up Next",
                value=queue_text,
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name='volume', aliases=['vol'])
    async def volume(self, ctx, volume: int):
        """Set the volume (0-100)"""
        if not ctx.voice_client:
            embed = discord.Embed(
                title="❌ Error",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if not 0 <= volume <= 100:
            embed = discord.Embed(
                title="❌ Error",
                description="Volume must be between 0 and 100.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        ctx.voice_client.volume = volume / 100
        music_player = self.get_player(ctx.guild.id)
        music_player.volume = volume
        
        embed = discord.Embed(
            title="🔊 Volume",
            description=f"Volume set to {volume}%",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name='leave', aliases=['disconnect', 'dc'])
    async def leave(self, ctx):
        """Leave the voice channel"""
        if not ctx.voice_client:
            embed = discord.Embed(
                title="❌ Error",
                description="I'm not connected to a voice channel.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await ctx.voice_client.disconnect()
        music_player = self.get_player(ctx.guild.id)
        music_player.queue.clear()
        music_player.current_track = None
        music_player.is_playing = False
        
        embed = discord.Embed(
            title="👋 Disconnected",
            description="I've left the voice channel.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, reason):
        """Handle track ending"""
        guild_id = player.guild.id
        music_player = self.get_player(guild_id)
        
        # Get next track from queue
        next_track = music_player.get_next_track()
        
        if next_track:
            # Play next track
            await player.play(next_track)
            music_player.current_track = next_track
            
            # Update database
            await self.bot.db.update_music_queue(
                guild_id,
                current_track={
                    'title': next_track.title,
                    'uri': next_track.uri,
                    'duration': next_track.duration,
                    'requester_id': getattr(next_track, 'requester_id', None)
                }
            )
        else:
            # No more tracks, stop playing
            music_player.current_track = None
            music_player.is_playing = False
            
            # Update database
            await self.bot.db.update_music_queue(guild_id, current_track=None)

async def setup(bot):
    await bot.add_cog(Music(bot)) 