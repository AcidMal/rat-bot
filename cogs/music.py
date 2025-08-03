import discord
from discord.ext import commands
import wavelink
import asyncio
import math
import re
import yt_dlp
from typing import Optional, List, Dict, Union
from datetime import datetime, timezone, timedelta
from loguru import logger
from core.db_queue import DatabaseQueue

class MusicPlayer(wavelink.Player):
    """Enhanced music player with advanced features"""
    
    def __init__(self, *args, **kwargs):
        # Extract database from kwargs
        self.db = kwargs.pop('db', None)
        super().__init__(*args, **kwargs)
        
        # Queue management - use database queue if available
        if self.db and hasattr(self, 'guild') and self.guild:
            self.queue = DatabaseQueue(self.guild.id, self.db)
        else:
            self.queue = wavelink.Queue()  # Fallback to wavelink queue
        
        self.history = []
        self.loop_mode = "none"  # none, track, queue
        
        # Player state
        self.is_locked = False
        self.locked_by = None
        self.auto_play = False
        self.volume_locked = False
        
        # Advanced features
        self._custom_filters = {}
        self.equalizer = None
        self.skip_votes = set()
        self.required_skips = 1
        
        # Statistics
        self.tracks_played = 0
        self.total_playtime = 0
        self.session_start = datetime.now(timezone.utc)

class Music(commands.Cog):
    """Advanced music system with queue management, filters, and more"""
    
    def __init__(self, bot):
        self.bot = bot
        self.players: Dict[int, MusicPlayer] = {}
    
    def get_player(self, guild: discord.Guild) -> Optional[MusicPlayer]:
        """Get the music player for a guild"""
        return guild.voice_client if isinstance(guild.voice_client, MusicPlayer) else None
    
    async def connect_player(self, channel: discord.VoiceChannel) -> MusicPlayer:
        """Connect to a voice channel and return the player"""
        try:
            # Disconnect existing connection if any
            if channel.guild.voice_client:
                await channel.guild.voice_client.disconnect(force=True)
            
            # Connect with timeout and retry, passing database
            player = await channel.connect(
                cls=MusicPlayer, 
                timeout=30.0, 
                reconnect=True,
                db=self.bot.db
            )
            self.players[channel.guild.id] = player
            
            # Wait a moment for the connection to stabilize
            await asyncio.sleep(1)
            
            logger.info(f"Successfully connected to voice channel: {channel.name} in {channel.guild.name}")
            return player
        except Exception as e:
            logger.error(f"Failed to connect to voice channel {channel.name}: {e}")
            raise
    
    async def _search_youtube_direct(self, query: str) -> Optional[str]:
        """Search YouTube directly using yt-dlp and return stream URL"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestaudio/best',
                'noplaylist': True,
                'extract_flat': False,
            }
            
            # Add cookies if available
            import os
            cookies_paths = [
                'cookies.txt',
                '/rat-bot/cookies.txt',
                os.path.expanduser('~/cookies.txt'),
                'data/cookies.txt'
            ]
            
            for cookies_path in cookies_paths:
                if os.path.exists(cookies_path):
                    ydl_opts['cookiefile'] = cookies_path
                    logger.info(f"Using cookies from: {cookies_path}")
                    break
            else:
                logger.warning("No cookies file found. YouTube access may be limited.")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Search for the query
                search_query = f"ytsearch1:{query}"
                info = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: ydl.extract_info(search_query, download=False)
                )
                
                if info and 'entries' in info and info['entries']:
                    entry = info['entries'][0]
                    return {
                        'url': entry['url'],
                        'title': entry['title'],
                        'duration': entry.get('duration', 0),
                        'webpage_url': entry['webpage_url']
                    }
                    
        except Exception as e:
            logger.error(f"YouTube direct search failed: {e}")
            return None
    
    async def _handle_youtube_fallback(self, ctx, original_title: str, player: MusicPlayer):
        """Handle YouTube playback failure by searching alternative sources"""
        logger.info(f"Searching for alternatives to YouTube track: {original_title}")
        
        # First try direct YouTube with yt-dlp
        try:
            logger.info("Attempting direct YouTube search with yt-dlp...")
            youtube_info = await self._search_youtube_direct(original_title)
            if youtube_info:
                # Create a direct HTTP track
                tracks = await wavelink.Playable.search(youtube_info['url'])
                if tracks:
                    track = tracks[0]
                    await player.play(track)
                    
                    embed = discord.Embed(
                        title="🎵 Now Playing (Direct YouTube)",
                        description=f"**[{youtube_info['title']}]({youtube_info['webpage_url']})**\n"
                                   f"*Using direct YouTube stream*",
                        color=0x00ff00
                    )
                    embed.add_field(name="Duration", value=self._format_time(youtube_info['duration']), inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    embed.add_field(name="Source", value="YouTube (Direct)", inline=True)
                    
                    await ctx.send(embed=embed)
                    return
        except Exception as e:
            logger.warning(f"Direct YouTube fallback failed: {e}")
        
        # Try alternative sources for the same track
        fallback_sources = [
            ("SoundCloud", f"scsearch:{original_title}"),
            ("Bandcamp", f"bcsearch:{original_title}")
        ]
        
        for source_name, search_query in fallback_sources:
            try:
                tracks = await wavelink.Playable.search(search_query)
                if tracks:
                    fallback_track = tracks[0]
                    logger.info(f"Found fallback track on {source_name}: {fallback_track.title}")
                    
                    try:
                        await player.play(fallback_track)
                        
                        embed = discord.Embed(
                            title="🎵 Now Playing (Fallback)",
                            description=f"**[{fallback_track.title}]({fallback_track.uri})**\n"
                                       f"*YouTube version failed, playing from {source_name}*",
                            color=0xffa500  # Orange for fallback
                        )
                        embed.add_field(name="Duration", value=self._format_time(fallback_track.length), inline=True)
                        embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                        embed.add_field(name="Source", value=fallback_track.source, inline=True)
                        
                        await ctx.send(embed=embed)
                        return
                        
                    except Exception as e:
                        logger.warning(f"Fallback track from {source_name} also failed: {e}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Fallback search failed on {source_name}: {e}")
                continue
        
        # If all fallbacks failed
        embed = discord.Embed(
            title="❌ Playback Failed",
            description=f"**{original_title}** failed to play from YouTube and no alternatives were found.",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.group(name="music", aliases=["m"], invoke_without_command=True)
    async def music(self, ctx):
        """Music command group"""
        await ctx.send_help(ctx.command)
    
    @commands.command(name="debug")
    async def debug_voice(self, ctx):
        """Debug voice connection and permissions"""
        embed = discord.Embed(title="🔧 Voice Debug Info", color=0x00ff00)
        
        # Check bot permissions
        permissions = ctx.channel.permissions_for(ctx.guild.me)
        embed.add_field(
            name="Bot Permissions",
            value=f"Connect: {permissions.connect}\n"
                  f"Speak: {permissions.speak}\n"
                  f"Use Voice Activity: {permissions.use_voice_activation}",
            inline=True
        )
        
        # Check voice client status
        if ctx.voice_client:
            player = ctx.voice_client
            embed.add_field(
                name="Voice Client",
                value=f"Channel: {player.channel.name if player.channel else 'None'}\n"
                      f"Playing: {player.playing}\n"
                      f"Paused: {player.paused}\n"
                      f"Current: {player.current.title if player.current else 'None'}",
                inline=True
            )
        else:
            embed.add_field(name="Voice Client", value="Not connected", inline=True)
        
        # Check Lavalink connection
        nodes = wavelink.Pool.nodes
        if nodes:
            node = list(nodes.values())[0]
            embed.add_field(
                name="Lavalink",
                value=f"Node ID: {node.identifier}\n"
                      f"Players: {len(node.players)}",
                inline=True
            )
        else:
            embed.add_field(name="Lavalink", value="No nodes", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="status")
    async def player_status(self, ctx):
        """Check current player status"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ No player found")
        
        embed = discord.Embed(title="🎵 Player Status", color=0x00ff00)
        embed.add_field(name="Playing", value=player.playing, inline=True)
        embed.add_field(name="Paused", value=player.paused, inline=True)
        embed.add_field(name="Volume", value=f"{player.volume}%", inline=True)
        
        if player.current:
            embed.add_field(name="Current Track", value=player.current.title, inline=False)
            embed.add_field(name="Source", value=player.current.source, inline=True)
            embed.add_field(name="Position", value=f"{self._format_time(player.position)}/{self._format_time(player.current.length)}", inline=True)
        
        embed.add_field(name="Queue", value=f"{player.queue.count} tracks", inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="voicetest")
    async def voice_test(self, ctx):
        """Test voice connection and play a short test tone"""
        if not ctx.author.voice:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        # Connect if not connected
        if not ctx.voice_client:
            try:
                await self.connect_player(ctx.author.voice.channel)
            except Exception as e:
                return await ctx.send(f"❌ Failed to connect: {e}")
        
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ No player found")
        
        # Try to play a test track (silence/test tone)
        try:
            # Search for a very short test track
            tracks = await wavelink.Playable.search("scsearch:test tone 1 second")
            if not tracks:
                tracks = await wavelink.Playable.search("ytsearch:1 second test tone")
            
            if tracks:
                test_track = tracks[0]
                await player.play(test_track)
                
                embed = discord.Embed(
                    title="🔊 Voice Test",
                    description=f"Playing test track: **{test_track.title}**\n"
                               f"Voice Channel: **{ctx.voice_client.channel.name}**\n"
                               f"If you can hear this, voice connection is working!",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Could not find test track")
                
        except Exception as e:
            logger.error(f"Voice test failed: {e}")
            await ctx.send(f"❌ Voice test failed: {e}")

    @commands.command(name="testurl")
    async def test_url(self, ctx, url: str = None):
        """Test playing a direct URL (for debugging)"""
        if not url:
            url = "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav"  # Short test sound
        
        if not ctx.author.voice:
            return await ctx.send("❌ You need to be in a voice channel!")
        
        if not ctx.voice_client:
            try:
                await self.connect_player(ctx.author.voice.channel)
            except Exception as e:
                return await ctx.send(f"❌ Failed to connect: {e}")
        
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ No player found")
        
        try:
            tracks = await wavelink.Playable.search(url)
            if tracks:
                await player.play(tracks[0])
                await ctx.send(f"🔊 Testing direct URL: {url}")
            else:
                await ctx.send("❌ Could not load URL")
        except Exception as e:
            await ctx.send(f"❌ URL test failed: {e}")

    @commands.command(name="join", aliases=["connect"])
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Join a voice channel"""
        if not channel:
            if not ctx.author.voice:
                embed = discord.Embed(
                    title="❌ No Voice Channel",
                    description="You need to be in a voice channel or specify one!",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            channel = ctx.author.voice.channel
        
        if ctx.voice_client:
            if ctx.voice_client.channel == channel:
                embed = discord.Embed(
                    title="ℹ️ Already Connected",
                    description=f"Already connected to {channel.mention}",
                    color=0x00aaff
                )
                return await ctx.send(embed=embed)
            
            await ctx.voice_client.move_to(channel)
        else:
            await self.connect_player(channel)
        
        embed = discord.Embed(
            title="✅ Connected",
            description=f"Joined {channel.mention}",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx, *, query: str):
        """Play a song or add it to the queue"""
        if not ctx.voice_client:
            if not ctx.author.voice:
                embed = discord.Embed(
                    title="❌ Not Connected",
                    description="You need to be in a voice channel!",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            
            # Connect to voice channel with better error handling
            try:
                await self.connect_player(ctx.author.voice.channel)
                embed = discord.Embed(
                    title="🔗 Connected",
                    description=f"Joined **{ctx.author.voice.channel.name}**",
                    color=0x00ff00
                )
                await ctx.send(embed=embed)
            except Exception as e:
                embed = discord.Embed(
                    title="❌ Connection Failed",
                    description=f"Failed to connect to voice channel: {str(e)}",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
        
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Failed to get player")
        
        # Check if player is locked
        if player.is_locked and ctx.author.id != player.locked_by:
            embed = discord.Embed(
                title="🔒 Player Locked",
                description="The music player is currently locked.",
                color=0xff0000
            )
            return await ctx.send(embed=embed)
        
        # Search for tracks using multiple sources with bypass
        try:
            tracks = None
            # Check if user wants direct YouTube search
            if query.lower().startswith('yt:') or query.lower().startswith('youtube:'):
                youtube_query = query.split(':', 1)[1].strip()
                logger.info(f"Direct YouTube search requested: {youtube_query}")
                
                youtube_info = await self._search_youtube_direct(youtube_query)
                if youtube_info:
                    tracks = await wavelink.Playable.search(youtube_info['url'])
                    if tracks:
                        logger.info(f"Found direct YouTube track: {youtube_info['title']}")
                        # Mark as YouTube source for tracking
                        tracks[0]._youtube_direct = True
                        tracks[0]._youtube_info = youtube_info
            
            # If not direct YouTube or direct YouTube failed, try other sources
            if not tracks:
                # Prioritize reliable sources first
                search_sources = [
                    ("SoundCloud", f"scsearch:{query}"),
                    ("Bandcamp", f"bcsearch:{query}"),
                    ("HTTP", query if query.startswith(('http://', 'https://')) else None)
                ]
                
                # Try each source until we find results
                for source_name, search_query in search_sources:
                    if search_query is None:  # Skip HTTP if not a URL
                        continue
                    try:
                        tracks = await wavelink.Playable.search(search_query)
                        if tracks:
                            logger.info(f"Found tracks using {source_name}: {len(tracks)} results")
                            break
                    except Exception as e:
                        logger.warning(f"Search failed on {source_name}: {e}")
                        continue
            
            if not tracks:
                embed = discord.Embed(
                    title="❌ No Results",
                    description="No tracks found for your query on any available source.\n"
                               "💡 Try using `yt:` prefix for direct YouTube search (e.g., `!play yt:song name`)",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Search error: {e}")
            return await ctx.send("❌ Search failed. Please try again.")
        
        # Handle playlists
        if isinstance(tracks, wavelink.Playlist):
            await self._handle_playlist(ctx, player, tracks)
        else:
            await self._handle_single_track(ctx, player, tracks[0])
        
        # Update user stats
        if self.bot.db:
            await self.bot.db.increment_user_stat(ctx.author.id, 'songs_played')
    
    async def _handle_single_track(self, ctx, player: MusicPlayer, track: wavelink.Playable):
        """Handle adding a single track"""
        # Add requester info
        track.requester = ctx.author
        track.requested_at = datetime.now(timezone.utc)
        
        logger.info(f"Handling single track: {track.title} (URI: {track.uri[:50]}...)")
        logger.info(f"Player currently playing: {player.playing}")
        logger.info(f"Current queue size: {player.queue.count}")
        
        if player.playing:
            # Add to queue
            await player.queue.put_wait(track)
            logger.info(f"Added track to queue: {track.title} (Position: {player.queue.count})")
            
            embed = discord.Embed(
                title="📝 Added to Queue",
                description=f"**[{track.title}]({track.uri})**",
                color=0x00ff00
            )
            embed.add_field(name="Duration", value=self._format_time(track.length), inline=True)
            embed.add_field(name="Position", value=f"{player.queue.count}", inline=True)
            embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
            
            if hasattr(track, 'thumbnail'):
                embed.set_thumbnail(url=track.thumbnail)
            
            await ctx.send(embed=embed)
        else:
            # Play immediately
            try:
                # Verify voice connection before playing
                if not ctx.voice_client or not hasattr(ctx.voice_client, 'channel'):
                    raise Exception("Voice connection lost")
                
                # Set volume to ensure audio is audible
                await player.set_volume(100)
                
                # Play the track with YouTube fallback handling
                try:
                    await player.play(track)
                    logger.info(f"Started playing track: {track.title} from {track.source}")
                    logger.info(f"Voice channel: {ctx.voice_client.channel.name}")
                    logger.info(f"Player state - Playing: {player.playing}, Paused: {player.paused}")
                    
                    # Check if it's a YouTube track and if it actually started playing
                    if track.source == "youtube":
                        await asyncio.sleep(2)  # Give it a moment to start
                        if not player.playing and not player.paused:
                            logger.warning("YouTube track failed to play, attempting fallback...")
                            await self._handle_youtube_fallback(ctx, track.title, player)
                            return
                            
                except Exception as e:
                    if track.source == "youtube":
                        logger.warning(f"YouTube track failed: {e}, attempting fallback...")
                        await self._handle_youtube_fallback(ctx, track.title, player)
                        return
                    else:
                        raise e
                
                # Check if this is a direct YouTube track
                if hasattr(track, '_youtube_direct') and track._youtube_direct:
                    youtube_info = track._youtube_info
                    embed = discord.Embed(
                        title="🎵 Now Playing (Direct YouTube)",
                        description=f"**[{youtube_info['title']}]({youtube_info['webpage_url']})**",
                        color=0x00ff00
                    )
                    embed.add_field(name="Duration", value=self._format_time(youtube_info['duration']), inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    embed.add_field(name="Source", value="YouTube (Direct)", inline=True)
                else:
                    embed = discord.Embed(
                        title="🎵 Now Playing",
                        description=f"**[{track.title}]({track.uri})**",
                        color=0x00ff00
                    )
                    embed.add_field(name="Duration", value=self._format_time(track.length), inline=True)
                    embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
                    embed.add_field(name="Source", value=track.source, inline=True)
                
                embed.add_field(name="Voice Channel", value=ctx.voice_client.channel.name, inline=True)
                
                # Add a note about potential audio issues
                embed.set_footer(text="💡 If you can't hear audio, check your Discord voice settings and ensure the bot has proper permissions.")
                
            except Exception as e:
                logger.error(f"Failed to play track {track.title}: {e}")
                embed = discord.Embed(
                    title="❌ Playback Error",
                    description=f"Failed to play **{track.title}**\nError: {str(e)}",
                    color=0xff0000
                )
                return await ctx.send(embed=embed)
            
            if hasattr(track, 'thumbnail'):
                embed.set_thumbnail(url=track.thumbnail)
            
            await ctx.send(embed=embed)
    
    async def _handle_playlist(self, ctx, player: MusicPlayer, playlist: wavelink.Playlist):
        """Handle adding a playlist"""
        if not playlist.tracks:
            return await ctx.send("❌ Playlist is empty")
        
        # Add all tracks to queue
        added = 0
        for track in playlist.tracks:
            track.requester = ctx.author
            track.requested_at = datetime.now(timezone.utc)
            
            if not player.playing and added == 0:
                await player.play(track)
            else:
                await player.queue.put_wait(track)
            added += 1
        
        embed = discord.Embed(
            title="📝 Playlist Added",
            description=f"**{playlist.name}**",
            color=0x00ff00
        )
        embed.add_field(name="Tracks Added", value=str(added), inline=True)
        embed.add_field(name="Total Duration", value=self._format_time(sum(t.length for t in playlist.tracks)), inline=True)
        embed.add_field(name="Requested by", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="skip", aliases=["s"])
    async def skip(self, ctx):
        """Skip the current track"""
        player = self.get_player(ctx.guild)
        if not player or not player.playing:
            return await ctx.send("❌ Nothing is playing")
        
        # Check permissions for skip
        if await self._can_skip(ctx, player):
            logger.info(f"Skipping track: {player.current.title if player.current else 'Unknown'}")
            logger.info(f"Queue size before skip: {player.queue.count}")
            await player.skip()
            embed = discord.Embed(
                title="⏭️ Skipped",
                description="Skipped the current track",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        else:
            # Vote skip system
            await self._vote_skip(ctx, player)
    
    async def _can_skip(self, ctx, player: MusicPlayer) -> bool:
        """Check if user can skip without voting"""
        # DJ permissions, track requester, or alone in voice
        if (ctx.author.guild_permissions.manage_channels or 
            (hasattr(player.current, 'requester') and player.current.requester == ctx.author) or
            len([m for m in ctx.voice_client.channel.members if not m.bot]) <= 1):
            return True
        return False
    
    async def _vote_skip(self, ctx, player: MusicPlayer):
        """Handle vote skip system"""
        if ctx.author.id in player.skip_votes:
            return await ctx.send("❌ You've already voted to skip")
        
        player.skip_votes.add(ctx.author.id)
        
        # Calculate required votes (50% of non-bot members)
        voice_members = [m for m in ctx.voice_client.channel.members if not m.bot]
        player.required_skips = max(1, math.ceil(len(voice_members) * 0.5))
        
        if len(player.skip_votes) >= player.required_skips:
            await player.skip()
            player.skip_votes.clear()
            embed = discord.Embed(
                title="⏭️ Vote Skip Successful",
                description="Skipped the current track",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="🗳️ Vote Registered",
                description=f"Skip votes: {len(player.skip_votes)}/{player.required_skips}",
                color=0xffaa00
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="queue", aliases=["q"])
    async def queue(self, ctx, page: int = 1):
        """Show the music queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        # Check if queue is empty
        queue_is_empty = await player.queue.is_empty if hasattr(player.queue, 'is_empty') and asyncio.iscoroutinefunction(getattr(player.queue, 'is_empty', None)) else player.queue.is_empty
        
        if queue_is_empty and not player.playing:
            return await ctx.send("📭 Queue is empty")
        
        # Get queue size for pagination
        queue_size = await player.queue.count if hasattr(player.queue, 'count') and asyncio.iscoroutinefunction(getattr(player.queue, 'count', None)) else player.queue.count
        
        # Paginate queue
        per_page = 10
        total_pages = max(1, math.ceil(queue_size / per_page))
        page = max(1, min(page, total_pages))
        
        start = (page - 1) * per_page
        end = start + per_page
        
        embed = discord.Embed(
            title="🎵 Music Queue",
            color=0x00aaff
        )
        
        # Current track
        if player.playing:
            current = player.current
            progress = self._get_progress_bar(player.position, current.length)
            embed.add_field(
                name="🎵 Now Playing",
                value=f"**[{current.title}]({current.uri})**\n{progress}",
                inline=False
            )
        
        # Queue tracks
        if not queue_is_empty:
            queue_list = []
            
            # Get queue preview for display
            if hasattr(player.queue, 'get_preview'):
                queue_preview = await player.queue.get_preview(per_page)
                for i, track_data in enumerate(queue_preview[start:end], start + 1):
                    duration = self._format_time(track_data.get('length', 0))
                    requester_name = track_data.get('requester_name', 'Unknown')
                    queue_list.append(f"`{i}.` **[{track_data['title']}]({track_data['uri']})** `{duration}` - {requester_name}")
            else:
                # Fallback for wavelink queue
                for i, track in enumerate(list(player.queue)[start:end], start + 1):
                    duration = self._format_time(track.length)
                    requester = getattr(track, 'requester', 'Unknown')
                    queue_list.append(f"`{i}.` **[{track.title}]({track.uri})** `{duration}` - {requester.mention if hasattr(requester, 'mention') else requester}")
            
            embed.add_field(
                name=f"📝 Queue ({queue_size} tracks)",
                value="\n".join(queue_list) if queue_list else "No tracks in queue",
                inline=False
            )
        
        # Queue info
        if not queue_is_empty:
            if hasattr(player.queue, 'get_preview'):
                # For database queue, calculate duration from preview
                queue_preview = await player.queue.get_preview(100)  # Get more tracks for duration calculation
                total_duration = sum(track_data.get('length', 0) for track_data in queue_preview)
            else:
                # For wavelink queue
                total_duration = sum(track.length for track in player.queue)
            embed.add_field(name="Total Duration", value=self._format_time(total_duration), inline=True)
        
        embed.add_field(name="Loop Mode", value=player.loop_mode.title(), inline=True)
        embed.set_footer(text=f"Page {page}/{total_pages}")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="nowplaying", aliases=["np"])
    async def nowplaying(self, ctx):
        """Show currently playing track"""
        player = self.get_player(ctx.guild)
        if not player or not player.playing:
            return await ctx.send("❌ Nothing is playing")
        
        track = player.current
        progress = self._get_progress_bar(player.position, track.length)
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**[{track.title}]({track.uri})**",
            color=0x00ff00
        )
        
        embed.add_field(name="Duration", value=self._format_time(track.length), inline=True)
        embed.add_field(name="Position", value=self._format_time(player.position), inline=True)
        embed.add_field(name="Volume", value=f"{player.volume}%", inline=True)
        
        if hasattr(track, 'requester'):
            embed.add_field(name="Requested by", value=track.requester.mention, inline=True)
        
        embed.add_field(name="Loop Mode", value=player.loop_mode.title(), inline=True)
        embed.add_field(name="Auto Play", value="✅" if player.auto_play else "❌", inline=True)
        
        embed.add_field(name="Progress", value=progress, inline=False)
        
        if hasattr(track, 'thumbnail'):
            embed.set_thumbnail(url=track.thumbnail)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="queuedebug", aliases=["qd"])
    async def queue_debug(self, ctx):
        """Debug queue information (admin only)"""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.send("❌ This command is for bot owners only")
            
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to a voice channel")
        
        embed = discord.Embed(
            title="🔧 Queue Debug Info",
            color=0xff9900
        )
        
        queue_size = await player.queue.count if hasattr(player.queue, 'count') and asyncio.iscoroutinefunction(getattr(player.queue, 'count', None)) else player.queue.count
        queue_is_empty = await player.queue.is_empty if hasattr(player.queue, 'is_empty') and asyncio.iscoroutinefunction(getattr(player.queue, 'is_empty', None)) else player.queue.is_empty
        
        embed.add_field(name="Queue Size", value=f"{queue_size}", inline=True)
        embed.add_field(name="Queue Empty", value=f"{queue_is_empty}", inline=True)
        embed.add_field(name="Queue Type", value=f"{type(player.queue).__name__}", inline=True)
        embed.add_field(name="Playing", value=f"{player.playing}", inline=True)
        embed.add_field(name="Paused", value=f"{player.paused}", inline=True)
        embed.add_field(name="Loop Mode", value=f"{player.loop_mode}", inline=True)
        embed.add_field(name="Auto Play", value=f"{player.auto_play}", inline=True)
        embed.add_field(name="History Count", value=f"{len(player.history)}", inline=True)
        embed.add_field(name="Tracks Played", value=f"{player.tracks_played}", inline=True)
        embed.add_field(name="Connected", value=f"{player.connected}", inline=True)
        
        if player.current:
            embed.add_field(
                name="Current Track",
                value=f"**{player.current.title}**\n"
                      f"Source: {player.current.source}\n"
                      f"Position: {self._format_time(player.position)}/{self._format_time(player.current.length)}",
                inline=False
            )
        
        if not queue_is_empty:
            next_tracks = []
            
            if hasattr(player.queue, 'get_preview'):
                # For database queue
                queue_preview = await player.queue.get_preview(3)
                for i, track_data in enumerate(queue_preview):
                    next_tracks.append(f"{i+1}. {track_data['title']} ({track_data['source']})")
            else:
                # For wavelink queue
                for i, track in enumerate(player.queue):
                    if i >= 3:  # Show next 3 tracks
                        break
                    next_tracks.append(f"{i+1}. {track.title} ({track.source})")
            
            if next_tracks:
                embed.add_field(
                    name="Next Tracks",
                    value="\n".join(next_tracks),
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="queuelist", aliases=["ql"])
    async def queue_list(self, ctx):
        """List all tracks in queue with detailed info (admin only)"""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.send("❌ This command is for bot owners only")
            
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to a voice channel")
        
        embed = discord.Embed(
            title="📋 Detailed Queue List",
            color=0x00aaff
        )
        
        if player.current:
            embed.add_field(
                name="🎵 Currently Playing",
                value=f"**{player.current.title}**\n"
                      f"Source: {player.current.source}\n"
                      f"URI: {player.current.uri[:50]}...",
                inline=False
            )
        
        if player.queue.is_empty:
            embed.add_field(name="Queue", value="Empty", inline=False)
        else:
            queue_items = []
            for i, track in enumerate(player.queue):
                queue_items.append(
                    f"**{i+1}.** {track.title}\n"
                    f"   Source: {track.source}\n"
                    f"   URI: {track.uri[:50]}...\n"
                )
                if i >= 4:  # Show first 5 tracks
                    queue_items.append(f"... and {len(player.queue) - 5} more tracks")
                    break
            
            embed.add_field(
                name=f"Queue ({player.queue.count} tracks)",
                value="\n".join(queue_items),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="testqueue")
    async def test_queue(self, ctx):
        """Test queue with duplicate songs (admin only)"""
        if not await self.bot.is_owner(ctx.author):
            return await ctx.send("❌ This command is for bot owners only")
        
        player = await self.connect_player(ctx)
        if not player:
            return
        
        # Add the same song 3 times
        test_query = "test song"
        
        for i in range(3):
            try:
                tracks = await wavelink.Playable.search(f"scsearch:{test_query}")
                if tracks:
                    track = tracks[0]
                    track.requester = ctx.author
                    track.requested_at = datetime.now(timezone.utc)
                    
                    if not player.playing:
                        await player.play(track)
                        await ctx.send(f"🎵 Playing: {track.title}")
                    else:
                        await player.queue.put_wait(track)
                        await ctx.send(f"📝 Queued #{player.queue.count}: {track.title}")
                    
                    logger.info(f"Test queue - Added track {i+1}: {track.title} (URI: {track.uri})")
                else:
                    await ctx.send(f"❌ No results for test query {i+1}")
            except Exception as e:
                await ctx.send(f"❌ Error adding track {i+1}: {e}")
                logger.error(f"Test queue error {i+1}: {e}")
        
        await ctx.send(f"✅ Test complete. Queue size: {player.queue.count}")
    
    @commands.command(name="pause")
    async def pause(self, ctx):
        """Pause the current track"""
        player = self.get_player(ctx.guild)
        if not player or not player.playing:
            return await ctx.send("❌ Nothing is playing")
        
        if player.paused:
            return await ctx.send("⏸️ Already paused")
        
        await player.pause(True)
        embed = discord.Embed(
            title="⏸️ Paused",
            description="Music has been paused",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="resume")
    async def resume(self, ctx):
        """Resume the current track"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        if not player.paused:
            return await ctx.send("▶️ Not paused")
        
        await player.pause(False)
        embed = discord.Embed(
            title="▶️ Resumed",
            description="Music has been resumed",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="stop")
    async def stop(self, ctx):
        """Stop the music and clear the queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        player.queue.clear()
        await player.stop()
        
        embed = discord.Embed(
            title="⏹️ Stopped",
            description="Music stopped and queue cleared",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="volume", aliases=["vol"])
    async def volume(self, ctx, volume: int = None):
        """Set or show the volume"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        if volume is None:
            embed = discord.Embed(
                title="🔊 Current Volume",
                description=f"Volume is set to **{player.volume}%**",
                color=0x00aaff
            )
            return await ctx.send(embed=embed)
        
        if player.volume_locked and not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("🔒 Volume is locked")
        
        if not 0 <= volume <= 100:
            return await ctx.send("❌ Volume must be between 0 and 100")
        
        await player.set_volume(volume)
        
        embed = discord.Embed(
            title="🔊 Volume Changed",
            description=f"Volume set to **{volume}%**",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="loop")
    async def loop(self, ctx, mode: str = None):
        """Set loop mode (none, track, queue)"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        if mode is None:
            embed = discord.Embed(
                title="🔄 Current Loop Mode",
                description=f"Loop mode: **{player.loop_mode.title()}**",
                color=0x00aaff
            )
            return await ctx.send(embed=embed)
        
        mode = mode.lower()
        if mode not in ["none", "track", "queue"]:
            return await ctx.send("❌ Invalid loop mode. Use: none, track, or queue")
        
        player.loop_mode = mode
        
        embed = discord.Embed(
            title="🔄 Loop Mode Changed",
            description=f"Loop mode set to **{mode.title()}**",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="shuffle")
    async def shuffle(self, ctx):
        """Shuffle the queue"""
        player = self.get_player(ctx.guild)
        if not player or player.queue.is_empty:
            return await ctx.send("❌ Queue is empty")
        
        player.queue.shuffle()
        
        embed = discord.Embed(
            title="🔀 Queue Shuffled",
            description="The queue has been shuffled",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="remove")
    async def remove(self, ctx, index: int):
        """Remove a track from the queue"""
        player = self.get_player(ctx.guild)
        if not player or player.queue.is_empty:
            return await ctx.send("❌ Queue is empty")
        
        if not 1 <= index <= player.queue.count:
            return await ctx.send(f"❌ Invalid index. Use 1-{player.queue.count}")
        
        # Convert to 0-based index
        track = player.queue[index - 1]
        del player.queue[index - 1]
        
        embed = discord.Embed(
            title="🗑️ Track Removed",
            description=f"Removed **{track.title}** from the queue",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="clear")
    async def clear(self, ctx):
        """Clear the queue"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        # Check if queue is empty
        queue_is_empty = await player.queue.is_empty if hasattr(player.queue, 'is_empty') and asyncio.iscoroutinefunction(getattr(player.queue, 'is_empty', None)) else player.queue.is_empty
        
        if queue_is_empty:
            return await ctx.send("❌ Queue is empty")
        
        # Get count before clearing
        queue_size = await player.queue.count if hasattr(player.queue, 'count') and asyncio.iscoroutinefunction(getattr(player.queue, 'count', None)) else player.queue.count
        
        # Clear the queue
        if hasattr(player.queue, 'clear') and asyncio.iscoroutinefunction(player.queue.clear):
            cleared = await player.queue.clear()
        else:
            cleared = queue_size
            player.queue.clear()
        
        embed = discord.Embed(
            title="🗑️ Queue Cleared",
            description=f"Cleared {cleared} tracks from the queue",
            color=0xff0000
        )
        await ctx.send(embed=embed)
    
    @commands.command(name="disconnect", aliases=["leave", "dc"])
    async def disconnect(self, ctx):
        """Disconnect from voice channel"""
        player = self.get_player(ctx.guild)
        if not player:
            return await ctx.send("❌ Not connected to voice")
        
        # Save queue to database
        if self.bot.db and not player.queue.is_empty:
            queue_data = []
            for track in player.queue:
                queue_data.append({
                    'title': track.title,
                    'uri': track.uri,
                    'length': track.length,
                    'requester_id': getattr(track.requester, 'id', None) if hasattr(track, 'requester') else None
                })
            await self.bot.db.save_music_queue(ctx.guild.id, queue_data)
        
        await player.disconnect()
        if ctx.guild.id in self.players:
            del self.players[ctx.guild.id]
        
        embed = discord.Embed(
            title="👋 Disconnected",
            description="Left the voice channel",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    def _format_time(self, ms: int) -> str:
        """Format milliseconds to readable time"""
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        
        if hours > 0:
            return f"{hours}:{minutes%60:02d}:{seconds%60:02d}"
        else:
            return f"{minutes}:{seconds%60:02d}"
    
    def _get_progress_bar(self, position: int, duration: int, length: int = 20) -> str:
        """Generate a progress bar"""
        if duration == 0:
            return "`[Live Stream]`"
        
        progress = position / duration
        filled = int(progress * length)
        bar = "█" * filled + "░" * (length - filled)
        
        pos_str = self._format_time(position)
        dur_str = self._format_time(duration)
        
        return f"`{pos_str}` {bar} `{dur_str}`"
    
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """Handle track end events"""
        player = payload.player
        
        if not player:
            return
        
        logger.info(f"Track ended: {payload.track.title if payload.track else 'Unknown'}")
        logger.info(f"Queue size: {player.queue.count}")
        logger.info(f"Loop mode: {player.loop_mode}")
        
        # Update statistics
        player.tracks_played += 1
        if hasattr(payload.track, 'length'):
            player.total_playtime += payload.track.length
        
        # Add to history
        if len(player.history) >= 50:  # Keep last 50 tracks
            player.history.pop(0)
        player.history.append(payload.track)
        
        # Handle loop modes
        if player.loop_mode == "track" and payload.track:
            logger.info("Looping current track")
            return await player.play(payload.track)
        
        # Clear skip votes
        player.skip_votes.clear()
        
        # Play next track
        queue_is_empty = await player.queue.is_empty if hasattr(player.queue, 'is_empty') and asyncio.iscoroutinefunction(getattr(player.queue, 'is_empty', None)) else player.queue.is_empty
        
        if not queue_is_empty:
            try:
                queue_size = await player.queue.count if hasattr(player.queue, 'count') and asyncio.iscoroutinefunction(getattr(player.queue, 'count', None)) else player.queue.count
                logger.info(f"Queue before getting next track: {queue_size} tracks")
                
                next_track = await player.queue.get_wait()
                logger.info(f"Got next track from queue: {next_track.title} (Source: {next_track.source})")
                
                queue_size_after = await player.queue.count if hasattr(player.queue, 'count') and asyncio.iscoroutinefunction(getattr(player.queue, 'count', None)) else player.queue.count
                logger.info(f"Queue after getting next track: {queue_size_after} tracks")
                
                # Handle YouTube fallback for queued tracks
                if next_track.source == "youtube":
                    try:
                        await player.play(next_track)
                        # Check if it actually started playing
                        await asyncio.sleep(2)
                        if not player.playing and not player.paused:
                            logger.warning("Queued YouTube track failed, attempting fallback...")
                            # Find the channel for fallback
                            channel = player.channel
                            if channel and hasattr(channel, 'guild'):
                                # Create a mock context for fallback
                                class MockContext:
                                    def __init__(self, channel, author):
                                        self.channel = channel
                                        self.author = author
                                        self.send = channel.send
                                
                                mock_ctx = MockContext(channel, next_track.requester if hasattr(next_track, 'requester') else None)
                                await self._handle_youtube_fallback(mock_ctx, next_track.title, player)
                                return
                    except Exception as e:
                        logger.warning(f"Queued YouTube track failed: {e}, attempting fallback...")
                        channel = player.channel
                        if channel and hasattr(channel, 'guild'):
                            class MockContext:
                                def __init__(self, channel, author):
                                    self.channel = channel
                                    self.author = author
                                    self.send = channel.send
                            
                            mock_ctx = MockContext(channel, next_track.requester if hasattr(next_track, 'requester') else None)
                            await self._handle_youtube_fallback(mock_ctx, next_track.title, player)
                            return
                else:
                    await player.play(next_track)
                    
            except Exception as e:
                logger.error(f"Error playing next track: {e}")
                # Try to continue with the next track if available
                if not player.queue.is_empty:
                    try:
                        next_track = await player.queue.get_wait()
                        await player.play(next_track)
                    except Exception as e2:
                        logger.error(f"Failed to play backup track: {e2}")
                        
        elif player.loop_mode == "queue" and player.history:
            logger.info("Restarting queue loop")
            # Restart queue
            for track in reversed(player.history):
                await player.queue.put_wait(track)
            if not player.queue.is_empty:
                next_track = await player.queue.get_wait()
                await player.play(next_track)
        elif player.auto_play and payload.track:
            logger.info("Attempting auto-play")
            # Auto-play similar tracks (if supported)
            try:
                recommended = await wavelink.Playable.search(f"scsearch:{payload.track.title}")
                if not recommended:
                    recommended = await wavelink.Playable.search(f"bcsearch:{payload.track.title}")
                    
                if recommended and len(recommended) > 1:
                    next_track = recommended[1]  # Skip the same track
                    next_track.requester = payload.track.requester if hasattr(payload.track, 'requester') else None
                    await player.play(next_track)
            except Exception as e:
                logger.warning(f"Auto-play failed: {e}")
        else:
            logger.info("No more tracks to play, queue is empty")
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        """Handle track start events"""
        player = payload.player
        track = payload.track
        
        # Update bot statistics
        self.bot.stats['songs_played'] += 1

async def setup(bot):
    await bot.add_cog(Music(bot))