import asyncio
import os
import discord
from discord.ext import commands
from discord import app_commands
from pathlib import Path
import youtube_dl
import ssl
from datetime import timedelta

# Configure youtube-dl options with SSL certificate handling
youtube_dl.utils.bug_reports_message = lambda: ''

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

# Configure youtube-dl with custom SSL context
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

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
    fallback_ytdl = youtube_dl.YoutubeDL(fallback_options)
    return fallback_ytdl.extract_info(url, download=download)

# 20 minutes, in seconds
DURATION_CEILING = 20 * 60
DURATION_CEILING_STRING = '20mins'
SONGS_PER_PAGE = 10

def set_str_len(s: str, length: int):
    '''Adds whitespace or trims string to enforce a specific size'''
    return s.ljust(length)[:length]

class Queue(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_song = None
        self._skip_voters = []

    def next_song(self):
        self._current_song = self.pop(0)
        return self._current_song

    def clear(self):
        super().clear()
        self._current_song = None

    def add_skip_vote(self, voter: discord.Member):
        self._skip_voters.append(voter)

    def clear_skip_votes(self):
        self._skip_voters.clear()

    @property
    def skip_voters(self):
        return self._skip_voters

    @property
    def current_song(self):
        return self._current_song

    def get_embed(self, song_id: int):
        if song_id <= 0:
            song = self.current_song
        else:
            song = self[song_id-1]

        if len(song.description) > 300:
            song['description'] = f'{song.description[:300]}...'

        embed = discord.Embed(title="Audio Info")
        embed.set_thumbnail(url=song.thumbnail)
        embed.add_field(name='Song', value=song.title, inline=True)
        embed.add_field(name='Uploader', value=song.uploader, inline=True)
        embed.add_field(name='Duration', value=song.duration_formatted, inline=True)
        embed.add_field(name='Description', value=song.description, inline=True)
        embed.add_field(name='Upload Date', value=song.upload_date_formatted, inline=True)
        embed.add_field(name='Views', value=song.views, inline=True)
        embed.add_field(name='Likes', value=song.likes, inline=True)
        embed.add_field(name='Dislikes', value=song.dislikes, inline=True)
        embed.add_field(name='Requested By', value=song.requested_by_username, inline=True)

        return embed

class Song(dict):
    def __init__(self, url: str, author: discord.Member):
        super().__init__()
        self.download_info(url, author)

    @property
    def url(self):
        return self.get('url', None)

    @property
    def title(self):
        return self.get('title', 'Unable To Fetch')

    @property
    def uploader(self):
        return self.get('uploader', 'Unable To Fetch')

    @property
    def duration_raw(self):
        return self.get('duration', 0)

    @property
    def duration_formatted(self):
        minutes, seconds = self.duration_raw // 60, self.duration_raw % 60
        return f'{minutes}m, {seconds}s'

    @property
    def description(self):
        return self.get('description', 'Unable To Fetch')

    @property
    def upload_date_raw(self):
        return self.get('upload_date', '01011970')

    @property
    def upload_date_formatted(self):
        m, d, y = self.upload_date_raw[4:6], self.upload_date_raw[6:8], self.upload_date_raw[0:4]
        return f'{m}/{d}/{y}'

    @property
    def views(self):
        return self.get('view_count', 0)

    @property
    def likes(self):
        return self.get('like_count', 0)

    @property
    def dislikes(self):
        return self.get('dislike_count', 0)

    @property
    def thumbnail(self):
        return self.get('thumbnail', 'http://i.imgur.com/dDTCO6e.png')

    @property
    def requested_by_username(self):
        return self.get('requested_by', 'Unknown requester')

    @property
    def requested_by_id(self):
        return self.get('requested_by_id', 1)

    def download_info(self, url: str, author: discord.Member):
        try:
            # Use youtube-dl instead of yt-dlp
            data = extract_info(url, download=False)
            
            if not url.startswith('https'):
                data = extract_info(data['entries'][0]['webpage_url'], download=False)

            self.update(data)
            self['url'] = url
            self['requested_by'] = str(author.name)
            self['requested_by_id'] = author.id
            
        except Exception as e:
            # Fallback to SSL-bypass method
            try:
                data = extract_info_fallback(url, download=False)
                
                if not url.startswith('https'):
                    data = extract_info_fallback(data['entries'][0]['webpage_url'], download=False)

                self.update(data)
                self['url'] = url
                self['requested_by'] = str(author.name)
                self['requested_by_id'] = author.id
                
            except Exception as e2:
                raise Exception(f"Failed to extract video info: {e2}")

class Music(commands.Cog):
    """Music commands for playing audio from various sources."""

    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}
        self.voice_clients = {}

    def get_queue(self, guild):
        """Get or create music queue for guild."""
        if guild not in self.music_queues:
            self.music_queues[guild] = Queue()
        return self.music_queues[guild]

    @commands.hybrid_command(name='join', description="Join a voice channel")
    async def join(self, ctx):
        """Join a voice channel."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        if ctx.guild in self.voice_clients and self.voice_clients[ctx.guild] is not None:
            return await self.voice_clients[ctx.guild].move_to(channel)

        self.voice_clients[ctx.guild] = await channel.connect()
        await ctx.send(f"✅ Joined {channel.name}")

    @commands.hybrid_command(name='play', description="Play a song from YouTube or other sources")
    @app_commands.describe(query="The song to play (URL or search term)")
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube or other sources."""
        if ctx.author.voice is None:
            await ctx.send("❌ You are not connected to a voice channel.")
            return

        music_queue = self.get_queue(ctx.guild)
        voice = self.voice_clients.get(ctx.guild)

        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("❌ You're not connected to a voice channel.")
            return

        if voice is not None and not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send("❌ You're not in my voice channel.")
            return

        if not query.startswith('https://'):
            query = f'ytsearch1:{query}'

        try:
            song = Song(query, ctx.author)
            valid_song, song_err = self.song_error_check(song)

            if not valid_song:
                await ctx.send(f"❌ {song_err}")
                return

            if voice is None or not voice.is_connected():
                self.voice_clients[ctx.guild] = await channel.connect()

            music_queue.append(song)
            await ctx.send(f'✅ Queued song: {song.title}')

            await self.play_all_songs(ctx.guild)

        except Exception as e:
            error_msg = f"❌ An error occurred while processing your song.\n```css\n[{e}]\n```"
            
            # Add troubleshooting information
            if "certificate" in str(e).lower() or "ssl" in str(e).lower():
                error_msg += "\n**SSL Certificate Error Detected!**\n"
                error_msg += "**Solutions:**\n"
                error_msg += "• Update youtube-dl: `pip install --upgrade youtube-dl`\n"
                error_msg += "• Try a different song or URL\n"
                error_msg += "• Check your internet connection\n"
                error_msg += "• The bot has been configured to bypass SSL verification"
            else:
                error_msg += "\n**Troubleshooting:**\n"
                error_msg += "• Try updating youtube-dl: `pip install --upgrade youtube-dl`\n"
                error_msg += "• Check your internet connection\n"
                error_msg += "• Try a different song or URL"
            
            await ctx.send(error_msg)

    @commands.hybrid_command(name='pause', description="Pause the currently playing song")
    async def pause(self, ctx):
        """Pause the currently playing song."""
        voice = self.voice_clients.get(ctx.guild)
        if voice is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if voice.is_playing():
            voice.pause()
            await ctx.send("⏸️ Paused the music.")
        else:
            await ctx.send("❌ I am not playing anything.")

    @commands.hybrid_command(name='resume', description="Resume the currently paused song")
    async def resume(self, ctx):
        """Resume the currently paused song."""
        voice = self.voice_clients.get(ctx.guild)
        if voice is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        if voice.is_paused():
            voice.resume()
            await ctx.send("▶️ Resumed the music.")
        else:
            await ctx.send("❌ I am not paused.")

    @commands.hybrid_command(name='stop', description="Stop playing and clear the queue")
    @commands.has_permissions(ban_members=True)
    async def stop(self, ctx):
        """Stop playing and clear the queue."""
        voice = self.voice_clients.get(ctx.guild)
        queue = self.music_queues.get(ctx.guild)

        if self.client_in_same_channel(ctx.author, ctx.guild):
            if voice:
                voice.stop()
            if queue:
                queue.clear()
            self.voice_clients[ctx.guild] = None
            await ctx.send("⏹️ Stopping playback")
            if voice:
                await voice.disconnect()
        else:
            await ctx.send("❌ You're not in a voice channel with me.")

    @commands.hybrid_command(name='skip', description="Vote to skip the currently playing song")
    async def skip(self, ctx):
        """Vote to skip the currently playing song."""
        voice = self.voice_clients.get(ctx.guild)
        queue = self.music_queues.get(ctx.guild)

        if not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send("❌ You're not in a voice channel with me.")
            return

        if voice is None or not voice.is_playing():
            await ctx.send("❌ I'm not playing a song right now.")
            return

        if ctx.author in queue.skip_voters:
            await ctx.send("❌ You've already voted to skip this song.")
            return

        channel = ctx.author.voice.channel
        required_votes = round(len(channel.members) / 2)

        queue.add_skip_vote(ctx.author)

        if len(queue.skip_voters) >= required_votes:
            await ctx.send('⏭️ Skipping song after successful vote.')
            voice.stop()
        else:
            await ctx.send(f'✅ You voted to skip this song. {required_votes-len(queue.skip_voters)} more votes are required.')

    @commands.hybrid_command(name='fskip', description="Force skip the currently playing song")
    @commands.has_permissions(ban_members=True)
    async def fskip(self, ctx):
        """Force skip the currently playing song."""
        voice = self.voice_clients.get(ctx.guild)

        if not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send("❌ You're not in a voice channel with me.")
        elif voice is None or not voice.is_playing():
            await ctx.send("❌ I'm not playing a song right now.")
        else:
            voice.stop()
            await ctx.send("⏭️ Force skipped the song.")

    @commands.hybrid_command(name='songinfo', description="Show detailed information about a song")
    @app_commands.describe(song_index="Song index in queue (0 for current song)")
    async def songinfo(self, ctx, song_index: int = 0):
        """Show detailed information about a song."""
        queue = self.music_queues.get(ctx.guild)

        if not queue or song_index not in range(len(queue)+1):
            await ctx.send("❌ A song does not exist at that index in the queue.")
            return
        
        embed = queue.get_embed(song_index)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name='remove', description="Remove a song from the queue")
    @app_commands.describe(song_id="Song ID to remove (leave empty for your last song)")
    async def remove(self, ctx, song_id: int = None):
        """Remove a song from the queue."""
        if not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send("❌ You're not in a voice channel with me.")
            return

        queue = self.music_queues.get(ctx.guild)

        if song_id is None:
            for index, song in reversed(list(enumerate(queue))):
                if ctx.author.id == song.requested_by_id:
                    queue.pop(index)
                    await ctx.send(f'✅ Song "{song.title}" removed from queue.')
                    return
            await ctx.send("❌ You haven't requested any songs in the queue.")
        else:
            try:
                song = queue[song_id-1]
            except IndexError:
                await ctx.send('❌ An invalid index was provided.')
                return

            if ctx.author.id == song.requested_by_id:
                queue.pop(song_id-1)
                await ctx.send(f'✅ Song {song.title} removed from queue.')
            else:
                await ctx.send('❌ You cannot remove a song requested by someone else.')

    @commands.hybrid_command(name='fremove', description="Force remove a song from the queue")
    @commands.has_permissions(ban_members=True)
    @app_commands.describe(song_id="Song ID to remove")
    async def fremove(self, ctx, song_id: int):
        """Force remove a song from the queue."""
        queue = self.music_queues.get(ctx.guild)

        if not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send('❌ You\'re not in a voice channel with me.')
            return
        
        if song_id is None or song_id <= 0:
            await ctx.send('❌ You need to specify a song by its queue index.')
            return
        
        try:
            song = queue[song_id-1]
        except IndexError:
            await ctx.send('❌ A song does not exist at this queue index.')
            return
        
        queue.pop(song_id-1)
        await ctx.send(f'✅ Removed {song.title} from the queue.')

    @commands.hybrid_command(name='queue', description="Show the music queue")
    @app_commands.describe(page="Page number to show")
    async def queue(self, ctx, page: int = 1):
        """Show the music queue."""
        queue = self.music_queues.get(ctx.guild)

        if not self.client_in_same_channel(ctx.author, ctx.guild):
            await ctx.send('❌ You\'re not in a voice channel with me.')
            return
        
        if not len(queue):
            await ctx.send('📭 I don\'t have anything in my queue right now.')
            return

        if len(queue) < SONGS_PER_PAGE*(page-1):
            await ctx.send('❌ I don\'t have that many pages in my queue.')
            return

        to_send = f'```\n    {set_str_len("Song", 66)}{set_str_len("Uploader", 36)}Requested By\n'

        for pos, song in enumerate(queue[:SONGS_PER_PAGE*page], start=SONGS_PER_PAGE*(page-1)):
            title = set_str_len(song.title, 65)
            uploader = set_str_len(song.uploader, 35)
            requested_by = song.requested_by_username
            to_send += f'{set_str_len(f"{pos+1})",4)}{title}|{uploader}|{requested_by}\n'

        await ctx.send(to_send + '```')

    @commands.hybrid_command(name='leave', description="Leave the voice channel")
    async def leave(self, ctx):
        """Leave the voice channel."""
        voice = self.voice_clients.get(ctx.guild)
        if voice is None:
            await ctx.send("❌ I am not connected to a voice channel.")
            return

        await voice.disconnect()
        self.voice_clients[ctx.guild] = None
        await ctx.send("👋 Left the voice channel.")

    @commands.hybrid_command(name='fixmusic', description="Update youtube-dl to fix music issues")
    async def fixmusic(self, ctx):
        """Update youtube-dl to fix music issues."""
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ You need administrator permissions to use this command.")
            return

        await ctx.send("🔄 Updating youtube-dl... This may take a moment.")
        
        try:
            import subprocess
            import sys
            
            # Update youtube-dl
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "youtube-dl"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                await ctx.send("✅ youtube-dl updated successfully! Try playing music again.")
            else:
                await ctx.send(f"❌ Failed to update youtube-dl:\n```{result.stderr}```")
                
        except Exception as e:
            await ctx.send(f"❌ Error updating youtube-dl: {e}")

    async def play_all_songs(self, guild: discord.Guild):
        """Play all songs in the queue."""
        queue = self.music_queues.get(guild)

        # Play next song until queue is empty
        while len(queue) > 0:
            await self.wait_for_end_of_song(guild)

            song = queue.next_song()

            await self.play_song(guild, song)

        # Disconnect after song queue is empty
        await self.inactivity_disconnect(guild)

    async def play_song(self, guild: discord.Guild, song: Song):
        """Downloads and starts playing a YouTube video's audio."""
        audio_dir = os.path.join('.', 'audio')
        audio_path = os.path.join(audio_dir, f'{guild.id}.mp3')
        voice = self.voice_clients.get(guild)

        queue = self.music_queues.get(guild)
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': audio_path,
            'nocheckcertificate': True,  # SSL bypass
        }

        Path(audio_dir).mkdir(parents=True, exist_ok=True)

        try:
            os.remove(audio_path)
        except OSError:
            pass
        
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([f'{song.url}'])
        except Exception as e:
            print(f'Error downloading song: {e}')
            await self.play_all_songs(guild)
            return
        
        voice.play(discord.FFmpegPCMAudio(audio_path))
        queue.clear_skip_votes()

    async def wait_for_end_of_song(self, guild: discord.Guild):
        """Wait for the current song to finish."""
        voice = self.voice_clients.get(guild)
        while voice.is_playing():
            await asyncio.sleep(1)

    async def inactivity_disconnect(self, guild: discord.Guild):
        """If a song is not played for 5 minutes, automatically disconnects bot from server."""
        voice = self.voice_clients.get(guild)
        queue = self.music_queues.get(guild)
        last_song = queue.current_song

        await asyncio.sleep(300)
        if queue.current_song == last_song:
            await voice.disconnect()

    def client_in_same_channel(self, author: discord.Member, guild: discord.Guild):
        """Checks to see if a client is in the same channel as the bot."""
        voice = self.voice_clients.get(guild)

        try:
            channel = author.voice.channel
        except AttributeError:
            return False
        
        return voice is not None and voice.is_connected() and channel == voice.channel

    @staticmethod
    def song_error_check(song: Song):
        """Checks song properties to ensure that the song is both valid and doesn't match any filtered properties"""
        if song.url is None:
            return False, 'Invalid URL provided or no video found.'
        
        if song.get('is_live', True):
            return False, 'Invalid video - either live stream or unsupported website.'

        if song.duration_raw > DURATION_CEILING:
            return False, f'Video is too long. Keep it under {DURATION_CEILING_STRING}.'
        
        return True, None

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state updates."""
        if member.bot:
            return

        # If the bot is alone in a voice channel, disconnect after 60 seconds
        if before.channel and after.channel != before.channel:
            voice = discord.utils.get(self.bot.voice_clients, guild=member.guild)
            if voice and voice.channel == before.channel:
                members = [m for m in before.channel.members if not m.bot]
                if not members:
                    await asyncio.sleep(60)
                    if voice.channel == before.channel:
                        await voice.disconnect()

async def setup(bot):
    await bot.add_cog(Music(bot))