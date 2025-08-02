@echo off
echo 🤖 Rat Bot Installation Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher first.
    echo Visit: https://python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo ⬆️ Upgrading pip...
python -m pip install --upgrade pip

REM Install Python dependencies
echo 📥 Installing Python dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file...
    (
    echo # Discord Bot Configuration
    echo DISCORD_TOKEN=your_discord_token_here
    echo DISCORD_PREFIX=!
    echo.
    echo # Database Configuration
    echo DATABASE_PATH=data/bot.db
    echo.
    echo # Logging Configuration
    echo LOG_LEVEL=INFO
    ) > .env
    echo ⚠️ Please edit .env file and add your Discord bot token!
)

REM Create data directory
echo 📁 Creating data directory...
if not exist "data" mkdir data

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️ FFmpeg is not installed. Music functionality may not work properly.
    echo 📥 To install FFmpeg:
    echo    Download from https://ffmpeg.org/download.html
)

REM Install LavaLink
echo 🎵 Installing LavaLink server...
call install_lavalink.bat

echo.
echo ✅ Installation complete!
echo.
echo 🎵 To start the bot:
echo    venv\Scripts\activate.bat
echo    python bot.py
echo.
echo 🎵 To start LavaLink server ^(in a separate terminal^):
echo    start_lavalink.bat
echo.
echo 📝 Don't forget to:
echo    1. Edit .env file with your Discord bot token
echo    2. Start LavaLink server before running the bot
echo    3. Make sure Java 11+ is installed for LavaLink
pause 