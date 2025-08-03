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
        self.music = None
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
        # Initialize LavaLink client
        if self.bot.user:
            self.bot.music = lavalink.Client(self.bot.user.id)
            self.bot.music.add_node('127.0.0.1', 2333, 'youshallnotpass', 'us', 10)
            self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
            self.music = self.bot.music
        
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
        if not self.music:
            return None
        return self.music.player_manager.get(guild.id)

    @commands.hybrid_command(name='join', description="Join a voice channel")
    async def join(self, ctx):
        """Join the user's voice channel."""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        channel = ctx.author.voice.channel
        try:
            player = self.music.player_manager.create(guild_id=ctx.guild.id, endpoint=str(channel.guild.region))
            if not player.is_connected:
                player.store('channel', ctx.channel.id)
                await self.connect_to(ctx.guild.id, str(channel.id), self_deaf=True)
            await ctx.send(f"✅ Joined {channel.name}!")
        except Exception as e:
            await ctx.send(f"❌ Failed to join voice channel: {e}")

    async def connect_to(self, guild_id: int, channel_id: str, self_deaf: bool = True):
        """Connect to a voice channel."""
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id, self_deaf=self_deaf)

    @commands.hybrid_command(name='play', description="Play a song from YouTube or other sources")
    @app_commands.describe(query="The song to play (URL or search term)")
    async def play(self, ctx, *, query: str):
        """Play a song."""
        if not ctx.author.voice:
            await ctx.send("❌ You need to be in a voice channel first!")
            return

        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player:
            await ctx.send("❌ Please join a voice channel first with `/join`!")
            return

        # Search for the track
        query = query.strip('<>')
        if not re.match(r'https?://', query):
            query = f'ytsearch:{query}'

        try:
            tracks = await self.music.get_tracks(query)
            if not tracks:
                await ctx.send("❌ No tracks found!")
                return

            track = tracks[0]
            player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.play()
                await ctx.send(f"🎵 Now playing: **{track.title}**")
            else:
                await ctx.send(f"✅ Added to queue: **{track.title}**")

        except Exception as e:
            await ctx.send(f"❌ Error playing track: {e}")

    @commands.hybrid_command(name='pause', description="Pause the currently playing song")
    async def pause(self, ctx):
        """Pause the current song."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.is_playing:
            await ctx.send("❌ Nothing is currently playing!")
            return

        await player.set_pause(True)
        await ctx.send("⏸️ Paused the music!")

    @commands.hybrid_command(name='resume', description="Resume the currently paused song")
    async def resume(self, ctx):
        """Resume the current song."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.is_playing:
            await ctx.send("❌ Nothing is currently playing!")
            return

        await player.set_pause(False)
        await ctx.send("▶️ Resumed the music!")

    @commands.hybrid_command(name='stop', description="Stop playing and clear the queue")
    @commands.has_permissions(ban_members=True)
    async def stop(self, ctx):
        """Stop playing and clear the queue."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player:
            await ctx.send("❌ Nothing is currently playing!")
            return

        player.queue.clear()
        await player.stop()
        await ctx.send("⏹️ Stopped playing and cleared the queue!")

    @commands.hybrid_command(name='skip', description="Skip the currently playing song")
    async def skip(self, ctx):
        """Skip the current song."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.is_playing:
            await ctx.send("❌ Nothing is currently playing!")
            return

        await player.skip()
        await ctx.send("⏭️ Skipped the current song!")

    @commands.hybrid_command(name='queue', description="Show the music queue")
    async def queue(self, ctx):
        """Show the current queue."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.queue:
            await ctx.send("❌ The queue is empty!")
            return

        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blue())
        
        for i, track in enumerate(player.queue[:10], 1):
            duration = str(timedelta(seconds=track.length // 1000))
            embed.add_field(
                name=f"{i}. {track.title}",
                value=f"Duration: {duration} | Requested by <@{track.requester}>",
                inline=False
            )

        if len(player.queue) > 10:
            embed.set_footer(text=f"And {len(player.queue) - 10} more tracks...")

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='now', description="Show currently playing song")
    async def now(self, ctx):
        """Show the currently playing song."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.is_playing:
            await ctx.send("❌ Nothing is currently playing!")
            return

        track = player.current
        duration = str(timedelta(seconds=track.length // 1000))
        
        embed = discord.Embed(title="🎵 Now Playing", color=discord.Color.green())
        embed.add_field(name="Title", value=track.title, inline=False)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Requested by", value=f"<@{track.requester}>", inline=True)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='leave', description="Leave the voice channel")
    async def leave(self, ctx):
        """Leave the voice channel."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player:
            await ctx.send("❌ I'm not in a voice channel!")
            return

        await player.disconnect()
        await ctx.send("👋 Left the voice channel!")

    @commands.hybrid_command(name='volume', description="Set the volume")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx, volume: int):
        """Set the volume."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        if not 0 <= volume <= 100:
            await ctx.send("❌ Volume must be between 0 and 100!")
            return

        player = self.get_player(ctx.guild)
        if not player:
            await ctx.send("❌ Nothing is currently playing!")
            return

        await player.set_volume(volume)
        await ctx.send(f"🔊 Volume set to {volume}%!")

    @commands.hybrid_command(name='shuffle', description="Shuffle the queue")
    async def shuffle(self, ctx):
        """Shuffle the queue."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or len(player.queue) < 2:
            await ctx.send("❌ Need at least 2 tracks in queue to shuffle!")
            return

        player.queue.shuffle()
        await ctx.send("🔀 Queue shuffled!")

    @commands.hybrid_command(name='clear', description="Clear the queue")
    @commands.has_permissions(ban_members=True)
    async def clear(self, ctx):
        """Clear the queue."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player:
            await ctx.send("❌ Nothing is currently playing!")
            return

        player.queue.clear()
        await ctx.send("🗑️ Queue cleared!")

    @commands.hybrid_command(name='remove', description="Remove a track from the queue")
    @app_commands.describe(position="Position in queue (1, 2, 3, etc.)")
    async def remove(self, ctx, position: int):
        """Remove a track from the queue."""
        if not self.music:
            await ctx.send("❌ Music system is not ready yet. Please wait a moment.")
            return

        player = self.get_player(ctx.guild)
        if not player or not player.queue:
            await ctx.send("❌ The queue is empty!")
            return

        if position < 1 or position > len(player.queue):
            await ctx.send(f"❌ Invalid position! Queue has {len(player.queue)} tracks.")
            return

        removed_track = player.queue.pop(position - 1)
        await ctx.send(f"✅ Removed **{removed_track.title}** from the queue!")

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
            await asyncio.sleep(60)  # Wait 1 minute
            if not player.queue:
                await player.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates."""
        if member.id == self.bot.user.id:
            return

        if not self.music:
            return

        player = self.get_player(member.guild)
        if not player:
            return

        # If everyone left the voice channel
        if len([m for m in member.guild.voice_channels[0].members if not m.bot]) == 0:
            await player.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))