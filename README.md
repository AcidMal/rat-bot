# Rat Bot 🤖

A feature-rich Discord bot built with Discord.py, featuring moderation tools, music playback, custom commands, and more!

## ✨ Features

- **Moderation System** - Kick, ban, mute, warn users with logging
- **Music System** - High-quality audio playback using LavaLink
- **Custom Commands** - Server-specific custom commands
- **User Statistics** - Track user activity and engagement
- **Server Settings** - Configurable welcome messages, auto-roles, and more
- **Hybrid Commands** - Both slash commands and legacy prefix commands
- **Sharding Support** - Handle large numbers of servers efficiently
- **Database Integration** - Persistent data storage with SQLite
- **Auto-Installation** - Easy setup scripts for all platforms
- **Auto-LavaLink** - LavaLink server starts automatically with the bot

## 🎵 Music System

The bot uses **LavaLink** for high-quality audio processing:

### **Why LavaLink?**
- ✅ **Better Performance** - Dedicated audio server handles all processing
- ✅ **No SSL Issues** - LavaLink handles YouTube API changes automatically
- ✅ **Multiple Sources** - YouTube, SoundCloud, Bandcamp, Twitch, Vimeo
- ✅ **Higher Quality** - Better audio quality and stability
- ✅ **No Authentication** - No sign-in prompts or certificate issues
- ✅ **Auto-Start** - LavaLink server starts automatically with the bot

### **Music Commands**
| Command | Description |
|---------|-------------|
| `/join` | Join a voice channel |
| `/play <song>` | Play a song (URL or search) |
| `/pause` | Pause current song |
| `/resume` | Resume paused song |
| `/skip` | Skip current song |
| `/stop` | Stop and clear queue |
| `/queue` | Show music queue |
| `/now` | Show currently playing |
| `/volume <0-100>` | Set volume |
| `/shuffle` | Shuffle queue |
| `/clear` | Clear queue |
| `/remove <position>` | Remove track from queue |
| `/leave` | Leave voice channel |
| `/lavalink` | Check LavaLink server status |

## 🚀 Quick Start

### **Prerequisites**
- Python 3.8 or higher
- Java 11 or higher (for LavaLink)
- FFmpeg (optional, for additional audio formats)

### **Installation**

#### **Linux/macOS:**
```bash
# Clone the repository
git clone <repository-url>
cd rat-bot

# Run installation script
chmod +x install.sh
./install.sh
```

#### **Windows:**
```cmd
# Clone the repository
git clone <repository-url>
cd rat-bot

# Run installation script
install.bat
```

### **Setup**

1. **Edit `.env` file** with your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_token_here
   DISCORD_PREFIX=!
   ```

2. **Start the bot** (LavaLink starts automatically):
   ```bash
   # Linux/macOS
   ./run.sh
   
   # Windows
   run.bat
   ```

That's it! The bot will automatically start the LavaLink server when it connects to Discord.

## 📋 Manual Installation

If you prefer manual installation:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install LavaLink:**
   ```bash
   # Linux/macOS
   ./install_lavalink.sh
   
   # Windows
   install_lavalink.bat
   ```

3. **Configure and run the bot:**
   ```bash
   # Edit .env file with your token
   python bot.py
   ```

## 🎵 LavaLink Configuration

The bot automatically connects to LavaLink with these settings:
- **Host:** 127.0.0.1
- **Port:** 2333
- **Password:** youshallnotpass

### **LavaLink Features:**
- **YouTube Search** - Search and play YouTube videos
- **Multiple Sources** - Support for various audio platforms
- **High Quality** - Better audio processing than direct downloads
- **No Authentication** - No SSL certificate or login issues
- **Auto-Reconnect** - Automatic reconnection on disconnection
- **Auto-Start** - Server starts automatically with the bot

## 🔧 Configuration

### **Environment Variables (.env)**
```env
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
DISCORD_PREFIX=!

# Database Configuration
DATABASE_PATH=data/bot.db

# Logging Configuration
LOG_LEVEL=INFO
```

### **Bot Permissions**
The bot needs these permissions:
- **Send Messages**
- **Use Slash Commands**
- **Connect** (for voice)
- **Speak** (for voice)
- **Manage Messages** (for moderation)
- **Kick Members** (for moderation)
- **Ban Members** (for moderation)

## 📁 Project Structure

```
rat-bot/
├── bot.py                 # Main bot file
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── cogs/                 # Bot cogs (modules)
│   ├── admin.py         # Admin commands
│   ├── moderation.py    # Moderation commands
│   ├── music.py         # Music commands (LavaLink)
│   ├── fun.py           # Fun commands
│   └── utility.py       # Utility commands
├── data/                 # Database and data files
├── lavalink/            # LavaLink server files
│   ├── Lavalink.jar     # LavaLink server
│   └── application.yml  # LavaLink configuration
├── install.sh           # Linux/macOS installation
├── install.bat          # Windows installation
├── install_lavalink.sh  # LavaLink installation (Linux/macOS)
├── install_lavalink.bat # LavaLink installation (Windows)
├── run.sh               # Run bot (Linux/macOS)
├── run.bat              # Run bot (Windows)
├── update.py            # Update script
├── update.sh            # Update script (Linux/macOS)
├── update.bat           # Update script (Windows)
└── README.md            # This file
```

## 🎵 Music System Details

### **LavaLink Integration**
The bot uses LavaLink for all audio processing, which provides:
- **Better Performance** - Dedicated audio server
- **No SSL Issues** - Handles YouTube API changes automatically
- **Multiple Sources** - YouTube, SoundCloud, Bandcamp, Twitch, Vimeo
- **Higher Quality** - Better audio processing than direct downloads
- **Auto-Reconnect** - Automatic reconnection on disconnection
- **Auto-Start** - Server starts automatically with the bot

### **Install Java**
LavaLink requires Java 11 or higher:

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

**macOS:**
```bash
brew install openjdk@11
```

**Windows:**
Download from [Adoptium](https://adoptium.net/)

### **LavaLink Server**
The LavaLink server runs automatically when the bot starts and handles all audio processing. The bot connects to it via WebSocket.

## 🔄 Update System

### **Automatic Updates**
```bash
# Linux/macOS
./update.sh

# Windows
update.bat
```

### **Manual Updates**
```bash
# Update dependencies
pip install -r requirements.txt

# Update LavaLink (if needed)
cd lavalink
wget -O Lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **LavaLink Connection Issues**
- **Problem:** Bot can't connect to LavaLink
- **Solution:** Make sure Java 11+ is installed (`java -version`)
- **Solution:** Check if LavaLink is installed (`ls lavalink/`)

#### **Music Not Playing**
- **Problem:** Music commands don't work
- **Solution:** Check bot has voice permissions
- **Solution:** Verify FFmpeg is installed (optional)
- **Solution:** Use `/lavalink` command to check server status

#### **Java Issues**
- **Problem:** LavaLink won't start
- **Solution:** Install Java 11 or higher
- **Solution:** Check Java version (`java -version`)

#### **Bot Permissions**
- **Problem:** Bot can't join voice channels
- **Solution:** Give bot "Connect" and "Speak" permissions
- **Solution:** Check bot role hierarchy

### **Logs**
Check the console output for error messages. The bot will show connection status and any issues.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Discord.py** - The Discord API wrapper
- **LavaLink** - The audio server
- **SQLite** - Database engine
- **FFmpeg** - Audio processing

---

**🎵 Enjoy your music bot with auto-starting LavaLink!** 