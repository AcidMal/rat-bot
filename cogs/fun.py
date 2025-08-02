import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio

class Fun(commands.Cog):
    """Fun and entertainment commands."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='8ball', description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your question for the magic 8-ball")
    async def eight_ball(self, ctx, *, question: str):
        """Ask the magic 8-ball a question."""
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=discord.Color.purple()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)
        embed.set_footer(text=f"Asked by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='coinflip', description="Flip a coin")
    async def coinflip(self, ctx):
        """Flip a coin."""
        result = random.choice(["Heads", "Tails"])
        embed = discord.Embed(
            title="🪙 Coin Flip",
            description=f"The coin landed on: **{result}**!",
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Flipped by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='dice', description="Roll a dice with specified number of sides")
    @app_commands.describe(sides="Number of sides on the dice (default: 6)")
    async def dice(self, ctx, sides: int = 6):
        """Roll a dice with specified number of sides (default: 6)."""
        if sides < 2:
            await ctx.send("❌ A dice must have at least 2 sides.")
            return
        
        result = random.randint(1, sides)
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}** on a {sides}-sided dice!",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Rolled by {ctx.author.display_name}")
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='rps', description="Play rock, paper, scissors")
    @app_commands.describe(choice="Your choice: rock, paper, or scissors")
    async def rock_paper_scissors(self, ctx, choice: str):
        """Play rock, paper, scissors."""
        choices = ["rock", "paper", "scissors"]
        choice = choice.lower()
        
        if choice not in choices:
            await ctx.send("❌ Please choose rock, paper, or scissors.")
            return
        
        bot_choice = random.choice(choices)
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie!"
            color = discord.Color.light_grey()
        elif (
            (choice == "rock" and bot_choice == "scissors") or
            (choice == "paper" and bot_choice == "rock") or
            (choice == "scissors" and bot_choice == "paper")
        ):
            result = "You win!"
            color = discord.Color.green()
        else:
            result = "I win!"
            color = discord.Color.red()
        
        embed = discord.Embed(
            title="✂️ Rock, Paper, Scissors",
            color=color
        )
        embed.add_field(name="Your Choice", value=choice.title(), inline=True)
        embed.add_field(name="My Choice", value=bot_choice.title(), inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        embed.set_footer(text=f"Played by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='choose', description="Choose between multiple options")
    @app_commands.describe(options="Options separated by commas")
    async def choose(self, ctx, *, options: str):
        """Choose between multiple options separated by commas."""
        choices = [option.strip() for option in options.split(",")]
        
        if len(choices) < 2:
            await ctx.send("❌ Please provide at least 2 options separated by commas.")
            return
        
        chosen = random.choice(choices)
        embed = discord.Embed(
            title="🤔 Choice Made",
            description=f"I choose: **{chosen}**",
            color=discord.Color.blue()
        )
        embed.add_field(name="Options", value=", ".join(choices), inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='reverse', description="Reverse the given text")
    @app_commands.describe(text="The text to reverse")
    async def reverse(self, ctx, *, text: str):
        """Reverse the given text."""
        reversed_text = text[::-1]
        embed = discord.Embed(
            title="🔄 Text Reversed",
            color=discord.Color.blue()
        )
        embed.add_field(name="Original", value=text, inline=False)
        embed.add_field(name="Reversed", value=reversed_text, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name='emojify', description="Convert text to emoji letters")
    @app_commands.describe(text="The text to convert to emojis")
    async def emojify(self, ctx, *, text: str):
        """Convert text to emoji letters."""
        emoji_map = {
            'a': '🅰️', 'b': '🅱️', 'c': '©️', 'd': '🇩', 'e': '📧', 'f': '🎏',
            'g': '🇬', 'h': '♓', 'i': 'ℹ️', 'j': '🗾', 'k': '🇰', 'l': '🇱',
            'm': 'Ⓜ️', 'n': '🇳', 'o': '⭕', 'p': '🅿️', 'q': '🇶', 'r': '🇷',
            's': '💲', 't': '✝️', 'u': '🇺', 'v': '♈', 'w': '🇼', 'x': '❌',
            'y': '🇾', 'z': '💤'
        }
        
        emojified = ""
        for char in text.lower():
            if char in emoji_map:
                emojified += emoji_map[char] + " "
            elif char.isdigit():
                emojified += char + " "
            elif char == " ":
                emojified += "  "
        
        if len(emojified) > 2000:
            await ctx.send("❌ The emojified text is too long!")
            return
        
        embed = discord.Embed(
            title="😀 Emojified Text",
            description=emojified,
            color=discord.Color.pink()
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot)) 