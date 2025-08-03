# Advanced Discord Bot - Windows Installation Guide

This guide covers Windows-specific installation and usage of the Advanced Discord Bot.

## 🖥️ Windows Requirements

- **Windows 10/11** (Windows Server 2019+ also supported)
- **PowerShell 5.1+** (Windows PowerShell or PowerShell Core)
- **Internet Connection** for downloading dependencies
- **Administrator privileges** (for some installations)

## 🚀 Quick Start (Windows)

### Option 1: Batch File Installation (Recommended)
```cmd
# Download or clone the repository
git clone <repository-url>
cd discord-bot

# Run the installer
install.bat
```

### Option 2: PowerShell Installation
```powershell
# Run PowerShell as Administrator (recommended)
# Navigate to bot directory
cd discord-bot

# Run the installer
.\install.ps1
```

### Option 3: Silent Installation
```powershell
# For automated deployments
.\install.ps1 -Silent -Token "YOUR_BOT_TOKEN" -DatabaseType "json"
```

## 📋 What the Installer Does

The Windows installer automatically:

1. **Checks and installs Python 3.11+**
   - Downloads from python.org if not found
   - Configures PATH automatically
   - Installs pip and venv

2. **Checks and installs Java 17+**
   - Downloads OpenJDK from Adoptium
   - Required for Lavalink music server
   - Configures JAVA_HOME

3. **Installs Git for Windows**
   - Required for updates from GitHub
   - Includes Git Bash and Git GUI

4. **Creates Python Virtual Environment**
   - Isolates bot dependencies
   - Prevents conflicts with system Python

5. **Downloads and installs dependencies**
   - All Python packages from requirements.txt
   - Lavalink.jar for music functionality

6. **Interactive Configuration**
   - Discord bot token input
   - Database selection (MongoDB/JSON)
   - Lavalink settings
   - Web API configuration
   - Sharding options

7. **Creates Windows scripts**
   - start.bat - Start the bot
   - stop.bat - Stop the bot
   - update.bat - Update from GitHub

## 🔧 Windows Management Scripts

### Starting the Bot
```cmd
# Double-click or run from command prompt
start.bat

# Or from PowerShell
.\start.bat
```

### Stopping the Bot
```cmd
# Double-click or run from command prompt
stop.bat

# Or use Ctrl+C in the bot window
```

### Updating the Bot
```cmd
# Update from GitHub
update.bat

# Update without restarting services
update.bat --no-restart

# Backup only (no update)
update.bat --backup-only
```

## 🗂️ Windows File Structure

```
discord-bot/
├── venv/                    # Python virtual environment
├── logs/                    # Log files
│   ├── bot.log             # Bot logs
│   └── lavalink.log        # Lavalink logs
├── data/                   # Database files (if using JSON)
├── backups/                # Configuration backups
├── install.bat             # Batch installer
├── install.ps1             # PowerShell installer
├── start.bat               # Start script
├── stop.bat                # Stop script
├── update.bat              # Update script
├── update.ps1              # PowerShell update script
├── .env                    # Configuration file
└── Lavalink.jar           # Music server
```

## ⚙️ Windows Configuration

### Environment Variables (.env file)
The installer creates a `.env` file with Windows-appropriate settings:

```env
# Windows-specific paths
LOG_FILE=logs\bot.log
JSON_DATABASE_PATH=data\database.json

# Other settings remain the same
DISCORD_TOKEN=your_token_here
DATABASE_TYPE=json
# ... etc
```

### Windows Services (Optional)

To run the bot as a Windows service:

1. **Install NSSM (Non-Sucking Service Manager)**
   ```cmd
   # Download from https://nssm.cc/download
   # Or use Chocolatey
   choco install nssm
   ```

2. **Create the service**
   ```cmd
   # Run as Administrator
   nssm install DiscordBot
   
   # Set executable path
   nssm set DiscordBot Application "C:\path\to\discord-bot\start.bat"
   nssm set DiscordBot AppDirectory "C:\path\to\discord-bot"
   
   # Start the service
   nssm start DiscordBot
   ```

3. **Manage the service**
   ```cmd
   # Stop service
   nssm stop DiscordBot
   
   # Remove service
   nssm remove DiscordBot
   ```

## 🔍 Windows Troubleshooting

### Common Issues

**PowerShell Execution Policy Error**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

# Or for current user only
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python not found after installation**
```cmd
# Restart command prompt/PowerShell
# Or manually add to PATH:
# C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\
# C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\Scripts\
```

**Java not found**
```cmd
# Check if Java is installed
java -version

# If not found, download from:
# https://adoptium.net/temurin/releases/
```

**Bot doesn't start**
- Check `.env` file has valid Discord token
- Ensure virtual environment is activated
- Check logs in `logs\bot.log`

**Lavalink fails to start**
- Ensure Java 17+ is installed
- Check `logs\lavalink.log` for errors
- Verify `application.yml` configuration

**Permission errors**
- Run command prompt as Administrator
- Check antivirus isn't blocking files
- Ensure Python has write permissions

### Viewing Logs

**Real-time log viewing:**
```powershell
# Bot logs
Get-Content logs\bot.log -Tail 50 -Wait

# Lavalink logs
Get-Content logs\lavalink.log -Tail 50 -Wait
```

**Log files location:**
- Bot logs: `logs\bot.log`
- Lavalink logs: `logs\lavalink.log`
- Installation logs: Check PowerShell output

### Performance Optimization

**Windows-specific optimizations:**

1. **Disable Windows Defender real-time scanning** for bot directory (if safe)
2. **Set process priority:**
   ```cmd
   # Start with high priority
   start /high python main.py
   ```
3. **Configure Windows power settings** to "High Performance"
4. **Disable unnecessary Windows services** that might interfere

## 🔧 Development on Windows

### Setting up Development Environment

1. **Install Visual Studio Code**
   ```cmd
   # With Chocolatey
   choco install vscode
   
   # Or download from https://code.visualstudio.com/
   ```

2. **Install Python extension**
   - Open VS Code
   - Install Python extension by Microsoft
   - Select Python interpreter from `venv\Scripts\python.exe`

3. **Configure debugging**
   Create `.vscode\launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Discord Bot",
               "type": "python",
               "request": "launch",
               "program": "main.py",
               "console": "integratedTerminal",
               "python": "${workspaceFolder}\\venv\\Scripts\\python.exe"
           }
       ]
   }
   ```

### Building Executable (Optional)

To create a standalone executable:

```cmd
# Activate virtual environment
venv\Scripts\activate.bat

# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name DiscordBot main.py

# Executable will be in dist\DiscordBot.exe
```

## 📦 Windows Deployment

### Local Network Deployment
1. Copy entire bot folder to target machine
2. Run `install.bat` on target machine
3. Configure `.env` file
4. Run `start.bat`

### Server Deployment
1. Use Windows Server 2019+ or Windows 10/11
2. Install as Windows Service (see above)
3. Configure firewall rules if needed
4. Set up automatic startup

### Docker on Windows
```dockerfile
# Use Windows base image
FROM mcr.microsoft.com/windows/nanoserver:ltsc2022

# Copy bot files
COPY . /app
WORKDIR /app

# Install Python and dependencies
# (Windows container setup)
```

## 🆘 Getting Help

If you encounter issues on Windows:

1. **Check the logs** first (`logs\bot.log`)
2. **Run installer again** - it's safe to re-run
3. **Check antivirus** - some may block Python/Java
4. **Try running as Administrator**
5. **Create GitHub issue** with:
   - Windows version
   - PowerShell version
   - Error messages
   - Log files

## 📞 Windows-Specific Support

For Windows-specific issues:
- Include `systeminfo` output
- Include PowerShell version: `$PSVersionTable`
- Include Python version: `python --version`
- Include Java version: `java -version`

---

**Note:** This bot is primarily designed for Linux servers, but the Windows version provides full functionality for development and testing purposes.