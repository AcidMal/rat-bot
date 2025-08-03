# Advanced Discord Bot

A feature-rich, scalable Discord bot built with Python, featuring advanced music capabilities, comprehensive moderation tools, database integration, and clustering support.

## 🌟 Features

### 🎵 Advanced Music System
- **Hybrid Architecture**: Lavalink + yt-dlp for maximum compatibility
- **YouTube Bypass**: Direct YouTube access via yt-dlp when needed
- **Smart Fallback**: Automatic retry with alternative sources
- **Multiple Sources**: SoundCloud, Bandcamp, YouTube, Twitch
- **Dual Search Modes**: Regular (`!play song`) or YouTube (`!play yt:song`)
- **Cookies Support**: Enhanced YouTube access with browser cookies
- **Queue Management**: Add, remove, shuffle, and loop tracks
- **Audio Filters**: Equalizer, bass boost, speed control
- **Playlist Support**: Import and manage playlists
- **Vote Skip System**: Democratic track skipping

### 🛡️ Advanced Moderation
- **Comprehensive Commands**: Kick, ban, timeout, warn, and more
- **Auto-moderation**: Spam detection, word filters, link filtering
- **Moderation Logging**: All actions logged to database
- **Infraction Tracking**: User warning history and escalation
- **Bulk Actions**: Mass delete messages, bulk ban
- **Appeal System**: Built-in appeal and review process

### 📊 Database Integration
- **Multiple Backends**: MongoDB (production) or JSON (development)
- **Persistent Storage**: User data, guild settings, music queues
- **Analytics**: Command usage, user statistics, server metrics
- **Backup System**: Automated backups and data recovery

### ⚡ Sharding & Clustering
- **Auto-sharding**: Automatic shard management for large bots
- **Node Clustering**: Distribute load across multiple servers
- **Redis Integration**: Inter-node communication and caching
- **Load Balancing**: Intelligent request distribution
- **High Availability**: Automatic failover and recovery

### 🌐 Web Dashboard
- **Real-time Monitoring**: Bot statistics and performance metrics
- **Configuration Management**: Change settings via web interface
- **User Management**: View and manage user data
- **Server Analytics**: Detailed guild statistics and insights

### 🎮 Fun & Utility
- **Games**: 8-ball, rock-paper-scissors, trivia
- **Utilities**: QR codes, URL shortening, weather
- **Information**: Server info, user profiles, avatar display
- **Tools**: Base64 encoding, hash generation, JSON formatting

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Java 17+ (for Lavalink)
- MongoDB or Redis (optional)
- Linux server (Ubuntu/Debian/CentOS/Arch)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-bot
   ```

2. **Run the interactive installer**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. **Follow the setup wizard**
   - Enter your Discord bot token
   - Configure database settings
   - Set up Lavalink and Redis
   - Configure web API (optional)
   - Enable sharding (optional)

4. **Start the bot**
   ```bash
   ./start.sh
   ```

### Manual Installation

If you prefer manual installation:

```bash
# Install system dependencies
sudo apt update && sudo apt install python3 python3-pip python3-venv openjdk-17-jdk

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Download Lavalink
wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.4/Lavalink.jar

# Copy and configure environment
cp env.example .env
# Edit .env with your settings

# Start the bot
python main.py
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here
PREFIX=!
EMBED_COLOR=0x7289da

# Database Configuration
DATABASE_TYPE=mongodb  # or json
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=discord_bot
JSON_DATABASE_PATH=data/database.json

# Lavalink Configuration
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass
LAVALINK_SSL=false

# Redis Configuration (for clustering)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Web API Configuration
WEB_API_ENABLED=false
WEB_HOST=0.0.0.0
WEB_PORT=8080
WEB_SECRET_KEY=your_secret_key_here
CORS_ORIGINS=*

# Sharding Configuration
SHARDING_ENABLED=false
SHARD_COUNT=
AUTO_SHARD=true

# Node Configuration
NODE_ID=node-1
CLUSTER_NAME=discord-bot-cluster
IS_PRIMARY_NODE=true
NODE_HEARTBEAT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Owner Configuration
OWNER_IDS=your_user_id_here
```

### Database Setup

#### MongoDB (Recommended for Production)
```bash
# Install MongoDB
sudo apt install mongodb-org

# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# The bot will automatically create collections
```

#### JSON Database (Development)
```bash
# No additional setup required
# Database file will be created automatically
```

### Lavalink Setup

The installer automatically downloads and configures Lavalink. For manual setup:

```bash
# Download Lavalink
wget https://github.com/lavalink-devs/Lavalink/releases/download/4.0.4/Lavalink.jar

# Start Lavalink (in separate terminal)
java -jar Lavalink.jar
```

## 🍪 YouTube Cookies Setup (Optional)

For enhanced YouTube access (age-restricted, region-locked content), you can set up browser cookies:

### Quick Setup
```bash
# Run the interactive setup utility
python setup_cookies.py

# Test cookies functionality
python setup_cookies.py --test
```

### Manual Setup
1. **Export cookies from your browser:**
   - Install "Get cookies.txt LOCALLY" browser extension
   - Go to youtube.com and log in
   - Click extension and download cookies.txt

2. **Place cookies file in one of these locations:**
   - `./cookies.txt` (bot directory) - **Recommended**
   - `./data/cookies.txt`
   - `~/cookies.txt` (home directory)
   - `/rat-bot/cookies.txt` (your specified path)

3. **Restart the bot** - cookies will be automatically detected

### Benefits
- ✅ Access age-restricted videos
- ✅ Bypass region restrictions
- ✅ Better rate limiting
- ✅ Improved search results

### Usage
- **Regular search**: `!play song name` (SoundCloud/Bandcamp)
- **YouTube with cookies**: `!play yt:song name` (enhanced YouTube access)

## 📝 Commands

### Music Commands
- `!play <query>` - Play a song or add to queue (SoundCloud/Bandcamp)
- `!play yt:<query>` - Play from YouTube directly (with cookies support)
- `!pause` - Pause the current track
- `!resume` - Resume playback
- `!skip` - Skip the current track
- `!stop` - Stop music and clear queue
- `!queue` - Show the music queue
- `!volume <1-100>` - Set volume
- `!loop <none|track|queue>` - Set loop mode
- `!shuffle` - Shuffle the queue
- `!nowplaying` - Show current track info

### Moderation Commands
- `!kick <member> [reason]` - Kick a member
- `!ban <member> [reason]` - Ban a member
- `!unban <user_id> [reason]` - Unban a user
- `!timeout <member> <duration> [reason]` - Timeout a member
- `!warn <member> [reason]` - Warn a member
- `!modlogs [member]` - View moderation logs
- `!clear <amount> [member]` - Clear messages

### General Commands
- `!help [command]` - Show help information
- `!ping` - Show bot latency
- `!info` - Show bot information
- `!serverinfo` - Show server information
- `!userinfo [member]` - Show user information
- `!avatar [member]` - Show user avatar

### Fun Commands
- `!roll [sides]` - Roll a dice
- `!flip` - Flip a coin
- `!8ball <question>` - Ask the magic 8-ball
- `!joke` - Get a random joke
- `!fact` - Get a random fact
- `!meme` - Get a random meme

### Utility Commands
- `!qr <text>` - Generate QR code
- `!base64 <encode|decode> <text>` - Base64 operations
- `!hash <algorithm> <text>` - Hash text
- `!timestamp [timestamp]` - Convert timestamps
- `!remind <time> <message>` - Set a reminder
- `!poll <question> <options...>` - Create a poll

### Admin Commands (Bot Owner Only)
- `!reload <cog>` - Reload a cog
- `!shutdown` - Shutdown the bot
- `!restart` - Restart the bot
- `!update` - Update from GitHub
- `!eval <code>` - Evaluate Python code
- `!logs [lines]` - View recent logs

## 🔧 Management Scripts

### Start/Stop Scripts
```bash
./start.sh          # Start the bot
./stop.sh           # Stop the bot
./restart.sh        # Restart the bot
```

### Update Script
```bash
./update.sh         # Update from GitHub
./update.sh --no-restart  # Update without restarting
```

### Backup Script
```bash
./backup.sh         # Create configuration backup
```

## 🐳 Docker Support

### Using Docker Compose
```yaml
version: '3.8'
services:
  discord-bot:
    build: .
    environment:
      - DISCORD_TOKEN=your_token_here
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - mongodb
      - redis
      - lavalink

  mongodb:
    image: mongo:7.0
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:7-alpine

  lavalink:
    image: fredboat/lavalink:dev
    volumes:
      - ./application.yml:/opt/Lavalink/application.yml

volumes:
  mongodb_data:
```

### Running with Docker
```bash
docker-compose up -d
```

## 🌐 Web Dashboard

Access the web dashboard at `http://localhost:8080` (if enabled).

Features:
- Real-time bot statistics
- Server management
- User analytics
- Configuration editor
- Log viewer

## 📊 Monitoring

### System Service (systemd)
```bash
# Install as system service
sudo cp discord-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# View status
sudo systemctl status discord-bot

# View logs
journalctl -u discord-bot -f
```

### Health Checks
The bot includes built-in health checks:
- Database connectivity
- Lavalink connection
- Redis connection (if enabled)
- Shard health (if sharded)
- Node cluster status

## 🔧 Development

### Project Structure
```
discord-bot/
├── core/                 # Core bot components
│   ├── bot.py           # Main bot class
│   ├── node_manager.py  # Clustering manager
│   └── shard_manager.py # Sharding manager
├── cogs/                # Command modules
│   ├── music.py         # Music commands
│   ├── moderation.py    # Moderation commands
│   ├── general.py       # General commands
│   ├── admin.py         # Admin commands
│   ├── fun.py           # Fun commands
│   └── utility.py       # Utility commands
├── database/            # Database modules
│   ├── base.py          # Database interface
│   ├── mongodb.py       # MongoDB implementation
│   └── json_db.py       # JSON implementation
├── web/                 # Web dashboard
├── config.py            # Configuration management
├── main.py              # Entry point
└── requirements.txt     # Python dependencies
```

### Adding New Commands
1. Create a new command in the appropriate cog
2. Use proper error handling and logging
3. Add database integration if needed
4. Update help documentation

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🐛 Troubleshooting

### Common Issues

**Bot not responding to commands**
- Check if the bot has proper permissions
- Verify the command prefix
- Check bot status and logs

**Music not working**
- Ensure Lavalink is running
- Check Java version (17+ required)
- Verify Lavalink configuration

**Database connection failed**
- Check MongoDB/Redis service status
- Verify connection string
- Check firewall settings

**Installation fails**
- Check Python version (3.9+ required)
- Install system dependencies
- Check internet connection

### Getting Help
- Check the logs: `tail -f logs/bot.log`
- Run diagnostics: `./troubleshoot.sh`
- Create an issue on GitHub
- Join our Discord server (if available)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- [Lavalink](https://github.com/lavalink-devs/Lavalink) - Audio server
- [MongoDB](https://www.mongodb.com/) - Database
- [Redis](https://redis.io/) - Caching and messaging
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework

## 📞 Support

For support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details
4. Join our community Discord (if available)

---

Made with ❤️ by the Discord Bot Team