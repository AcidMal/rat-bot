#!/bin/bash

# Rat Bot Auto-Installation Script
# This script will install all dependencies and set up the bot

echo "🤖 Rat Bot Installation Script"
echo "=============================="

# Check if Python 3.8+ is installed
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [[ -z "$python_version" ]]; then
    echo "❌ Python 3.8+ is required but not found."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

required_version="3.8"
if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo "❌ Python $python_version found, but Python 3.8+ is required."
    exit 1
fi

echo "✅ Python $python_version found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip3 found"

# Check if FFmpeg is installed
echo "Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg not found. Music functionality requires FFmpeg."
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  CentOS/RHEL: sudo yum install ffmpeg"
    echo ""
    read -p "Continue without FFmpeg? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled. Please install FFmpeg and try again."
        exit 1
    fi
else
    echo "✅ FFmpeg found"
fi

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, removing..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp example.env .env
    echo "✅ .env file created from template"
    echo "⚠️  Please edit .env file and add your Discord bot token!"
else
    echo "✅ .env file already exists"
fi

# Create database directory
echo "Setting up database..."
mkdir -p data
touch data/bot.db

# Set up database
echo "Initializing database..."
python3 -c "
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

# Create logs directory
mkdir -p logs

# Make the script executable
chmod +x run.sh

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file and add your Discord bot token"
echo "2. Run the bot with: ./run.sh"
echo "3. Or manually with: source venv/bin/activate && python bot.py"
echo ""
echo "For help, check the README.md file" 