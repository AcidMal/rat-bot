# Discord Bot Template

A comprehensive Discord bot template built with Discord.js v14, featuring music playback, moderation tools, auto-moderation, and support for sharding and clustering.

## Features

- **Slash Commands**: Modern Discord slash command system
- **Music System**: Full-featured music bot with YouTube support
- **Moderation Tools**: Comprehensive moderation system with logging
- **Auto-Moderation**: Configurable auto-mod system
- **Database Integration**: SQLite database for persistent storage
- **Sharding Support**: Built-in sharding for large bots
- **Clustering Support**: Multi-process clustering for high performance
- **Modular Design**: Organized command structure with categories
- **Auto-Updater**: Automated update system for keeping your bot current

### Music Commands
- `/play` - Play music from YouTube
- `/skip` - Skip current song or specific songs in queue
- `/stop` - Stop playback and clear queue
- `/queue` - Show current music queue
- `/clear` - Clear the entire music queue
- `/remove` - Remove a specific song from queue
- `/shuffle` - Shuffle the music queue
- `/nowplaying` - Show currently playing song

### Moderation Commands
- `/kick` - Kick a user from the server
- `/ban` - Ban a user from the server
- `/timeout` - Timeout a user temporarily
- `/untimeout` - Remove timeout from a user
- `/tempban` - Temporarily ban a user with auto-unban
- `/voicemute` - Mute a user in voice channels
- `/voiceunmute` - Unmute a user in voice channels
- `/modlog` - View moderation logs
- `/setup` - Configure bot settings
- `/automod` - Configure auto-moderation settings

### General Commands
- `/ping` - Check bot latency
- `/help` - Display all available commands
- `/shardinfo` - Display shard and cluster information
- `/info` - Get user information

### Auto-Moderation Features
- **Anti Spam**: Detect and prevent message spam
- **Anti Caps**: Prevent excessive capitalization
- **Anti Links**: Block unwanted links
- **Anti Invite**: Block Discord invite links
- **Word Filter**: Filter specific words
- **Mass Mention**: Prevent excessive mentions

## Prerequisites

- Node.js 16.9.0 or higher
- FFmpeg (for music features)
- Discord Bot Token
- Discord Application with proper permissions

### FFmpeg Installation

#### Windows
1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add the `bin` folder to your system PATH
4. Restart your terminal/command prompt

#### macOS
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

#### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

## Installation

### Manual Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd discord-bot
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Discord bot credentials
   ```

4. **Deploy slash commands**
   ```bash
   npm run deploy
   ```

5. **Start the bot**
   ```bash
   npm start
   ```

### Auto-Installation (Debian-based Systems)

1. **Download the installation script**
   ```bash
   wget https://raw.githubusercontent.com/your-repo/discord-bot/main/install.sh
   chmod +x install.sh
   ```

2. **Run the installation script**
   ```bash
   ./install.sh
   ```

3. **Follow the interactive prompts** to configure your bot

4. **Start the bot**
   ```bash
   ./start.sh
   ```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
CLIENT_ID=your_client_id_here
GUILD_ID=your_guild_id_here

# Sharding Configuration (Optional)
TOTAL_SHARDS=auto

# Clustering Configuration (Optional)
TOTAL_CLUSTERS=auto

# Shard/Cluster ID (Set automatically by managers)
SHARD_ID=
CLUSTER_ID=
```

### Bot Permissions

Your bot needs the following permissions:
- **General**: Send Messages, Use Slash Commands, Embed Links
- **Music**: Connect, Speak, Use Voice Activity
- **Moderation**: Kick Members, Ban Members, Manage Messages, Moderate Members

## Usage

### Starting the Bot

```bash
# Normal mode
npm start

# Development mode (with auto-restart)
npm run dev

# With sharding (for large bots)
npm run shard

# With clustering (for high performance)
npm run cluster

# Interactive launcher
npm run run
```

### Deploying Commands

```bash
npm run deploy
```

### Updating Your Bot

The bot includes several updater scripts to keep your installation current:

#### Cross-Platform (Recommended)
```bash
npm run update
```

#### Linux/macOS
```bash
./update.sh
```

#### Windows
```bash
update.bat
```

The updater scripts will:
- Check for updates from the GitHub repository
- Pull latest changes if available
- Update dependencies
- Preserve your local changes by stashing them
- Show recent commits and changes
- Check for new environment variables
- Provide guidance on next steps

## Sharding and Clustering

### Sharding
Sharding allows your bot to handle more servers by splitting them across multiple processes. Use sharding when your bot is in 2500+ servers.

```bash
# Start with automatic sharding
npm run shard

# Or set specific number of shards in .env
TOTAL_SHARDS=4
```

### Clustering
Clustering provides multi-process support for better performance and reliability. Each cluster runs multiple shards.

```bash
# Start with clustering
npm run cluster

# Or set specific number of clusters in .env
TOTAL_CLUSTERS=2
```

### Shard Information
Use the `/shardinfo` command to view:
- Current shard and cluster IDs
- Guild count per shard
- Total guilds and users
- Bot latency

## Project Structure

```
discord-bot/
├── src/
│   ├── commands/
│   │   ├── general/
│   │   │   ├── ping.js
│   │   │   ├── help.js
│   │   │   └── shardinfo.js
│   │   ├── info/
│   │   │   └── info.js
│   │   ├── music/
│   │   │   ├── play.js
│   │   │   ├── skip.js
│   │   │   ├── stop.js
│   │   │   ├── queue.js
│   │   │   ├── clear.js
│   │   │   ├── remove.js
│   │   │   ├── shuffle.js
│   │   │   └── nowplaying.js
│   │   └── moderation/
│   │       ├── kick.js
│   │       ├── ban.js
│   │       ├── timeout.js
│   │       ├── untimeout.js
│   │       ├── tempban.js
│   │       ├── voicemute.js
│   │       ├── voiceunmute.js
│   │       ├── modlog.js
│   │       ├── setup.js
│   │       └── automod.js
│   ├── events/
│   │   ├── ready.js
│   │   ├── interactionCreate.js
│   │   └── messageCreate.js
│   ├── utils/
│   │   ├── musicManager.js
│   │   └── databaseManager.js
│   ├── index.js
│   ├── shardManager.js
│   ├── clusterManager.js
│   └── deploy-commands.js
├── data/
│   └── bot.db
├── package.json
├── .env
├── .gitignore
├── install.sh
├── update.sh
├── update.bat
├── update.js
├── run.js
└── README.md
```

## Troubleshooting

### Common Issues

#### Music not working
- Ensure FFmpeg is installed and in your PATH
- Check that the bot has Connect and Speak permissions
- Verify the voice channel is accessible

#### Commands not appearing
- Run `npm run deploy` to register slash commands
- Check that the bot has the "Use Slash Commands" permission
- Ensure the bot is added to your server with proper scopes

#### Database errors
- Check that the `data/` directory exists and is writable
- Verify SQLite is working: `node -e "require('better-sqlite3')"`

#### Auto-Mod not working
- Use `/setup` to configure a modlog channel
- Check that the bot has Manage Messages permission
- Verify auto-mod settings with `/automod view`

#### Sharding/Clustering issues
- Ensure `discord-hybrid-sharding` is installed
- Check that TOTAL_SHARDS and TOTAL_CLUSTERS are set correctly
- Verify all environment variables are properly configured

#### Update issues
- Ensure you're in a git repository
- Check that git and npm are installed
- Verify you have proper permissions to pull from the repository
- If you have local changes, the updater will stash them automatically

### Getting Help

1. Check the console output for error messages
2. Verify your Discord bot token is correct
3. Ensure all required permissions are granted
4. Check that FFmpeg is properly installed
5. Review the environment variables in `.env`
6. Run the updater to ensure you have the latest version

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section above
- Review Discord.js documentation
- Open an issue on GitHub

---

**Note**: This bot template is designed for educational purposes and can be extended with additional features as needed. 