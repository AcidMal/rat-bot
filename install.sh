#!/bin/bash

# Rat Bot Auto-Installation Script
# This script will install all dependencies and set up the bot

echo "🤖 Rat Bot Installation Script"
echo "=============================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
DISCORD_PREFIX=!

# Database Configuration
DATABASE_PATH=data/bot.db

# Logging Configuration
LOG_LEVEL=INFO
EOF
    echo "⚠️ Please edit .env file and add your Discord bot token!"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️ FFmpeg is not installed. Music functionality may not work properly."
    echo "📥 To install FFmpeg:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/download.html"
fi

# Install LavaLink
echo "🎵 Installing LavaLink server..."
chmod +x install_lavalink.sh
./install_lavalink.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎵 To start the bot:"
echo "   source venv/bin/activate"
echo "   python bot.py"
echo ""
echo "🎵 To start LavaLink server (in a separate terminal):"
echo "   ./start_lavalink.sh"
echo ""
echo "📝 Don't forget to:"
echo "   1. Edit .env file with your Discord bot token"
echo "   2. Start LavaLink server before running the bot"
echo "   3. Make sure Java 11+ is installed for LavaLink" 