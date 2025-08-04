import discord
from discord.ext import commands
import asyncio
import wavelink
import yt_dlp
import os
import json
import tempfile
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from loguru import logger
import subprocess
import shutil
from urllib.parse import urlparse
import re

class YTDLPPlayer:
    """Custom audio player using yt-dlp for YouTube and other sources"""
    
    def __init__(self, voice_client: discord.VoiceClient, guild_id: int, db=None):
        self.voice_client = voice_client
        self.guild_id = guild_id
        self.db = db
        
        # Queue management
        self.queue = []
        self.current_track = None
        self.history = []
        
        # Player state
        self.is_playing = False
        self.is_paused = False
        self.loop_mode = "none"  # none, track, queue
        self.volume = 1.0
        
        # Statistics
        self.tracks_played = 0
        self.total_playtime = 0
        self.session_start = datetime.now(timezone.utc)
        
        # Concurrency control
        self._processing_next_track = False
        self._track_lock = asyncio.Lock()
        
        # yt-dlp configuration
        self._setup_ytdlp()
    
    def _setup_ytdlp(self):
        """Setup yt-dlp with optimal configuration"""
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(tempfile.gettempdir(), 'ytdlp_%(id)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'extractaudio': True,
            'audioformat': 'best',
            'prefer_ffmpeg': True,
        }
        
        # Add cookies if available
        cookies_paths = [
            'cookies.txt',
            '/rat-bot/cookies.txt',
            os.path.expanduser('~/cookies.txt'),
            'data/cookies.txt'
        ]
        
        for cookies_path in cookies_paths:
            if os.path.exists(cookies_path):
                self.ytdl_opts['cookiefile'] = cookies_path
                logger.info(f"Using cookies from: {cookies_path}")
                break
        else:
            logger.warning("No cookies file found. YouTube access may be limited.")
    
    async def search(self, query: str, source: str = "auto") -> List[Dict]:
        """Search for tracks using yt-dlp or fallback to Lavalink"""
        try:
            # Determine search strategy
            if source == "youtube" or query.startswith("yt:"):
                query = query.replace("yt:", "").strip()
                return await self._search_youtube(query)
            elif source == "soundcloud" or query.startswith("sc:"):
                query = query.replace("sc:", "").strip()
                return await self._search_soundcloud(query)
            elif source == "auto":
                # Try multiple sources
                results = await self._search_youtube(query)
                if not results:
                    results = await self._search_soundcloud(query)
                if not results:
                    results = await self._search_bandcamp(query)
                return results
            else:
                # Use Lavalink for other sources
                return await self._search_lavalink(query, source)
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def _search_youtube(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search YouTube using yt-dlp"""
        try:
            search_query = f"ytsearch{max_results}:{query}"
            
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(search_query, download=False)
                )
                
                if not info or 'entries' not in info:
                    return []
                
                results = []
                for entry in info['entries']:
                    if entry:
                        results.append({
                            'title': entry.get('title', 'Unknown'),
                            'url': entry.get('url', ''),
                            'webpage_url': entry.get('webpage_url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Unknown'),
                            'view_count': entry.get('view_count', 0),
                            'source': 'youtube',
                            'id': entry.get('id', ''),
                            'thumbnail': entry.get('thumbnail', ''),
                            'description': entry.get('description', '')[:200] + '...' if entry.get('description') else ''
                        })
                
                logger.info(f"YouTube search found {len(results)} results for: {query}")
                return results
                
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    async def _search_soundcloud(self, query: str) -> List[Dict]:
        """Search SoundCloud using Lavalink"""
        try:
            tracks = await wavelink.Playable.search(f"scsearch:{query}")
            if not tracks:
                return []
            
            results = []
            for track in tracks[:10]:  # Limit to 10 results
                results.append({
                    'title': track.title,
                    'url': track.uri,
                    'webpage_url': track.uri,
                    'duration': track.length // 1000 if track.length else 0,
                    'uploader': track.author or 'Unknown',
                    'source': 'soundcloud',
                    'id': track.identifier,
                    'thumbnail': track.artwork,
                    'description': ''
                })
            
            logger.info(f"SoundCloud search found {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"SoundCloud search failed: {e}")
            return []
    
    async def _search_bandcamp(self, query: str) -> List[Dict]:
        """Search Bandcamp using Lavalink"""
        try:
            tracks = await wavelink.Playable.search(f"bcsearch:{query}")
            if not tracks:
                return []
            
            results = []
            for track in tracks[:10]:  # Limit to 10 results
                results.append({
                    'title': track.title,
                    'url': track.uri,
                    'webpage_url': track.uri,
                    'duration': track.length // 1000 if track.length else 0,
                    'uploader': track.author or 'Unknown',
                    'source': 'bandcamp',
                    'id': track.identifier,
                    'thumbnail': track.artwork,
                    'description': ''
                })
            
            logger.info(f"Bandcamp search found {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Bandcamp search failed: {e}")
            return []
    
    async def _search_lavalink(self, query: str, source: str) -> List[Dict]:
        """Fallback search using Lavalink"""
        try:
            search_query = f"{source}search:{query}" if source != "auto" else query
            tracks = await wavelink.Playable.search(search_query)
            
            if not tracks:
                return []
            
            results = []
            for track in tracks[:10]:
                results.append({
                    'title': track.title,
                    'url': track.uri,
                    'webpage_url': track.uri,
                    'duration': track.length // 1000 if track.length else 0,
                    'uploader': track.author or 'Unknown',
                    'source': source,
                    'id': track.identifier,
                    'thumbnail': getattr(track, 'artwork', ''),
                    'description': ''
                })
            
            logger.info(f"Lavalink search found {len(results)} results for: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Lavalink search failed: {e}")
            return []
    
    async def add_to_queue(self, track_data: Dict, requester: discord.Member = None):
        """Add a track to the queue"""
        track_data['requester'] = requester
        track_data['requested_at'] = datetime.now(timezone.utc)
        
        # Add to database if available
        if self.db:
            try:
                await self.db.add_to_queue(self.guild_id, track_data)
            except Exception as e:
                logger.error(f"Failed to add track to database queue: {e}")
        
        # Add to local queue
        self.queue.append(track_data)
        logger.info(f"Added to queue: {track_data['title']} (Position: {len(self.queue)})")
    
    async def play_next(self):
        """Play the next track in the queue"""
        async with self._track_lock:
            if self._processing_next_track:
                logger.info("Already processing next track, skipping...")
                return
            
            self._processing_next_track = True
            
            try:
                # Get next track from queue
                if not self.queue:
                    if self.loop_mode == "queue" and self.history:
                        # Restart queue
                        self.queue = self.history.copy()
                        self.history.clear()
                        logger.info("Restarting queue loop")
                    else:
                        logger.info("Queue is empty")
                        self.current_track = None
                        self.is_playing = False
                        return
                
                # Get next track
                if self.loop_mode == "track" and self.current_track:
                    next_track = self.current_track
                else:
                    next_track = self.queue.pop(0)
                    
                    # Remove from database if available
                    if self.db:
                        try:
                            await self.db.get_next_in_queue(self.guild_id)
                        except Exception as e:
                            logger.error(f"Failed to remove track from database queue: {e}")
                
                logger.info(f"Playing next track: {next_track['title']} (Source: {next_track['source']})")
                await self._play_track(next_track)
                
            except Exception as e:
                logger.error(f"Error in play_next: {e}")
                # Try to continue with next track
                if self.queue:
                    await asyncio.sleep(1)
                    await self.play_next()
            
            finally:
                self._processing_next_track = False
    
    async def _play_track(self, track_data: Dict):
        """Play a specific track"""
        try:
            self.current_track = track_data
            
            if track_data['source'] == 'youtube':
                await self._play_youtube_track(track_data)
            else:
                await self._play_lavalink_track(track_data)
                
        except Exception as e:
            logger.error(f"Failed to play track {track_data['title']}: {e}")
            # Try next track
            await self.play_next()
    
    async def _play_youtube_track(self, track_data: Dict):
        """Play a YouTube track using yt-dlp"""
        try:
            # Extract audio URL using yt-dlp
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(track_data['webpage_url'], download=False)
                )
                
                if not info:
                    raise Exception("Failed to extract track info")
                
                # Get the best audio URL
                audio_url = info.get('url')
                if not audio_url:
                    raise Exception("No audio URL found")
                
                # Create FFmpeg source
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': f'-vn -filter:a "volume={self.volume}"'
                }
                
                source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
                
                # Play the track
                self.voice_client.play(source, after=lambda e: asyncio.create_task(self._track_finished(e)))
                self.is_playing = True
                self.is_paused = False
                
                logger.info(f"Started playing YouTube track: {track_data['title']}")
                
        except Exception as e:
            logger.error(f"Failed to play YouTube track: {e}")
            raise
    
    async def _play_lavalink_track(self, track_data: Dict):
        """Play a non-YouTube track using yt-dlp fallback"""
        try:
            # Try to use yt-dlp for all sources for consistency
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(track_data['url'], download=False)
                )
                
                if not info:
                    raise Exception("Failed to extract track info")
                
                audio_url = info.get('url', track_data['url'])
                
                ffmpeg_options = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': f'-vn -filter:a "volume={self.volume}"'
                }
                
                source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
                self.voice_client.play(source, after=lambda e: asyncio.create_task(self._track_finished(e)))
                self.is_playing = True
                self.is_paused = False
                
                logger.info(f"Started playing track: {track_data['title']}")
                
        except Exception as e:
            logger.error(f"Failed to play track via yt-dlp fallback: {e}")
            raise
    
    async def _track_finished(self, error):
        """Handle track completion"""
        if error:
            logger.error(f"Player error: {error}")
        
        if self.current_track:
            # Add to history (unless it's a loop)
            if self.loop_mode != "track":
                self.history.append(self.current_track)
                # Limit history size
                if len(self.history) > 50:
                    self.history.pop(0)
            
            # Update statistics
            self.tracks_played += 1
            if self.current_track.get('duration'):
                self.total_playtime += self.current_track['duration']
        
        self.is_playing = False
        
        # Play next track
        await self.play_next()
    
    async def skip(self):
        """Skip the current track"""
        if self.voice_client.is_playing():
            self.voice_client.stop()
        else:
            await self.play_next()
    
    def pause(self):
        """Pause playback"""
        if self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
    
    def resume(self):
        """Resume playback"""
        if self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
    
    def stop(self):
        """Stop playback and clear queue"""
        if self.voice_client.is_playing() or self.voice_client.is_paused():
            self.voice_client.stop()
        self.queue.clear()
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
    
    async def set_volume(self, volume: float):
        """Set playback volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        # Note: Volume changes will apply to the next track
        # For real-time volume control, we'd need to implement audio filtering
    
    async def clear_queue(self):
        """Clear the queue"""
        cleared_count = len(self.queue)
        self.queue.clear()
        
        if self.db:
            try:
                await self.db.clear_queue(self.guild_id)
            except Exception as e:
                logger.error(f"Failed to clear database queue: {e}")
        
        return cleared_count
    
    def get_queue_info(self) -> Dict:
        """Get information about the current queue"""
        return {
            'current': self.current_track,
            'queue': self.queue.copy(),
            'queue_length': len(self.queue),
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'loop_mode': self.loop_mode,
            'volume': self.volume,
            'history_length': len(self.history),
            'tracks_played': self.tracks_played,
            'total_playtime': self.total_playtime
        }


class Music(commands.Cog):
    """Advanced music cog using yt-dlp with cookies support"""
    
    def __init__(self, bot):
        self.bot = bot
        self.players: Dict[int, YTDLPPlayer] = {}
    
    def get_player(self, guild: discord.Guild) -> Optional[YTDLPPlayer]:
        """Get or create a player for the guild"""
        return self.players.get(guild.id)
    
    async def connect_player(self, channel: discord.VoiceChannel) -> YTDLPPlayer:
        """Connect to a voice channel and create a player"""
        try:
            # Disconnect existing connection
            if channel.guild.voice_client:
                await channel.guild.voice_client.disconnect(force=True)
            
            # Connect to voice channel
            voice_client = await channel.connect(timeout=30.0, reconnect=True)
            
            # Create player
            player = YTDLPPlayer(voice_client, channel.guild.id, self.bot.db)
            self.players[channel.guild.id] = player
            
            logger.info(f"Connected to voice channel: {channel.name} in {channel.guild.name}")
            return player
            
        except Exception as e:
            logger.error(f"Failed to connect to voice channel {channel.name}: {e}")
            raise
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        """Play a song or add it to the queue"""
        if not query:
            return await ctx.send("❌ Please provide a song to play!")
        
        # Get user's voice channel
        if not ctx.author.voice:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        channel = ctx.author.voice.channel
        
        # Get or create player
        player = self.get_player(ctx.guild)
        if not player or not ctx.guild.voice_client:
            try:
                player = await self.connect_player(channel)
            except Exception as e:
                return await ctx.send(f"❌ Failed to connect to voice channel: {e}")
        
        # Show searching message
        search_msg = await ctx.send(f"🔍 Searching for: `{query}`...")
        
        try:
            # Determine source from query
            source = "auto"
            if query.startswith("yt:"):
                source = "youtube"
            elif query.startswith("sc:"):
                source = "soundcloud"
            
            # Search for tracks
            results = await player.search(query, source)
            
            if not results:
                return await search_msg.edit(content="❌ No results found!")
            
            # Take the first result
            track = results[0]
            
            # Add requester info
            track['requester'] = ctx.author
            
            # If nothing is playing, start immediately
            if not player.is_playing and not player.queue:
                await search_msg.edit(content=f"🎵 Loading: **{track['title']}**...")
                await player._play_track(track)
                
                embed = discord.Embed(
                    title="🎵 Now Playing",
                    description=f"**{track['title']}**",
                    color=0x00ff00
                )
                embed.add_field(name="Duration", value=self._format_duration(track['duration']), inline=True)
                embed.add_field(name="Source", value=track['source'].title(), inline=True)
                embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                
                if track.get('thumbnail'):
                    embed.set_thumbnail(url=track['thumbnail'])
                
                await search_msg.edit(content=None, embed=embed)
                
            else:
                # Add to queue
                await player.add_to_queue(track, ctx.author)
                
                embed = discord.Embed(
                    title="📝 Added to Queue",
                    description=f"**{track['title']}**",
                    color=0x0099ff
                )
                embed.add_field(name="Position", value=f"#{len(player.queue)}", inline=True)
                embed.add_field(name="Duration", value=self._format_duration(track['duration']), inline=True)
                embed.add_field(name="Source", value=track['source'].title(), inline=True)
                
                if track.get('thumbnail'):
                    embed.set_thumbnail(url=track['thumbnail'])
                
                await search_msg.edit(content=None, embed=embed)
        
        except Exception as e:
            logger.error(f"Error in play command: {e}")
            await search_msg.edit(content=f"❌ Error: {e}")
    
    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        """Skip the current track"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        if not player.is_playing:
            return await ctx.send("❌ Nothing is playing!")
        
        current_title = player.current_track['title'] if player.current_track else "Unknown"
        await player.skip()
        
        embed = discord.Embed(
            title="⏭️ Track Skipped",
            description=f"Skipped: **{current_title}**",
            color=0xff9900
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the current track"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        if not player.is_playing:
            return await ctx.send("❌ Nothing is playing!")
        
        if player.is_paused:
            return await ctx.send("❌ Already paused!")
        
        player.pause()
        
        embed = discord.Embed(
            title="⏸️ Paused",
            description="Playback paused",
            color=0xffff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resume the current track"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        if not player.is_paused:
            return await ctx.send("❌ Not paused!")
        
        player.resume()
        
        embed = discord.Embed(
            title="▶️ Resumed",
            description="Playback resumed",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stop playback and clear the queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        player.stop()
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Playback stopped and queue cleared",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx):
        """Show the current queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        queue_info = player.get_queue_info()
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=0x0099ff
        )
        
        # Current track
        if queue_info['current']:
            current = queue_info['current']
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**{current['title']}**\n"
                      f"Duration: {self._format_duration(current['duration'])}\n"
                      f"Source: {current['source'].title()}\n"
                      f"Requested by: {current['requester'].mention if current.get('requester') else 'Unknown'}",
                inline=False
            )
        
        # Queue
        if queue_info['queue']:
            queue_text = ""
            for i, track in enumerate(queue_info['queue'][:10], 1):
                duration = self._format_duration(track['duration'])
                queue_text += f"`{i}.` **{track['title']}** ({duration}) - {track['source'].title()}\n"
            
            if len(queue_info['queue']) > 10:
                queue_text += f"\n... and {len(queue_info['queue']) - 10} more tracks"
            
            embed.add_field(
                name=f"📝 Queue ({queue_info['queue_length']} tracks)",
                value=queue_text,
                inline=False
            )
        else:
            embed.add_field(
                name="📝 Queue",
                value="Queue is empty",
                inline=False
            )
        
        # Player info
        status = "🎵 Playing" if queue_info['is_playing'] else "⏸️ Paused" if queue_info['is_paused'] else "⏹️ Stopped"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Loop Mode", value=queue_info['loop_mode'].title(), inline=True)
        embed.add_field(name="Volume", value=f"{int(queue_info['volume'] * 100)}%", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="clear")
    async def clear(self, ctx):
        """Clear the queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        if not player.queue:
            return await ctx.send("❌ Queue is empty!")
        
        cleared = await player.clear_queue()
        
        embed = discord.Embed(
            title="🗑️ Queue Cleared",
            description=f"Cleared {cleared} tracks from the queue",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        """Show currently playing track"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice!")
        
        if not player.current_track:
            return await ctx.send("❌ Nothing is playing!")
        
        track = player.current_track
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{track['title']}**",
            color=0x00ff00
        )
        
        embed.add_field(name="Duration", value=self._format_duration(track['duration']), inline=True)
        embed.add_field(name="Source", value=track['source'].title(), inline=True)
        embed.add_field(name="Requested by", value=track['requester'].mention if track.get('requester') else 'Unknown', inline=True)
        
        if track.get('uploader'):
            embed.add_field(name="Uploader", value=track['uploader'], inline=True)
        
        if track.get('thumbnail'):
            embed.set_thumbnail(url=track['thumbnail'])
        
        # Player status
        status = "🎵 Playing" if player.is_playing else "⏸️ Paused"
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Loop", value=player.loop_mode.title(), inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="cookies")
    async def cookies(self, ctx):
        """Check cookies status"""
        embed = discord.Embed(
            title="🍪 Cookies Status",
            color=0x0099ff
        )
        
        cookies_found = False
        cookies_info = ""
        
        cookies_paths = [
            'cookies.txt',
            '/rat-bot/cookies.txt', 
            os.path.expanduser('~/cookies.txt'),
            'data/cookies.txt'
        ]
        
        for path in cookies_paths:
            if os.path.exists(path):
                cookies_found = True
                size = os.path.getsize(path)
                cookies_info += f"✅ **{path}** ({size} bytes)\n"
            else:
                cookies_info += f"❌ **{path}** (not found)\n"
        
        embed.add_field(
            name="Cookie Files",
            value=cookies_info,
            inline=False
        )
        
        if cookies_found:
            embed.add_field(
                name="Status",
                value="✅ Cookies available - Enhanced YouTube access enabled",
                inline=False
            )
            embed.color = 0x00ff00
        else:
            embed.add_field(
                name="Status", 
                value="⚠️ No cookies found - YouTube access may be limited",
                inline=False
            )
            embed.add_field(
                name="Setup Instructions",
                value="Run `python setup_cookies.py` to set up cookies for better YouTube access",
                inline=False
            )
            embed.color = 0xffaa00
        
        await ctx.send(embed=embed)
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS"""
        if not seconds:
            return "Unknown"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


async def setup(bot):
    await bot.add_cog(Music(bot))