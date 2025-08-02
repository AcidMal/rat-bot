import discord
from discord.ext import commands
from discord import app_commands
from database import db

class Custom(commands.Cog):
    """Custom commands management."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='addcommand', description="Add a custom command")
    @app_commands.describe(command_name="Name of the custom command", response="Response for the command")
    @commands.has_permissions(manage_messages=True)
    async def add_command(self, ctx, command_name: str, *, response: str):
        """Add a custom command."""
        # Check if command name is valid
        if not command_name.isalnum():
            await ctx.send("❌ Command name must contain only letters and numbers.")
            return
        
        # Check if command name conflicts with existing bot commands
        if self.bot.get_command(command_name):
            await ctx.send("❌ This command name conflicts with an existing bot command.")
            return
        
        # Check if custom command already exists
        existing = db.get_custom_command(ctx.guild.id, command_name)
        if existing:
            await ctx.send("❌ A custom command with this name already exists.")
            return
        
        # Add the custom command
        if db.add_custom_command(ctx.guild.id, command_name, response, ctx.author.id):
            embed = discord.Embed(
                title="✅ Custom Command Added",
                description=f"Command `{command_name}` has been created successfully!",
                color=discord.Color.green()
            )
            embed.add_field(name="Response", value=response[:100] + "..." if len(response) > 100 else response, inline=False)
            embed.set_footer(text=f"Created by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to create custom command.")
    
    @commands.hybrid_command(name='delcommand', description="Delete a custom command")
    @app_commands.describe(command_name="Name of the custom command to delete")
    @commands.has_permissions(manage_messages=True)
    async def delete_command(self, ctx, command_name: str):
        """Delete a custom command."""
        # Check if command exists
        existing = db.get_custom_command(ctx.guild.id, command_name)
        if not existing:
            await ctx.send("❌ No custom command found with that name.")
            return
        
        # Delete the command
        if db.delete_custom_command(ctx.guild.id, command_name):
            embed = discord.Embed(
                title="🗑️ Custom Command Deleted",
                description=f"Command `{command_name}` has been deleted successfully!",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Deleted by {ctx.author.display_name}")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ Failed to delete custom command.")
    
    @commands.hybrid_command(name='listcommands', description="List all custom commands for this server")
    async def list_commands(self, ctx):
        """List all custom commands for this server."""
        commands = db.get_guild_custom_commands(ctx.guild.id)
        
        if not commands:
            embed = discord.Embed(
                title="📋 Custom Commands",
                description="No custom commands found for this server.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="📋 Custom Commands",
                description=f"Found {len(commands)} custom command(s):",
                color=discord.Color.blue()
            )
            
            for cmd in commands:
                embed.add_field(
                    name=f"!{cmd['command_name']}",
                    value=f"**Response:** {cmd['response'][:50]}{'...' if len(cmd['response']) > 50 else ''}\n**Created:** {cmd['created_at']}",
                    inline=False
                )
        
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='editcommand', description="Edit a custom command's response")
    @app_commands.describe(command_name="Name of the custom command to edit", new_response="New response for the command")
    @commands.has_permissions(manage_messages=True)
    async def edit_command(self, ctx, command_name: str, *, new_response: str):
        """Edit a custom command's response."""
        # Check if command exists
        existing = db.get_custom_command(ctx.guild.id, command_name)
        if not existing:
            await ctx.send("❌ No custom command found with that name.")
            return
        
        # Delete old command and create new one
        if db.delete_custom_command(ctx.guild.id, command_name):
            if db.add_custom_command(ctx.guild.id, command_name, new_response, ctx.author.id):
                embed = discord.Embed(
                    title="✏️ Custom Command Updated",
                    description=f"Command `{command_name}` has been updated successfully!",
                    color=discord.Color.green()
                )
                embed.add_field(name="New Response", value=new_response[:100] + "..." if len(new_response) > 100 else new_response, inline=False)
                embed.set_footer(text=f"Updated by {ctx.author.display_name}")
                
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ Failed to update custom command.")
        else:
            await ctx.send("❌ Failed to update custom command.")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle custom command execution."""
        if message.author.bot:
            return
        
        if not message.content.startswith('!'):
            return
        
        # Extract command name
        command_name = message.content.split()[0][1:].lower()
        
        # Check if it's a custom command
        custom_command = db.get_custom_command(message.guild.id, command_name)
        if custom_command:
            # Increment command usage stats
            db.increment_user_stats(message.author.id, message.guild.id, "commands")
            
            # Send the custom response
            await message.channel.send(custom_command['response'])

async def setup(bot):
    await bot.add_cog(Custom(bot)) 