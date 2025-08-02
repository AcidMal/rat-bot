# Rat Bot - Discord Bot

A feature-rich Discord bot built with Discord.py that provides useful server management and utility commands, organized into modular cogs for easy maintenance. Includes a SQLite database for persistent data storage and mod logs. **Supports both slash commands and legacy prefix commands!** **Now with sharding support for large-scale deployments!**

## Features

- **Sharding Support**: Automatic and manual sharding for bots with 2500+ servers
- **Hybrid Commands**: All commands work as both slash commands and legacy prefix commands
- **Music System**: Full music player with queue management, YouTube support, and voice controls
- **Modular Design**: Commands organized into separate cog files by category
- **Database Integration**: SQLite database for mod logs, warnings, custom commands, and user stats
- **Auto-Installation**: Shell script for easy setup and installation
- **Utility Commands**: Ping, info, help, echo
- **Server Management**: Clear messages, kick, ban, unban, warn, warnings
- **Information Commands**: User info, server info, role info, channel info
- **Fun Commands**: 8ball, coinflip, dice, rock-paper-scissors, choose, reverse, emojify
- **Custom Commands**: Create and manage server-specific custom commands
- **Moderation Logs**: Automatic logging of all moderation actions
- **Error Handling**: Comprehensive error handling and logging
- **Modern UI**: Rich embeds for all responses
- **Permission System**: Proper permission checks for admin commands

## Quick Start

### 1. Auto-Installation (Recommended)

```bash
# Make install script executable
chmod +x install.sh

# Run the installation script
./install.sh

# Edit .env file with your bot token
nano .env

# Run the bot (choose one option)
./run.sh                    # Single instance
./run.sh --sharded          # Automatic sharding
./run.sh --shard-manager 4  # Manual sharding with 4 shards
```

### 2. Manual Installation

Follow the detailed setup instructions below.

## Sharding Support

### What is Sharding?

Sharding is a technique used by Discord bots to handle large numbers of servers (2500+) efficiently. When a bot joins more than 2500 servers, Discord requires the bot to use sharding to distribute the load across multiple connections.

### Sharding Options

#### 1. **Automatic Sharding** (Recommended for most users)
```bash
./run.sh --sharded
```
- Discord.py automatically determines the optimal number of shards
- Single process handles all shards
- Best for bots with moderate server counts

#### 2. **Manual Sharding** (For very large bots)
```bash
./run.sh --shard-manager 4
```
- Manually specify the number of shards
- Multiple processes for better resource distribution
- Includes automatic crash recovery and monitoring
- Best for bots with 10,000+ servers

#### 3. **Single Instance** (For small bots)
```bash
./run.sh
```
- No sharding, single bot instance
- Best for bots with fewer than 2500 servers

### Sharding Configuration

You can configure sharding in `config.py`:

```python
# For automatic sharding (recommended)
SHARD_COUNT = None
SHARD_IDS = None

# For manual sharding
SHARD_COUNT = 4
SHARD_IDS = [0, 1, 2, 3]
```

### Shard Manager Features

The shard manager provides:
- **Automatic crash recovery**: Restarts crashed shards
- **Process monitoring**: Tracks shard health
- **Graceful shutdown**: Properly stops all shards
- **Status reporting**: Shows shard status every 30 seconds
- **Resource management**: Efficient process handling

### When to Use Sharding

- **< 2500 servers**: No sharding needed
- **2500-10,000 servers**: Automatic sharding recommended
- **> 10,000 servers**: Manual sharding with shard manager recommended

## Commands

**All commands work with both slash commands (`/command`) and legacy prefix commands (`!command`)**

### General Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `ping` | Check bot latency | `/ping` or `!ping` |
| `info` | Display bot information | `/info` or `!info` |
| `help` | Show help menu | `/help` or `!help` |
| `echo` | Make bot repeat message | `/echo <message>` or `!echo <message>` |

### Music Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `join` | Join a voice channel | `/join` or `!join` |
| `play` | Play a song from YouTube | `/play <song>` or `!play <song>` |
| `pause` | Pause the current song | `/pause` or `!pause` |
| `resume` | Resume the paused song | `/resume` or `!resume` |
| `skip` | Skip the current song | `/skip` or `!skip` |
| `stop` | Stop playing and clear queue | `/stop` or `!stop` |
| `queue` | Show the music queue | `/queue` or `!queue` |
| `nowplaying` | Show current song | `/nowplaying` or `!nowplaying` |
| `volume` | Set music volume | `/volume <0-100>` or `!volume <0-100>` |
| `leave` | Leave voice channel | `/leave` or `!leave` |

### Moderation Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `clear` | Clear messages (Admin) | `/clear [amount]` or `!clear [amount]` |
| `kick` | Kick a member (Admin) | `/kick @user [reason]` or `!kick @user [reason]` |
| `ban` | Ban a member (Admin) | `/ban @user [reason]` or `!ban @user [reason]` |
| `unban` | Unban a user (Admin) | `/unban <user_id>` or `!unban <user_id>` |
| `warn` | Warn a member (Mod) | `/warn @user <reason>` or `!warn @user <reason>` |
| `warnings` | Check user warnings (Mod) | `/warnings @user` or `!warnings @user` |
| `clearwarnings` | Clear user warnings (Mod) | `/clearwarnings @user` or `!clearwarnings @user` |
| `modlogs` | View moderation logs (Mod) | `/modlogs [@user] [limit]` or `!modlogs [@user] [limit]` |
| `setmodlog` | Set mod log channel (Admin) | `/setmodlog #channel` or `!setmodlog #channel` |

### Custom Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `addcommand` | Add custom command (Mod) | `/addcommand <name> <response>` or `!addcommand <name> <response>` |
| `delcommand` | Delete custom command (Mod) | `/delcommand <name>` or `!delcommand <name>` |
| `editcommand` | Edit custom command (Mod) | `/editcommand <name> <new_response>` or `!editcommand <name> <new_response>` |
| `listcommands` | List custom commands | `/listcommands` or `!listcommands` |

### Information Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `userinfo` | Get user information | `/userinfo [@user]` or `!userinfo [@user]` |
| `serverinfo` | Get server information | `/serverinfo` or `!serverinfo` |
| `roleinfo` | Get role information | `/roleinfo @role` or `!roleinfo @role` |
| `channelinfo` | Get channel information | `/channelinfo [#channel]` or `!channelinfo [#channel]` |
| `botinfo` | Get detailed bot information | `/botinfo` or `!botinfo` |

### Fun Commands
| Command | Description | Usage |
|---------|-------------|-------|
| `8ball` | Ask the magic 8-ball | `/8ball <question>` or `!8ball <question>` |
| `coinflip` | Flip a coin | `/coinflip` or `!coinflip` |
| `dice` | Roll a dice | `/dice [sides]` or `!dice [sides]` |
| `rps` | Play rock-paper-scissors | `/rps <choice>` or `!rps <choice>` |
| `choose` | Choose between options | `/choose <options>` or `!choose <options>` |
| `reverse` | Reverse text | `/reverse <text>` or `!reverse <text>` |
| `emojify` | Convert text to emojis | `/emojify <text>` or `!emojify <text>` |

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord bot token
- Bash shell (for auto-installation script)
- **FFmpeg** (for music functionality)

### 2. Install FFmpeg

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
- Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Or use: `choco install ffmpeg` (Chocolatey)
- Or use: `winget install FFmpeg` (Windows Package Manager)

### 3. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Copy the bot token (you'll need this later)
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent
6. **Important**: Go to "OAuth2 > URL Generator" and select:
   - `bot` under scopes
   - `applications.commands` under scopes (for slash commands)
   - All necessary permissions

### 4. Auto-Installation (Recommended)

```bash
# Clone or download the bot files
# Navigate to the bot directory
cd rat-bot

# Make install script executable
chmod +x install.sh

# Run the installation script
./install.sh

# Edit the .env file with your bot token
nano .env
# or
code .env

# Run the bot (choose your preferred method)
./run.sh                    # Single instance
./run.sh --sharded          # Automatic sharding
./run.sh --shard-manager 4  # Manual sharding with 4 shards
```

### 5. Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp example.env .env
# Edit .env and add your bot token

# Run the bot
python bot.py
```

### 6. Invite the Bot to Your Server

1. Go to OAuth2 > URL Generator in the Discord Developer Portal
2. Select both "bot" and "applications.commands" under scopes
3. Select the permissions you want (at minimum: Send Messages, Read Message History, Use Slash Commands, Connect, Speak)
4. Use the generated URL to invite the bot to your server

## Music System

The bot includes a comprehensive music system with the following features:

### Music Commands
- **`/play <song>`** - Play music from YouTube (URL or search term)
- **`/pause`** - Pause the current song
- **`/resume`** - Resume the paused song
- **`/skip`** - Skip to the next song
- **`/stop`** - Stop playing and clear the queue
- **`/queue`** - View the current music queue
- **`/nowplaying`** - Show currently playing song
- **`/volume <0-100>`** - Set the music volume
- **`/join`** - Join your voice channel
- **`/leave`** - Leave the voice channel

### Music Features
- **YouTube Support**: Play from YouTube URLs or search terms
- **Queue Management**: Add multiple songs to a queue
- **Volume Control**: Adjust music volume
- **Auto-disconnect**: Bot leaves when alone in voice channel
- **Rich Embeds**: Beautiful song information displays
- **Error Handling**: Graceful handling of music errors

### Music Usage Examples
```bash
# Join and play a song
/join
/play despacito

# Play from YouTube URL
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Control playback
/pause
/resume
/skip

# Manage queue
/queue
/nowplaying
/volume 50

# Leave voice channel
/leave
```

## Slash Commands vs Legacy Commands

### Slash Commands (`/command`)
- **Modern Discord interface**
- **Auto-completion and suggestions**
- **Parameter descriptions and validation**
- **Better mobile experience**
- **Automatic permission checking**

### Legacy Commands (`!command`)
- **Faster typing for experienced users**
- **Works with custom prefixes**
- **Familiar to long-time Discord users**
- **No need to wait for Discord's slash command system**

### Hybrid Support
All commands in this bot work with **both** systems simultaneously:
- Use `/ping` or `!ping` - both work!
- Use `/kick @user reason` or `!kick @user reason` - both work!
- The bot automatically syncs slash commands on startup and when joining new servers

## Project Structure

```
rat-bot/
├── bot.py              # Main bot file with events and cog loading
├── config.py           # Configuration and environment variables
├── database.py         # Database management and operations
├── shard_manager.py    # Shard management for large-scale deployments
├── run_sharded.py      # Simple sharded bot runner
├── requirements.txt    # Python dependencies
├── install.sh         # Auto-installation script
├── run.sh             # Bot run script with sharding options
├── README.md          # This file
├── example.env        # Environment template
├── .gitignore         # Git ignore file
├── data/              # Database files
│   └── bot.db        # SQLite database
├── logs/              # Log files
└── cogs/              # Command categories
    ├── __init__.py    # Package initialization
    ├── general.py     # General utility commands
    ├── moderation.py  # Moderation commands with database logging
    ├── info.py        # Information commands
    ├── fun.py         # Fun and entertainment commands
    ├── custom.py      # Custom commands management
    └── music.py       # Music player functionality
```

## Database Features

The bot uses a SQLite database with the following tables:

- **mod_logs**: Tracks all moderation actions (kick, ban, warn, etc.)
- **user_warnings**: Stores user warnings with reasons and timestamps
- **custom_commands**: Server-specific custom commands
- **server_settings**: Server configuration (mod log channels, prefixes, etc.)
- **user_stats**: User activity tracking (messages, commands used)

## Configuration

You can modify the bot settings in `config.py`:

- `BOT_PREFIX`: Command prefix (default: "!")
- `BOT_NAME`: Bot name for display
- `BOT_VERSION`: Bot version
- `SHARD_COUNT`: Number of shards for manual sharding
- `SHARD_IDS`: Specific shard IDs to run

## Moderation Logs

The bot automatically logs all moderation actions to a designated channel:

1. Set up a mod log channel: `/setmodlog #mod-logs` or `!setmodlog #mod-logs`
2. All moderation actions will be logged automatically
3. View logs with: `/modlogs` or `!modlogs @user`

## Custom Commands

Create server-specific custom commands:

- `/addcommand hello Welcome to our server!` or `!addcommand hello Welcome to our server!`
- `/listcommands` or `!listcommands` - View all custom commands
- `/editcommand hello Welcome to our amazing server!` or `!editcommand hello Welcome to our amazing server!`
- `/delcommand hello` or `!delcommand hello` - Delete a custom command

## Adding New Commands

To add new commands, simply create a new file in the `cogs/` directory or add to an existing cog file:

1. Create a new Python file in `cogs/` (e.g., `cogs/your_category.py`)
2. Define a cog class with your commands using `@commands.hybrid_command`
3. Add a `setup(bot)` function at the bottom
4. The bot will automatically load the new cog on startup

Example:
```python
import discord
from discord.ext import commands
from discord import app_commands

class YourCategory(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name='yourcommand', description="Your command description")
    @app_commands.describe(parameter="Description of the parameter")
    async def your_command(self, ctx, parameter: str):
        await ctx.send("Your command response!")

async def setup(bot):
    await bot.add_cog(YourCategory(bot))
```

## Features in Detail

### Sharding System
- **Automatic Sharding**: Discord.py automatically determines optimal shard count
- **Manual Sharding**: Custom shard management for very large bots
- **Shard Manager**: Process monitoring and crash recovery
- **Cross-shard Communication**: Commands work across all shards
- **Resource Optimization**: Efficient memory and CPU usage

### Music System
- **YouTube Integration**: Play from YouTube URLs or search terms
- **Queue Management**: Add multiple songs to a queue
- **Volume Control**: Adjust music volume (0-100%)
- **Auto-disconnect**: Bot leaves when alone in voice channel
- **Rich Embeds**: Beautiful song information displays
- **Error Handling**: Graceful handling of music errors

### Hybrid Commands
- **Dual compatibility**: Works with both slash and legacy commands
- **Automatic syncing**: Commands sync to Discord on startup
- **Parameter descriptions**: Rich descriptions for slash command parameters
- **Type validation**: Automatic parameter type checking

### Database Integration
- Persistent storage for all bot data
- Automatic mod action logging
- User warning system
- Custom commands per server
- User activity tracking

### Auto-Installation Script
- Checks Python version requirements
- Checks FFmpeg installation (for music)
- Creates virtual environment
- Installs all dependencies
- Sets up database structure
- Creates necessary directories

### Modular Design
- Commands organized into logical categories
- Easy to maintain and extend
- Automatic cog loading system

### Error Handling
- Command not found errors
- Permission errors
- General error logging
- Separate error handling for slash and legacy commands

### Logging
- Comprehensive logging system
- Guild join/leave tracking
- Command error logging
- Shard status monitoring

### Rich Embeds
- All responses use Discord embeds
- Color-coded responses
- Professional appearance

### Permission System
- Admin-only commands properly protected
- User-friendly permission error messages

## Troubleshooting

### Common Issues

1. **Bot not starting**: Check your `.env` file has the correct token
2. **Commands not working**: Ensure the bot has the required permissions
3. **Slash commands not appearing**: Make sure you invited the bot with `applications.commands` scope
4. **Music not working**: Ensure FFmpeg is installed and in PATH
5. **Database errors**: Run `./install.sh` again to recreate the database
6. **Permission denied**: Make sure the scripts are executable: `chmod +x *.sh`

### Sharding Issues

1. **"Too many guilds"**: Enable sharding with `./run.sh --sharded`
2. **Shard crashes**: Use the shard manager for automatic recovery
3. **Memory usage**: Manual sharding can help distribute load
4. **Rate limits**: Shard manager includes delays between shard starts

### Music Issues

1. **"FFmpeg not found"**: Install FFmpeg (see setup instructions)
2. **"No module named 'yt_dlp'"**: Run `pip install -r requirements.txt`
3. **Music not playing**: Check bot has "Connect" and "Speak" permissions
4. **Queue not working**: Make sure you're in a voice channel

### Slash Command Sync Issues

If slash commands aren't appearing:
1. Make sure the bot has the `applications.commands` scope
2. Check the bot has proper permissions
3. Wait a few minutes for Discord to sync (can take up to 1 hour)
4. Try running the bot again to force a sync

### Logs

Check the `logs/` directory for detailed error logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue on the repository.

---

**Note**: Make sure to keep your bot token secure and never share it publicly! 