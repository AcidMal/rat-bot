#!/bin/bash

echo "🔧 Installing Missing Dependencies"
echo "=================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install system dependencies
echo "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    sudo apt-get update
    sudo apt-get install -y python3-psutil python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama
    echo "✅ System dependencies installed"
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    sudo dnf install -y python3-psutil python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama
    echo "✅ System dependencies installed"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    sudo pacman -S --noconfirm python-psutil python-yarl python-aiohttp python-asyncpg python-dotenv python-colorama
    echo "✅ System dependencies installed"
else
    echo "⚠️ Could not detect package manager, trying pip installation"
    pip install psutil yarl aiohttp asyncpg python-dotenv colorama
fi

# Install Python-only dependencies
echo "Installing Python-only dependencies..."
pip install discord.py==2.3.2 wavelink==2.6.4

# Verify installations
echo "Verifying installations..."
python3 -c "import psutil; print('✅ psutil installed')" 2>/dev/null || echo "❌ psutil missing"
python3 -c "import discord; print('✅ discord.py installed')" 2>/dev/null || echo "❌ discord.py missing"
python3 -c "import wavelink; print('✅ wavelink installed')" 2>/dev/null || echo "❌ wavelink missing"

echo "Installation completed!" 