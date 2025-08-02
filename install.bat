@echo off
REM Rat Bot Auto-Installation Script for Windows
REM This script will install all dependencies and set up the bot

echo 🤖 Rat Bot Installation Script
echo ==============================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip and try again.
    pause
    exit /b 1
)

echo ✅ pip found

REM Check if FFmpeg is installed
echo Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  FFmpeg not found. Music functionality requires FFmpeg.
    echo Please install FFmpeg:
    echo   Download from: https://ffmpeg.org/download.html
    echo   Or use chocolatey: choco install ffmpeg
    echo   Or use winget: winget install FFmpeg
    echo.
    set /p continue="Continue without FFmpeg? (y/N): "
    if /i not "%continue%"=="y" (
        echo Installation cancelled. Please install FFmpeg and try again.
        pause
        exit /b 1
    )
) else (
    echo ✅ FFmpeg found
)

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, removing...
    rmdir /s /q venv
)

python -m venv venv
echo ✅ Virtual environment created

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy example.env .env
    echo ✅ .env file created from template
    echo ⚠️  Please edit .env file and add your Discord bot token!
) else (
    echo ✅ .env file already exists
)

REM Create database directory
echo Setting up database...
if not exist data mkdir data
type nul > data\bot.db

REM Set up database
echo Initializing database...
python -c "
import sqlite3
import os

# Create database connection
conn = sqlite3.connect('data/bot.db')
cursor = conn.cursor()

# Create mod_logs table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS mod_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        moderator_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create user_warnings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_warnings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        moderator_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create custom_commands table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guild_id INTEGER NOT NULL,
        command_name TEXT NOT NULL,
        response TEXT NOT NULL,
        created_by INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create server_settings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS server_settings (
        guild_id INTEGER PRIMARY KEY,
        mod_log_channel INTEGER,
        welcome_channel INTEGER,
        welcome_message TEXT,
        prefix TEXT DEFAULT '!',
        auto_role INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create user_stats table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER NOT NULL,
        guild_id INTEGER NOT NULL,
        messages_sent INTEGER DEFAULT 0,
        commands_used INTEGER DEFAULT 0,
        last_message DATETIME,
        joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, guild_id)
    )
''')

conn.commit()
conn.close()
print('✅ Database initialized successfully')
"

REM Create logs directory
if not exist logs mkdir logs

echo.
echo 🎉 Installation completed successfully!
echo.
echo Next steps:
echo 1. Edit the .env file and add your Discord bot token
echo 2. Run the bot with: run.bat
echo 3. Or manually with: venv\Scripts\activate.bat ^&^& python bot.py
echo.
echo For help, check the README.md file
pause 