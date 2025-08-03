import discord
from discord.ext import commands
import sys
import os
import subprocess
import asyncio
from typing import Optional
from loguru import logger

class Admin(commands.Cog):
    """Admin-only commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Check if user is bot owner"""
        return await self.bot.is_owner(ctx.author)
    
    @commands.command(name="reload")
    async def reload_cog(self, ctx, *, cog_name: str):
        """Reload a cog"""
        try:
            await self.bot.reload_extension(f"cogs.{cog_name}")
            embed = discord.Embed(
                title="✅ Cog Reloaded",
                description=f"Successfully reloaded `{cog_name}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"Reloaded cog: {cog_name}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Reload Failed",
                description=f"Failed to reload `{cog_name}`: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            logger.error(f"Failed to reload cog {cog_name}: {e}")
    
    @commands.command(name="load")
    async def load_cog(self, ctx, *, cog_name: str):
        """Load a cog"""
        try:
            await self.bot.load_extension(f"cogs.{cog_name}")
            embed = discord.Embed(
                title="✅ Cog Loaded",
                description=f"Successfully loaded `{cog_name}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"Loaded cog: {cog_name}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Load Failed",
                description=f"Failed to load `{cog_name}`: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            logger.error(f"Failed to load cog {cog_name}: {e}")
    
    @commands.command(name="unload")
    async def unload_cog(self, ctx, *, cog_name: str):
        """Unload a cog"""
        if cog_name.lower() == "admin":
            return await ctx.send("❌ Cannot unload the admin cog!")
        
        try:
            await self.bot.unload_extension(f"cogs.{cog_name}")
            embed = discord.Embed(
                title="✅ Cog Unloaded",
                description=f"Successfully unloaded `{cog_name}`",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            logger.info(f"Unloaded cog: {cog_name}")
        except Exception as e:
            embed = discord.Embed(
                title="❌ Unload Failed",
                description=f"Failed to unload `{cog_name}`: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            logger.error(f"Failed to unload cog {cog_name}: {e}")
    
    @commands.command(name="cogs")
    async def list_cogs(self, ctx):
        """List all loaded cogs"""
        loaded_cogs = list(self.bot.cogs.keys())
        
        embed = discord.Embed(
            title="📦 Loaded Cogs",
            description=f"Total: {len(loaded_cogs)} cogs",
            color=0x7289da
        )
        
        if loaded_cogs:
            embed.add_field(
                name="Cogs",
                value="\n".join(f"• {cog}" for cog in sorted(loaded_cogs)),
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="shutdown", aliases=["quit", "exit"])
    async def shutdown(self, ctx):
        """Shutdown the bot"""
        embed = discord.Embed(
            title="⚠️ Shutdown Confirmation",
            description="Are you sure you want to shutdown the bot?",
            color=0xffaa00
        )
        
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == msg.id
        
        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)
            
            if str(reaction.emoji) == "✅":
                embed = discord.Embed(
                    title="🛑 Shutting Down",
                    description="Bot is shutting down...",
                    color=0xff0000
                )
                await msg.edit(embed=embed)
                logger.info(f"Bot shutdown initiated by {ctx.author}")
                await self.bot.close()
            else:
                embed = discord.Embed(
                    title="✅ Shutdown Cancelled",
                    description="Bot shutdown cancelled.",
                    color=0x00ff00
                )
                await msg.edit(embed=embed)
                
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="⏰ Timeout",
                description="Shutdown confirmation timed out.",
                color=0xffaa00
            )
            await msg.edit(embed=embed)
    
    @commands.command(name="restart")
    async def restart(self, ctx):
        """Restart the bot"""
        embed = discord.Embed(
            title="🔄 Restarting",
            description="Bot is restarting...",
            color=0xffaa00
        )
        await ctx.send(embed=embed)
        
        logger.info(f"Bot restart initiated by {ctx.author}")
        
        # Try to restart using systemctl if available
        try:
            subprocess.run(["sudo", "systemctl", "restart", "discord-bot"], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to regular shutdown (requires external process manager)
            await self.bot.close()
    
    @commands.command(name="update")
    async def update_bot(self, ctx):
        """Update the bot from GitHub"""
        embed = discord.Embed(
            title="🔄 Updating Bot",
            description="Pulling latest changes from GitHub...",
            color=0xffaa00
        )
        msg = await ctx.send(embed=embed)
        
        try:
            # Run update script
            process = await asyncio.create_subprocess_shell(
                "./update.sh --no-restart",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                embed = discord.Embed(
                    title="✅ Update Successful",
                    description="Bot updated successfully! Restart required to apply changes.",
                    color=0x00ff00
                )
                
                if stdout:
                    output = stdout.decode()[-1000:]  # Last 1000 chars
                    embed.add_field(name="Output", value=f"```\n{output}\n```", inline=False)
            else:
                embed = discord.Embed(
                    title="❌ Update Failed",
                    description="Failed to update bot.",
                    color=0xff0000
                )
                
                if stderr:
                    error = stderr.decode()[-1000:]  # Last 1000 chars
                    embed.add_field(name="Error", value=f"```\n{error}\n```", inline=False)
            
            await msg.edit(embed=embed)
            logger.info(f"Bot update initiated by {ctx.author}")
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Update Error",
                description=f"An error occurred during update: {str(e)}",
                color=0xff0000
            )
            await msg.edit(embed=embed)
            logger.error(f"Update error: {e}")
    
    @commands.command(name="eval")
    async def eval_code(self, ctx, *, code: str):
        """Evaluate Python code"""
        # Remove code blocks if present
        if code.startswith("```python"):
            code = code[9:-3]
        elif code.startswith("```"):
            code = code[3:-3]
        
        try:
            # Create environment
            env = {
                'bot': self.bot,
                'ctx': ctx,
                'channel': ctx.channel,
                'author': ctx.author,
                'guild': ctx.guild,
                'message': ctx.message,
                'discord': discord,
                'commands': commands
            }
            
            result = eval(code, env)
            
            if asyncio.iscoroutine(result):
                result = await result
            
            embed = discord.Embed(
                title="✅ Evaluation Result",
                color=0x00ff00
            )
            embed.add_field(name="Input", value=f"```python\n{code}\n```", inline=False)
            embed.add_field(name="Output", value=f"```python\n{result}\n```", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Evaluation Error",
                color=0xff0000
            )
            embed.add_field(name="Input", value=f"```python\n{code}\n```", inline=False)
            embed.add_field(name="Error", value=f"```python\n{str(e)}\n```", inline=False)
            
            await ctx.send(embed=embed)
    
    @commands.command(name="sql")
    async def execute_sql(self, ctx, *, query: str):
        """Execute SQL query (MongoDB aggregation or JSON query)"""
        if not self.bot.db:
            return await ctx.send("❌ Database not available")
        
        try:
            # This is a simplified example - implement based on your database type
            embed = discord.Embed(
                title="📊 SQL Query",
                description="SQL execution not implemented for this database type",
                color=0xffaa00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ SQL Error",
                description=f"Error executing query: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="viewlogs")
    async def view_logs(self, ctx, lines: int = 20):
        """View recent log entries"""
        if lines > 50:
            lines = 50
        
        try:
            # Read log file
            log_file = "logs/bot.log"
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    log_lines = f.readlines()
                
                recent_logs = log_lines[-lines:]
                log_content = ''.join(recent_logs)
                
                if len(log_content) > 1900:  # Discord embed limit
                    log_content = log_content[-1900:] + "..."
                
                embed = discord.Embed(
                    title=f"📋 Recent Logs ({lines} lines)",
                    description=f"```\n{log_content}\n```",
                    color=0x7289da
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Log file not found")
                
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Reading Logs",
                description=f"Error: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name="stats")
    async def show_stats(self, ctx):
        """Show detailed bot statistics"""
        embed = discord.Embed(
            title="📊 Bot Statistics",
            color=0x7289da
        )
        
        # Basic stats
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds):,}", inline=True)
        embed.add_field(name="Users", value=f"{len(self.bot.users):,}", inline=True)
        embed.add_field(name="Commands", value=f"{len(self.bot.commands)}", inline=True)
        
        # Node stats if available
        if hasattr(self.bot, 'node_manager') and self.bot.node_manager:
            try:
                nodes = await self.bot.node_manager.get_cluster_nodes()
                embed.add_field(name="Cluster Nodes", value=f"{len(nodes)}", inline=True)
            except:
                pass
        
        # Shard stats if sharded
        if hasattr(self.bot, 'shard_manager') and self.bot.shard_manager:
            try:
                shard_stats = self.bot.shard_manager.get_total_stats()
                embed.add_field(name="Shards", value=f"{shard_stats['total_shards']}", inline=True)
                embed.add_field(name="Avg Latency", value=f"{shard_stats['average_latency']:.2f}ms", inline=True)
            except:
                pass
        
        # Database stats
        if self.bot.db:
            try:
                db_stats = await self.bot.db.get_global_stats()
                embed.add_field(name="Total Commands", value=f"{db_stats.get('total_commands_used', 0):,}", inline=True)
                embed.add_field(name="Total Songs", value=f"{db_stats.get('total_songs_played', 0):,}", inline=True)
            except:
                pass
        
        await ctx.send(embed=embed)
    
    @commands.command(name="broadcast")
    async def broadcast_message(self, ctx, *, message: str):
        """Broadcast a message to all servers"""
        embed = discord.Embed(
            title="📢 Broadcasting Message",
            description="Sending message to all servers...",
            color=0xffaa00
        )
        msg = await ctx.send(embed=embed)
        
        sent_count = 0
        failed_count = 0
        
        broadcast_embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=0x7289da
        )
        broadcast_embed.set_footer(text="This is an announcement from the bot owner")
        
        for guild in self.bot.guilds:
            try:
                # Try to send to system channel first, then first available channel
                channel = guild.system_channel
                if not channel:
                    channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)
                
                if channel:
                    await channel.send(embed=broadcast_embed)
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except discord.Forbidden:
                failed_count += 1
            except Exception:
                failed_count += 1
        
        result_embed = discord.Embed(
            title="✅ Broadcast Complete",
            color=0x00ff00
        )
        result_embed.add_field(name="Sent", value=f"{sent_count} servers", inline=True)
        result_embed.add_field(name="Failed", value=f"{failed_count} servers", inline=True)
        
        await msg.edit(embed=result_embed)

async def setup(bot):
    await bot.add_cog(Admin(bot))