import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import yt_dlp
import os
from collections import deque
from datetime import datetime, timedelta
import re
import ssl

# Configure yt-dlp options with SSL certificate handling
yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,  # Disable certificate checking
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    # SSL certificate handling
    'nocheckcertificate': True,
    'extractor_retries': 3,
    'fragment_retries': 3,
    'retries': 3,
    # Additional options for better compatibility
    'prefer_ffmpeg': True,
    'geo_bypass': True,
    'nocheckcertificate': True,
}

ffmpeg_options = {
    'options': '-vn',
}

# Create a custom SSL context that doesn't verify certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Configure yt-dlp with custom SSL context
ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

def extract_info(url, download=True):
    """Extract info from URL using ytdl."""
    return ytdl.extract_info(url, download=download)

def extract_info_fallback(url, download=True):
    """Extract info from URL using fallback options."""
    fallback_options = ytdl_format_options.copy()
    fallback_options.update({
        'nocheckcertificate': True,
        'extractor_retries': 5,
        'fragment_retries': 5,
        'retries': 5,
        'skip_download': True,
    })
    fallback_ytdl = yt_dlp.YoutubeDL(fallback_options)
    return fallback_ytdl.extract_info(url, download=download)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')
        self.uploader_url = data.get('uploader_url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        
        try:
            data = await loop.run_in_executor(None, extract_info, url, not stream)
        except Exception as e:
            # If the first attempt fails, try with additional SSL bypass options
            try:
                data = await loop.run_in_executor(None, extract_info_fallback, url, not stream)
            except Exception as e2:
                raise Exception(f"Failed to extract video info: {e2}")
        
        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]
        
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.channel = ctx.channel
        self.cog = ctx.cog

        self.queue = deque()
        self.next = asyncio.Event()
        self.np = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            # Wait for the next song. If we timeout, player will disconnect
            try:
                async with asyncio.timeout(300):  # 5 minutes
                    await self.next.wait()
            except asyncio.TimeoutError:
                return self.destroy(self.guild)

            if not self.queue:
                continue

            # Get the first song from the queue
            current = self.queue.popleft()

            if not current:
                continue

            # Create the player
            try:
                player = await YTDLSource.from_url(current['url'], loop=self.bot.loop, stream=True)
            except Exception as e:
                await self.channel.send(f'❌ An error occurred while processing your song.\n'
                                      f'```css\n[{e}]\n```\n'
                                      f'**Troubleshooting:**\n'
                                      f'• Try updating yt-dlp: `pip install --upgrade yt-dlp`\n'
                                      f'• Check your internet connection\n'
                                      f'• Try a different song or URL')
                continue

            # Set the volume
            player.volume = 0.5

            # Get the voice client
            voice_client = discord.utils.get(self.bot.voice_clients, guild=self.guild)
            if not voice_client:
                continue

            # Play the song with proper error handling
            def after_playing(error):
                if error:
                    print(f"Error in after callback: {error}")
                self.bot.loop.call_soon_threadsafe(self.next.set)

            voice_client.play(player, after=after_playing)

            # Create the "Now Playing" embed
            embed = discord.Embed(title="🎵 Now Playing", color=discord.Color.green())
            embed.add_field(name="Title", value=player.title, inline=False)
            embed.add_field(name="Duration", value=str(timedelta(seconds=player.duration)) if player.duration else "Unknown", inline=True)
            embed.add_field(name="Uploader", value=f"[{player.uploader}]({player.uploader_url})" if player.uploader_url else player.uploader or "Unknown", inline=True)
            if player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)
            embed.set_footer(text=f"Requested by {current['requester']}")

            self.np = await self.channel.send(embed=embed)

            # Wait for the song to finish
            await self.next.wait()

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self.cog.cleanup(guild))

class Music(commands.Cog):
    """Music commands for playing audio from various sources."""

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, ctx):
        """Retrieve the guild player, or create one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.hybrid_command(name='join', description="Join a voice channel")
    async def join(self, ctx):
        """Join a voice channel."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.send(f"✅ Joined {channel.name}")

    @commands.hybrid_command(name='play', description="Play a song from YouTube or other sources")
    @app_commands.describe(query="The song to play (URL or search term)")
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube or other sources."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        player = self.get_player(ctx)

        # Check if it's a URL
        if not query.startswith('http'):
            query = f'ytsearch:{query}'

        async with ctx.typing():
            try:
                # Extract info from the URL
                data = await self.bot.loop.run_in_executor(None, extract_info, query, False)
                
                if 'entries' in data:
                    # Take first item from a playlist
                    data = data['entries'][0]

                # Add to queue
                player.queue.append({
                    'url': data['webpage_url'],
                    'requester': ctx.author.display_name,
                    'title': data['title']
                })

                embed = discord.Embed(title="✅ Added to Queue", color=discord.Color.green())
                embed.add_field(name="Title", value=data['title'], inline=False)
                embed.add_field(name="Duration", value=str(timedelta(seconds=data['duration'])) if data.get('duration') else "Unknown", inline=True)
                embed.add_field(name="Uploader", value=data.get('uploader', 'Unknown'), inline=True)
                if data.get('thumbnail'):
                    embed.set_thumbnail(url=data['thumbnail'])
                embed.set_footer(text=f"Requested by {ctx.author.display_name}")

                await ctx.send(embed=embed)

            except Exception as e:
                error_msg = f"❌ An error occurred while processing your song.\n```css\n[{e}]\n```"
                
                # Add troubleshooting information
                if "certificate" in str(e).lower() or "ssl" in str(e).lower():
                    error_msg += "\n**SSL Certificate Error Detected!**\n"
                    error_msg += "**Solutions:**\n"
                    error_msg += "• Update yt-dlp: `pip install --upgrade yt-dlp`\n"
                    error_msg += "• Try a different song or URL\n"
                    error_msg += "• Check your internet connection\n"
                    error_msg += "• The bot has been configured to bypass SSL verification"
                else:
                    error_msg += "\n**Troubleshooting:**\n"
                    error_msg += "• Try updating yt-dlp: `pip install --upgrade yt-dlp`\n"
                    error_msg += "• Check your internet connection\n"
                    error_msg += "• Try a different song or URL"
                
                await ctx.send(error_msg)

    @commands.hybrid_command(name='pause', description="Pause the currently playing song")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused the music.")
        else:
            await ctx.send("❌ I am not playing anything.")

    @commands.hybrid_command(name='resume', description="Resume the currently paused song")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed the music.")
        else:
            await ctx.send("❌ I am not paused.")

    @commands.hybrid_command(name='stop', description="Stop playing and clear the queue")
    async def stop(self, ctx):
        """Stop playing and clear the queue."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        # Clear the queue
        if ctx.guild.id in self.players:
            self.players[ctx.guild.id].queue.clear()

        # Stop playing
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped the music and cleared the queue.")

    @commands.hybrid_command(name='skip', description="Skip the currently playing song")
    async def skip(self, ctx):
        """Skip the currently playing song."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped the song.")
        else:
            await ctx.send("❌ I am not playing anything.")

    @commands.hybrid_command(name='queue', description="Show the current music queue")
    async def queue(self, ctx):
        """Show the current music queue."""
        if ctx.guild.id not in self.players:
            await ctx.send("❌ I am not playing anything.")
            return

        player = self.players[ctx.guild.id]
        
        if not player.queue:
            await ctx.send("📭 The queue is empty.")
            return

        embed = discord.Embed(title="📋 Music Queue", color=discord.Color.blue())
        
        for i, song in enumerate(player.queue, 1):
            embed.add_field(
                name=f"{i}. {song['title'][:50]}...",
                value=f"Requested by {song['requester']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='nowplaying', description="Show the currently playing song")
    async def nowplaying(self, ctx):
        """Show the currently playing song."""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("❌ I am not playing anything.")
            return

        if ctx.guild.id in self.players and self.players[ctx.guild.id].np:
            await ctx.send("🎵 Current song:", embed=self.players[ctx.guild.id].np.embeds[0])
        else:
            await ctx.send("❌ No song information available.")

    @commands.hybrid_command(name='volume', description="Set the volume of the music")
    @app_commands.describe(volume="Volume level (0-100)")
    async def volume(self, ctx, volume: int):
        """Set the volume of the music."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if not 0 <= volume <= 100:
            await ctx.send("❌ Volume must be between 0 and 100.")
            return

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Volume set to {volume}%.")

    @commands.hybrid_command(name='leave', description="Leave the voice channel")
    async def leave(self, ctx):
        """Leave the voice channel."""
        if ctx.voice_client is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel.")

        # Clean up the player
        if ctx.guild.id in self.players:
            del self.players[ctx.guild.id]

    @commands.hybrid_command(name='fixmusic', description="Update yt-dlp to fix music issues")
    async def fixmusic(self, ctx):
        """Update yt-dlp to fix music issues."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        await ctx.send("🔄 Updating yt-dlp... This may take a moment.")
        
        try:
            import subprocess
            import sys
            
            # Update yt-dlp
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                await ctx.send("✅ yt-dlp updated successfully! Try playing music again.")
            else:
                await ctx.send(f"❌ Failed to update yt-dlp:\n```{result.stderr}```")
                
        except Exception as e:
            await ctx.send(f"❌ Error updating yt-dlp: {e}")

    async def cleanup(self, guild):
        """Clean up the player for a guild."""
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates."""
        if member.bot:
            return

        # If the bot is alone in a voice channel, disconnect after 60 seconds
        if before.channel and after.channel != before.channel:
            voice_client = discord.utils.get(self.bot.voice_clients, guild=member.guild)
            if voice_client and voice_client.channel == before.channel:
                members = [m for m in before.channel.members if not m.bot]
                if not members:
                    await asyncio.sleep(60)
                    if voice_client.channel == before.channel:
                        await voice_client.disconnect()
                        if member.guild.id in self.players:
                            del self.players[member.guild.id]

async def setup(bot):
    await bot.add_cog(Music(bot)) 