import discord
from discord.ext import commands
import random
import aiohttp
import asyncio
from typing import Optional

class Fun(commands.Cog):
    """Fun and entertainment commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        asyncio.create_task(self.session.close())
    
    @commands.command(name="roll", aliases=["dice"])
    async def roll_dice(self, ctx, sides: int = 6):
        """Roll a dice with specified sides"""
        if sides < 2:
            return await ctx.send("❌ Dice must have at least 2 sides!")
        
        if sides > 1000:
            return await ctx.send("❌ Dice cannot have more than 1000 sides!")
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{result}** on a {sides}-sided dice!",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="flip", aliases=["coin"])
    async def flip_coin(self, ctx):
        """Flip a coin"""
        result = random.choice(["Heads", "Tails"])
        emoji = "🪙" if result == "Heads" else "🔄"
        
        embed = discord.Embed(
            title=f"{emoji} Coin Flip",
            description=f"The coin landed on **{result}**!",
            color=0xffd700
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, question: str):
        """Ask the magic 8-ball a question"""
        responses = [
            "It is certain", "It is decidedly so", "Without a doubt",
            "Yes definitely", "You may rely on it", "As I see it, yes",
            "Most likely", "Outlook good", "Yes", "Signs point to yes",
            "Reply hazy, try again", "Ask again later", "Better not tell you now",
            "Cannot predict now", "Concentrate and ask again",
            "Don't count on it", "My reply is no", "My sources say no",
            "Outlook not so good", "Very doubtful"
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball",
            color=0x800080
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=response, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="choose")
    async def choose_option(self, ctx, *, options: str):
        """Choose randomly from given options (separated by commas)"""
        choices = [choice.strip() for choice in options.split(',')]
        
        if len(choices) < 2:
            return await ctx.send("❌ Please provide at least 2 options separated by commas!")
        
        if len(choices) > 20:
            return await ctx.send("❌ Please provide no more than 20 options!")
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🤔 Choice Made",
            description=f"I choose: **{chosen}**",
            color=0x00aaff
        )
        embed.add_field(name="Options", value=", ".join(choices), inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="rps")
    async def rock_paper_scissors(self, ctx, choice: str):
        """Play rock, paper, scissors"""
        valid_choices = ["rock", "paper", "scissors"]
        choice = choice.lower()
        
        if choice not in valid_choices:
            return await ctx.send("❌ Please choose rock, paper, or scissors!")
        
        bot_choice = random.choice(valid_choices)
        
        # Determine winner
        if choice == bot_choice:
            result = "It's a tie!"
            color = 0xffaa00
        elif (choice == "rock" and bot_choice == "scissors") or \
             (choice == "paper" and bot_choice == "rock") or \
             (choice == "scissors" and bot_choice == "paper"):
            result = "You win!"
            color = 0x00ff00
        else:
            result = "I win!"
            color = 0xff0000
        
        emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
        
        embed = discord.Embed(
            title="🎮 Rock Paper Scissors",
            color=color
        )
        embed.add_field(name="Your Choice", value=f"{emojis[choice]} {choice.title()}", inline=True)
        embed.add_field(name="My Choice", value=f"{emojis[bot_choice]} {bot_choice.title()}", inline=True)
        embed.add_field(name="Result", value=result, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="joke")
    async def random_joke(self, ctx):
        """Get a random joke"""
        try:
            async with self.session.get("https://official-joke-api.appspot.com/random_joke") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    embed = discord.Embed(
                        title="😂 Random Joke",
                        color=0xffd700
                    )
                    embed.add_field(name="Setup", value=data['setup'], inline=False)
                    embed.add_field(name="Punchline", value=data['punchline'], inline=False)
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a joke. Try again later!")
        except Exception:
            # Fallback jokes
            jokes = [
                ("Why don't scientists trust atoms?", "Because they make up everything!"),
                ("Why did the scarecrow win an award?", "He was outstanding in his field!"),
                ("Why don't eggs tell jokes?", "They'd crack each other up!"),
                ("What do you call a fake noodle?", "An impasta!"),
                ("Why did the math book look so sad?", "Because it had too many problems!")
            ]
            
            setup, punchline = random.choice(jokes)
            
            embed = discord.Embed(
                title="😂 Random Joke",
                color=0xffd700
            )
            embed.add_field(name="Setup", value=setup, inline=False)
            embed.add_field(name="Punchline", value=punchline, inline=False)
            
            await ctx.send(embed=embed)
    
    @commands.command(name="fact")
    async def random_fact(self, ctx):
        """Get a random fact"""
        try:
            async with self.session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    embed = discord.Embed(
                        title="🧠 Random Fact",
                        description=data['text'],
                        color=0x00aaff
                    )
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a fact. Try again later!")
        except Exception:
            # Fallback facts
            facts = [
                "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible.",
                "A group of flamingos is called a 'flamboyance'.",
                "Octopuses have three hearts and blue blood.",
                "Bananas are berries, but strawberries aren't.",
                "A day on Venus is longer than its year.",
                "Wombat poop is cube-shaped.",
                "There are more possible games of chess than there are atoms in the observable universe."
            ]
            
            fact = random.choice(facts)
            
            embed = discord.Embed(
                title="🧠 Random Fact",
                description=fact,
                color=0x00aaff
            )
            
            await ctx.send(embed=embed)
    
    @commands.command(name="quote")
    async def inspirational_quote(self, ctx):
        """Get an inspirational quote"""
        try:
            async with self.session.get("https://api.quotable.io/random") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    embed = discord.Embed(
                        title="💭 Inspirational Quote",
                        description=f'"{data["content"]}"',
                        color=0x9932cc
                    )
                    embed.set_footer(text=f"— {data['author']}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a quote. Try again later!")
        except Exception:
            # Fallback quotes
            quotes = [
                ("The only way to do great work is to love what you do.", "Steve Jobs"),
                ("Innovation distinguishes between a leader and a follower.", "Steve Jobs"),
                ("Life is what happens to you while you're busy making other plans.", "John Lennon"),
                ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
                ("It is during our darkest moments that we must focus to see the light.", "Aristotle")
            ]
            
            quote, author = random.choice(quotes)
            
            embed = discord.Embed(
                title="💭 Inspirational Quote",
                description=f'"{quote}"',
                color=0x9932cc
            )
            embed.set_footer(text=f"— {author}")
            
            await ctx.send(embed=embed)
    
    @commands.command(name="meme")
    async def random_meme(self, ctx):
        """Get a random meme"""
        try:
            async with self.session.get("https://meme-api.herokuapp.com/gimme") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    embed = discord.Embed(
                        title=data['title'],
                        color=0xff6b6b
                    )
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"👍 {data['ups']} | r/{data['subreddit']}")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to fetch a meme. Try again later!")
        except Exception:
            await ctx.send("❌ Failed to fetch a meme. Try again later!")
    
    @commands.command(name="ascii")
    async def ascii_art(self, ctx, *, text: str):
        """Convert text to ASCII art"""
        if len(text) > 10:
            return await ctx.send("❌ Text must be 10 characters or less!")
        
        # Simple ASCII art patterns
        ascii_patterns = {
            'A': ['  █  ', ' █ █ ', '█████', '█   █', '█   █'],
            'B': ['████ ', '█   █', '████ ', '█   █', '████ '],
            'C': [' ████', '█    ', '█    ', '█    ', ' ████'],
            'D': ['████ ', '█   █', '█   █', '█   █', '████ '],
            'E': ['█████', '█    ', '███  ', '█    ', '█████'],
            'F': ['█████', '█    ', '███  ', '█    ', '█    '],
            'G': [' ████', '█    ', '█ ███', '█   █', ' ████'],
            'H': ['█   █', '█   █', '█████', '█   █', '█   █'],
            'I': ['█████', '  █  ', '  █  ', '  █  ', '█████'],
            'J': ['█████', '    █', '    █', '█   █', ' ████'],
            'K': ['█   █', '█  █ ', '███  ', '█  █ ', '█   █'],
            'L': ['█    ', '█    ', '█    ', '█    ', '█████'],
            'M': ['█   █', '██ ██', '█ █ █', '█   █', '█   █'],
            'N': ['█   █', '██  █', '█ █ █', '█  ██', '█   █'],
            'O': [' ███ ', '█   █', '█   █', '█   █', ' ███ '],
            'P': ['████ ', '█   █', '████ ', '█    ', '█    '],
            'Q': [' ███ ', '█   █', '█ █ █', '█  ██', ' ████'],
            'R': ['████ ', '█   █', '████ ', '█  █ ', '█   █'],
            'S': [' ████', '█    ', ' ███ ', '    █', '████ '],
            'T': ['█████', '  █  ', '  █  ', '  █  ', '  █  '],
            'U': ['█   █', '█   █', '█   █', '█   █', ' ███ '],
            'V': ['█   █', '█   █', '█   █', ' █ █ ', '  █  '],
            'W': ['█   █', '█   █', '█ █ █', '██ ██', '█   █'],
            'X': ['█   █', ' █ █ ', '  █  ', ' █ █ ', '█   █'],
            'Y': ['█   █', ' █ █ ', '  █  ', '  █  ', '  █  '],
            'Z': ['█████', '   █ ', '  █  ', ' █   ', '█████'],
            ' ': ['     ', '     ', '     ', '     ', '     ']
        }
        
        text = text.upper()
        lines = ['', '', '', '', '']
        
        for char in text:
            if char in ascii_patterns:
                pattern = ascii_patterns[char]
                for i in range(5):
                    lines[i] += pattern[i] + ' '
        
        ascii_art = '\n'.join(lines)
        
        embed = discord.Embed(
            title="🎨 ASCII Art",
            description=f"```\n{ascii_art}\n```",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="reverse")
    async def reverse_text(self, ctx, *, text: str):
        """Reverse the given text"""
        if len(text) > 1000:
            return await ctx.send("❌ Text must be 1000 characters or less!")
        
        reversed_text = text[::-1]
        
        embed = discord.Embed(
            title="🔄 Reversed Text",
            color=0x00aaff
        )
        embed.add_field(name="Original", value=text, inline=False)
        embed.add_field(name="Reversed", value=reversed_text, inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="mock")
    async def mocking_text(self, ctx, *, text: str):
        """Convert text to mocking SpongeBob case"""
        if len(text) > 500:
            return await ctx.send("❌ Text must be 500 characters or less!")
        
        mocked = ""
        upper = True
        
        for char in text:
            if char.isalpha():
                mocked += char.upper() if upper else char.lower()
                upper = not upper
            else:
                mocked += char
        
        embed = discord.Embed(
            title="🧽 Mocking SpongeBob",
            description=mocked,
            color=0xffff00
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))