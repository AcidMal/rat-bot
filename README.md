# 🐀 RatBot - Discord Music & Moderation Bot

A feature-rich Discord bot built with Discord.py that includes music playback, moderation tools, and comprehensive logging.

## ✨ Features

### 🎵 Music Features
- **YouTube, SoundCloud, and more** - Play music from various sources
- **Queue management** - Add, remove, and manage your music queue
- **Volume control** - Adjust playback volume
- **Playback controls** - Play, pause, resume, skip, and stop
- **Lavalink integration** - High-quality audio processing

### 🛡️ Moderation Features
- **User management** - Kick, ban, unban, timeout users
- **Warning system** - Issue warnings to users
- **Message clearing** - Bulk delete messages
- **Comprehensive logging** - All actions logged to database and Discord channels

### 📊 General Features
- **Server information** - Detailed server stats and info
- **User information** - User profiles and statistics
- **System monitoring** - Bot performance and system stats
- **Customizable prefix** - Change bot command prefix
- **Embedded responses** - Beautiful, formatted responses

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Java 11 or higher (for Lavalink)
- PostgreSQL database
- Discord Bot Token

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd rat-bot
   ```

2. **Run the installation script**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Configure the bot**
   - Edit the `.env` file with your settings
   - Set up your PostgreSQL database
   - Add your Discord bot token

4. **Start the bot**
   ```bash
   ./start.sh
   ```

## 📋 Configuration

### Environment Variables (.env file)

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ratbot

# Lavalink Configuration
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass

# Bot Configuration
PREFIX=!
EMBED_COLOR=0x00ff00

# Logging Configuration
LOG_LEVEL=INFO

# ModLog Configuration
MODLOG_CHANNEL_ID=your_modlog_channel_id_here
```

### Database Setup

1. Install PostgreSQL
2. Create a database named `ratbot`
3. Update the `DATABASE_URL` in your `.env` file
4. The bot will automatically create the necessary tables

## 🎮 Commands

### Music Commands
- `!join` / `!j` - Join a voice channel
- `!play <query>` / `!p <query>` - Play a song
- `!pause` - Pause the current track
- `!resume` - Resume the current track
- `!stop` - Stop playing and clear queue
- `!skip` / `!s` - Skip the current track
- `!queue` / `!q` - Show the current queue
- `!volume <0-100>` / `!vol <0-100>` - Set volume
- `!leave` / `!dc` - Leave the voice channel

### Moderation Commands
- `!kick <user> [reason]` - Kick a user
- `!ban <user> [reason]` - Ban a user
- `!unban <user_id> [reason]` - Unban a user
- `!timeout <user> <duration> [reason]` - Timeout a user
- `!warn <user> [reason]` - Warn a user
- `!modlogs [user] [limit]` - Show moderation logs
- `!clear <amount>` - Clear messages

### General Commands
- `!ping` - Check bot latency
- `!info` - Show bot information
- `!serverinfo` / `!server` - Show server information
- `!userinfo [user]` / `!user [user]` - Show user information
- `!avatar [user]` / `!av [user]` - Show user avatar
- `!invite` - Get bot invite link
- `!help [command]` - Show help information

## 🛠️ Management Scripts

### Installation
```bash
./install.sh
```
Installs all dependencies, downloads Lavalink, and sets up the environment.

### Starting the Bot
```bash
./start.sh              # Start normally
./start.sh -d           # Start in background
./start.sh -v           # Start with verbose logging
./start.sh --no-lavalink # Start without Lavalink
```

### Stopping the Bot
```bash
./stop.sh
```
Safely stops the bot and Lavalink server.

### Updating the Bot
```bash
./update.sh
```
Updates the bot from GitHub and updates dependencies.

### Troubleshooting
```bash
./troubleshoot.sh
```
Interactive script to fix common installation and dependency issues.

## 📁 Project Structure

```
rat-bot/
├── main.py                 # Main bot file
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── application.yml        # Lavalink configuration
├── install.sh            # Installation script
├── start.sh              # Start script
├── stop.sh               # Stop script
├── update.sh             # Update script
├── .env                  # Environment variables
├── cogs/                 # Bot cogs (modules)
│   ├── general.py        # General commands
│   ├── music.py          # Music commands
│   └── moderation.py     # Moderation commands
├── database/             # Database models
│   └── models.py         # Database class
├── logs/                 # Log files
└── data/                 # Data files
```

## 🔧 Development

### Adding New Commands
1. Create a new cog in the `cogs/` directory
2. Add the cog to the `load_cogs()` method in `main.py`
3. Follow the existing cog structure

### Database Schema
The bot automatically creates these tables:
- `modlogs` - Moderation action logs
- `guild_settings` - Per-guild settings
- `music_queues` - Music queue data

### Logging
- Bot logs: `logs/bot.log`
- Lavalink logs: `logs/lavalink.log`
- Log level can be set in `.env` file

## 🐛 Troubleshooting

### Common Issues

**Bot won't start**
- Check your `.env` file configuration
- Ensure PostgreSQL is running
- Verify your Discord token is correct

**Music not working**
- Make sure Java 11+ is installed
- Check if Lavalink.jar exists
- Verify Lavalink is running (check logs/lavalink.log)

**Database connection failed**
- Ensure PostgreSQL is installed and running
- Check your DATABASE_URL in `.env`
- Verify the database exists

**Permission errors**
- Check bot permissions in Discord
- Ensure bot has required roles
- Verify channel permissions

**yarl installation issues**
- The install script automatically installs yarl from system packages
- If you encounter issues, run: `sudo apt-get install python3-yarl` (Ubuntu/Debian)
- Or: `sudo dnf install python3-yarl` (Fedora/RHEL)
- Or: `sudo pacman -S python-yarl` (Arch Linux)

### Getting Help
1. Check the logs in the `logs/` directory
2. Run with verbose logging: `./start.sh -v`
3. Check the bot's status with `!ping` and `!info`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the logs for error messages
- Verify your configuration is correct

---

**Made with ❤️ using Discord.py and Lavalink** 