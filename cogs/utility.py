import discord
from discord.ext import commands
import aiohttp
import asyncio
import json
import base64
from datetime import datetime, timezone
from typing import Optional

class Utility(commands.Cog):
    """Utility and tools commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        asyncio.create_task(self.session.close())
    
    @commands.command(name="weather")
    async def weather(self, ctx, *, location: str):
        """Get weather information for a location"""
        # This would require a weather API key
        embed = discord.Embed(
            title="🌤️ Weather Information",
            description="Weather feature requires API configuration.",
            color=0x87ceeb
        )
        embed.add_field(name="Location", value=location, inline=False)
        embed.add_field(name="Note", value="Configure a weather API key to enable this feature.", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="shorten")
    async def shorten_url(self, ctx, url: str):
        """Shorten a URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            # Using a simple URL shortener API (you'd need to implement this)
            embed = discord.Embed(
                title="🔗 URL Shortener",
                description="URL shortening feature requires API configuration.",
                color=0x00aaff
            )
            embed.add_field(name="Original URL", value=url, inline=False)
            embed.add_field(name="Note", value="Configure a URL shortening service to enable this feature.", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to shorten URL: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="qr")
    async def generate_qr(self, ctx, *, text: str):
        """Generate a QR code for the given text"""
        if len(text) > 500:
            return await ctx.send("❌ Text must be 500 characters or less!")
        
        try:
            # Using QR Server API
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={text}"
            
            embed = discord.Embed(
                title="📱 QR Code Generator",
                description=f"QR Code for: `{text}`",
                color=0x000000
            )
            embed.set_image(url=qr_url)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to generate QR code: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="base64")
    async def base64_encode(self, ctx, action: str, *, text: str):
        """Encode or decode base64 text"""
        if action.lower() not in ['encode', 'decode']:
            return await ctx.send("❌ Action must be 'encode' or 'decode'!")
        
        if len(text) > 1000:
            return await ctx.send("❌ Text must be 1000 characters or less!")
        
        try:
            if action.lower() == 'encode':
                encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
                result = encoded
                action_past = "Encoded"
            else:
                decoded = base64.b64decode(text.encode('utf-8')).decode('utf-8')
                result = decoded
                action_past = "Decoded"
            
            embed = discord.Embed(
                title=f"🔐 Base64 {action_past}",
                color=0x00ff00
            )
            embed.add_field(name="Input", value=f"```{text}```", inline=False)
            embed.add_field(name="Output", value=f"```{result}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to {action} text: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="hash")
    async def hash_text(self, ctx, algorithm: str, *, text: str):
        """Hash text using various algorithms"""
        import hashlib
        
        algorithms = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        algorithm = algorithm.lower()
        if algorithm not in algorithms:
            return await ctx.send(f"❌ Supported algorithms: {', '.join(algorithms.keys())}")
        
        if len(text) > 1000:
            return await ctx.send("❌ Text must be 1000 characters or less!")
        
        try:
            hash_obj = algorithms[algorithm]()
            hash_obj.update(text.encode('utf-8'))
            hashed = hash_obj.hexdigest()
            
            embed = discord.Embed(
                title=f"🔒 {algorithm.upper()} Hash",
                color=0x800080
            )
            embed.add_field(name="Input", value=f"```{text}```", inline=False)
            embed.add_field(name="Hash", value=f"```{hashed}```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to hash text: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="color")
    async def color_info(self, ctx, color_code: str):
        """Get information about a color"""
        # Remove # if present
        if color_code.startswith('#'):
            color_code = color_code[1:]
        
        # Validate hex color
        if len(color_code) != 6 or not all(c in '0123456789abcdefABCDEF' for c in color_code):
            return await ctx.send("❌ Please provide a valid hex color code (e.g., #FF0000 or FF0000)")
        
        try:
            # Convert hex to RGB
            hex_color = color_code.upper()
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Convert RGB to HSV
            r, g, b = [x/255.0 for x in rgb]
            max_val = max(r, g, b)
            min_val = min(r, g, b)
            diff = max_val - min_val
            
            # Hue
            if diff == 0:
                hue = 0
            elif max_val == r:
                hue = (60 * ((g - b) / diff) + 360) % 360
            elif max_val == g:
                hue = (60 * ((b - r) / diff) + 120) % 360
            else:
                hue = (60 * ((r - g) / diff) + 240) % 360
            
            # Saturation
            saturation = 0 if max_val == 0 else (diff / max_val) * 100
            
            # Value
            value = max_val * 100
            
            embed = discord.Embed(
                title=f"🎨 Color Information",
                color=int(hex_color, 16)
            )
            
            embed.add_field(name="Hex", value=f"#{hex_color}", inline=True)
            embed.add_field(name="RGB", value=f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})", inline=True)
            embed.add_field(name="HSV", value=f"hsv({hue:.0f}°, {saturation:.0f}%, {value:.0f}%)", inline=True)
            
            # Create a color preview using a colored embed
            embed.set_thumbnail(url=f"https://via.placeholder.com/100x100/{hex_color}/{hex_color}.png")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to process color: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="timestamp")
    async def timestamp(self, ctx, timestamp: Optional[int] = None):
        """Convert timestamp to readable date or get current timestamp"""
        if timestamp is None:
            # Get current timestamp
            current_timestamp = int(datetime.now(timezone.utc).timestamp())
            current_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            embed = discord.Embed(
                title="⏰ Current Timestamp",
                color=0x00aaff
            )
            embed.add_field(name="Timestamp", value=f"`{current_timestamp}`", inline=True)
            embed.add_field(name="Date", value=current_date, inline=True)
            embed.add_field(name="Discord Format", value=f"`<t:{current_timestamp}>`", inline=False)
            embed.add_field(name="Preview", value=f"<t:{current_timestamp}>", inline=True)
            
        else:
            try:
                # Convert timestamp to date
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
                
                embed = discord.Embed(
                    title="⏰ Timestamp Conversion",
                    color=0x00aaff
                )
                embed.add_field(name="Timestamp", value=f"`{timestamp}`", inline=True)
                embed.add_field(name="Date", value=formatted_date, inline=True)
                embed.add_field(name="Discord Format", value=f"`<t:{timestamp}>`", inline=False)
                embed.add_field(name="Preview", value=f"<t:{timestamp}>", inline=True)
                embed.add_field(name="Relative", value=f"<t:{timestamp}:R>", inline=True)
                
            except (ValueError, OSError):
                return await ctx.send("❌ Invalid timestamp!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="json")
    async def format_json(self, ctx, *, json_text: str):
        """Format and validate JSON"""
        if len(json_text) > 1500:
            return await ctx.send("❌ JSON text must be 1500 characters or less!")
        
        try:
            # Parse and format JSON
            parsed = json.loads(json_text)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            
            if len(formatted) > 1900:
                formatted = formatted[:1900] + "..."
            
            embed = discord.Embed(
                title="✅ Valid JSON",
                description=f"```json\n{formatted}\n```",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
        except json.JSONDecodeError as e:
            embed = discord.Embed(
                title="❌ Invalid JSON",
                description=f"Error: {str(e)}",
                color=0xff0000
            )
            embed.add_field(name="Input", value=f"```json\n{json_text}\n```", inline=False)
            
            await ctx.send(embed=embed)
    
    @commands.command(name="remind")
    async def remind_me(self, ctx, time: str, *, message: str):
        """Set a reminder (e.g., !remind 1h30m Buy groceries)"""
        import re
        
        # Parse time string
        time_regex = re.compile(r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
        match = time_regex.match(time.lower())
        
        if not match or not any(match.groups()):
            return await ctx.send("❌ Invalid time format! Use format like: 1d2h30m45s")
        
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
            return await ctx.send("❌ Time must be greater than 0!")
        
        if total_seconds > 86400 * 7:  # 7 days max
            return await ctx.send("❌ Reminder time cannot exceed 7 days!")
        
        embed = discord.Embed(
            title="⏰ Reminder Set",
            description=f"I'll remind you in {time}",
            color=0x00ff00
        )
        embed.add_field(name="Message", value=message, inline=False)
        embed.add_field(name="Time", value=f"<t:{int(datetime.now(timezone.utc).timestamp()) + total_seconds}:R>", inline=True)
        
        await ctx.send(embed=embed)
        
        # Wait and then send reminder
        await asyncio.sleep(total_seconds)
        
        reminder_embed = discord.Embed(
            title="⏰ Reminder",
            description=message,
            color=0xffaa00
        )
        reminder_embed.set_footer(text=f"Reminder set {time} ago")
        
        try:
            await ctx.author.send(embed=reminder_embed)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}", embed=reminder_embed)
    
    @commands.command(name="poll")
    async def create_poll(self, ctx, question: str, *options):
        """Create a poll with reactions"""
        if len(options) < 2:
            return await ctx.send("❌ Please provide at least 2 options!")
        
        if len(options) > 10:
            return await ctx.send("❌ Please provide no more than 10 options!")
        
        # Emoji numbers
        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        
        embed = discord.Embed(
            title="📊 Poll",
            description=question,
            color=0x00aaff
        )
        
        poll_text = ""
        for i, option in enumerate(options):
            poll_text += f"{emojis[i]} {option}\n"
        
        embed.add_field(name="Options", value=poll_text, inline=False)
        embed.set_footer(text=f"Poll created by {ctx.author}")
        
        msg = await ctx.send(embed=embed)
        
        # Add reactions
        for i in range(len(options)):
            await msg.add_reaction(emojis[i])
    
    @commands.command(name="translate")
    async def translate_text(self, ctx, target_lang: str, *, text: str):
        """Translate text to another language"""
        # This would require a translation API
        embed = discord.Embed(
            title="🌐 Translation",
            description="Translation feature requires API configuration.",
            color=0x4169e1
        )
        embed.add_field(name="Target Language", value=target_lang, inline=True)
        embed.add_field(name="Text", value=text, inline=False)
        embed.add_field(name="Note", value="Configure a translation API to enable this feature.", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))