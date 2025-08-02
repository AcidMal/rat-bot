import asyncio
import discord
from discord.ext import commands
from discord import app_commands
import lavalink
from datetime import timedelta
import re
import subprocess
import os
import sys
import time
import threading

class Music(commands.Cog):
    """Music commands using LavaLink for better audio processing."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(self.bot.user.id)
        self.bot.music.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 10)
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.music = self.bot.music
        self.lavalink_ready = False
        self.lavalink_process = None
        self.lavalink_started = False

    async def start_lavalink_server(self):
        """Start LavaLink server if not already running."""
        if self.lavalink_started:
            return

        # Check if LavaLink directory exists
        if not os.path.exists('lavalink'):
            print("❌ LavaLink not installed. Please run install_lavalink.sh first.")
            return

        # Check if Lavalink.jar exists
        if not os.path.exists('lavalink/Lavalink.jar'):
            print("❌ Lavalink.jar not found. Please run install_lavalink.sh first.")
            return

        # Check if Java is available
        try:
            subprocess.run(['java', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Java not found. Please install Java 11 or higher.")
            return

        print("🎵 Starting LavaLink server...")
        
        try:
            # Start LavaLink server in background
            self.lavalink_process = subprocess.Popen(
                ['java', '-jar', 'Lavalink.jar'],
                cwd='lavalink',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.lavalink_started = True
            print("✅ LavaLink server started successfully!")
            
            # Wait a moment for server to start
            await asyncio.sleep(3)
            
        except Exception as e:
            print(f"❌ Failed to start LavaLink server: {e}")
            self.lavalink_started = False

    async def stop_lavalink_server(self):
        """Stop LavaLink server."""
        if self.lavalink_process and self.lavalink_process.poll() is None:
            print("🛑 Stopping LavaLink server...")
            self.lavalink_process.terminate()
            try:
                self.lavalink_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.lavalink_process.kill()
            print("✅ LavaLink server stopped.")

    @commands.Cog.listener()
    async def on_ready(self):
        """Initialize LavaLink when bot is ready."""
        # Start LavaLink server
        await self.start_lavalink_server()
        
        # Wait for LavaLink to be ready
        await asyncio.sleep(2)
        
        self.lavalink_ready = True
        print("🎵 Music system ready with LavaLink!")

    @commands.Cog.listener()
    async def on_disconnect(self):
        """Stop LavaLink when bot disconnects."""
        await self.stop_lavalink_server()

    def get_player(self, guild):
        """Get or create a LavaLink player for the guild."""
        return self.music.player_manager.get(guild.id)

    @commands.hybrid_command(name='join', description="Join a voice channel")
    async def join(self, ctx):
        """Join a voice channel."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        player = self.get_player(ctx.guild)
        
        if player is None:
            player = self.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        
        if not player.is_connected:
            await player.connect(channel.id)
            await ctx.send(f"✅ Joined {channel.name}")
        else:
            await ctx.send("✅ Already connected to a voice channel.")

    @commands.hybrid_command(name='play', description="Play a song from YouTube or other sources")
    @app_commands.describe(query="The song to play (URL or search term)")
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube or other sources."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        # Join voice channel if not already connected
        if not self.get_player(ctx.guild) or not self.get_player(ctx.guild).is_connected:
            await self.join(ctx)

        player = self.get_player(ctx.guild)
        
        # Search for the track
        try:
            # Check if it's a URL
            if not query.startswith('http'):
                query = f'ytsearch:{query}'
            
            results = await player.node.get_tracks(query)
            
            if not results or not results['tracks']:
                await ctx.send("❌ No tracks found.")
                return

            track = results['tracks'][0]
            
            # Add track to queue
            player.add(requester=ctx.author.id, track=track)
            
            embed = discord.Embed(title="🎵 Added to Queue", color=0x00ff00)
            embed.add_field(name="Track", value=track.title, inline=False)
            embed.add_field(name="Duration", value=str(timedelta(seconds=track.length // 1000)), inline=True)
            embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
            
            if track.uri:
                embed.add_field(name="URL", value=track.uri, inline=False)
            
            await ctx.send(embed=embed)
            
            # Start playing if not already playing
            if not player.is_playing:
                await player.play()
                
        except Exception as e:
            await ctx.send(f"❌ Error playing track: {str(e)}")

    @commands.hybrid_command(name='pause', description="Pause the currently playing song")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if player.is_playing:
            await player.set_pause(True)
            await ctx.send("⏸️ Paused the music.")
        else:
            await ctx.send("❌ I am not playing anything.")

    @commands.hybrid_command(name='resume', description="Resume the currently paused song")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if player.is_paused:
            await player.set_pause(False)
            await ctx.send("▶️ Resumed the music.")
        else:
            await ctx.send("❌ I am not paused.")

    @commands.hybrid_command(name='stop', description="Stop playing and clear the queue")
    @commands.has_permissions(ban_members=True)
    async def stop(self, ctx):
        """Stop playing and clear the queue."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        player.queue.clear()
        await player.stop()
        await ctx.send("⏹️ Stopped playback and cleared queue.")

    @commands.hybrid_command(name='skip', description="Skip the currently playing song")
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if not player.is_playing:
            await ctx.send("❌ I am not playing anything.")
            return

        await player.skip()
        await ctx.send("⏭️ Skipped the current song.")

    @commands.hybrid_command(name='queue', description="Show the music queue")
    async def queue(self, ctx):
        """Show the music queue."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.queue:
            await ctx.send("📭 The queue is empty.")
            return

        embed = discord.Embed(title="🎵 Music Queue", color=0x00ff00)
        
        # Current track
        if player.current:
            embed.add_field(
                name="🎶 Now Playing",
                value=f"{player.current.title} - {str(timedelta(seconds=player.current.length // 1000))}",
                inline=False
            )
        
        # Queue
        queue_text = ""
        for i, track in enumerate(player.queue[:10], 1):
            duration = str(timedelta(seconds=track.length // 1000))
            queue_text += f"{i}. {track.title} - {duration}\n"
        
        if queue_text:
            embed.add_field(name="📋 Up Next", value=queue_text, inline=False)
        
        if len(player.queue) > 10:
            embed.add_field(name="...", value=f"And {len(player.queue) - 10} more tracks", inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='now', description="Show currently playing song")
    async def now(self, ctx):
        """Show currently playing song."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.current:
            await ctx.send("❌ I am not playing anything.")
            return

        embed = discord.Embed(title="🎶 Now Playing", color=0x00ff00)
        embed.add_field(name="Track", value=player.current.title, inline=False)
        embed.add_field(name="Duration", value=str(timedelta(seconds=player.current.length // 1000)), inline=True)
        
        if player.current.uri:
            embed.add_field(name="URL", value=player.current.uri, inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='leave', description="Leave the voice channel")
    async def leave(self, ctx):
        """Leave the voice channel."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        await player.disconnect()
        await ctx.send("👋 Left the voice channel.")

    @commands.hybrid_command(name='volume', description="Set the volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx, volume: int):
        """Set the volume."""
        if not 0 <= volume <= 100:
            await ctx.send("❌ Volume must be between 0 and 100.")
            return

        player = self.get_player(ctx.guild)
        
        if not player or not player.is_connected:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        await player.set_volume(volume)
        await ctx.send(f"🔊 Volume set to {volume}%")

    @commands.hybrid_command(name='shuffle', description="Shuffle the queue")
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.queue:
            await ctx.send("❌ The queue is empty.")
            return

        player.queue.shuffle()
        await ctx.send("🔀 Queue shuffled!")

    @commands.hybrid_command(name='clear', description="Clear the queue")
    @commands.has_permissions(ban_members=True)
    async def clear(self, ctx):
        """Clear the queue."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.queue:
            await ctx.send("❌ The queue is already empty.")
            return

        player.queue.clear()
        await ctx.send("🗑️ Queue cleared!")

    @commands.hybrid_command(name='remove', description="Remove a track from the queue")
    @app_commands.describe(position="Position in queue (1, 2, 3, etc.)")
    async def remove(self, ctx, position: int):
        """Remove a track from the queue."""
        player = self.get_player(ctx.guild)
        
        if not player or not player.queue:
            await ctx.send("❌ The queue is empty.")
            return

        if position < 1 or position > len(player.queue):
            await ctx.send(f"❌ Invalid position. Queue has {len(player.queue)} tracks.")
            return

        track = player.queue.pop(position - 1)
        await ctx.send(f"✅ Removed '{track.title}' from the queue.")

    @commands.hybrid_command(name='lavalink', description="Check LavaLink server status")
    async def lavalink_status(self, ctx):
        """Check LavaLink server status."""
        if self.lavalink_started and self.lavalink_process and self.lavalink_process.poll() is None:
            embed = discord.Embed(title="🎵 LavaLink Status", color=0x00ff00)
            embed.add_field(name="Status", value="✅ Running", inline=True)
            embed.add_field(name="Process ID", value=str(self.lavalink_process.pid), inline=True)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="🎵 LavaLink Status", color=0xff0000)
            embed.add_field(name="Status", value="❌ Not Running", inline=True)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_lavalink_track_end(self, player, track, reason):
        """Handle track end events."""
        if not player.queue:
            # No more tracks, disconnect after 60 seconds
            await asyncio.sleep(60)
            if not player.queue and not player.is_playing:
                await player.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates."""
        if member.bot:
            return

        # If the bot is alone in a voice channel, disconnect after 60 seconds
        if before.channel and after.channel != before.channel:
            player = self.get_player(member.guild)
            if player and player.is_connected and player.channel_id == before.channel.id:
                members = [m for m in before.channel.members if not m.bot]
                if not members:
                    await asyncio.sleep(60)
                    if player.is_connected and player.channel_id == before.channel.id:
                        await player.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))