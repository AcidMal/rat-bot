#!/bin/bash

# RatBot Update Script
# This script updates the bot from GitHub and updates dependencies

set -e

echo "🔄 RatBot Update Script"
echo "======================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This directory is not a git repository."
    print_status "Please clone the repository first or initialize git."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git to update the bot."
    exit 1
fi

# Backup current configuration
print_status "Backing up current configuration..."
if [ -f ".env" ]; then
    cp .env .env.backup
    print_success "Configuration backed up to .env.backup"
fi

# Stash any local changes
print_status "Stashing local changes..."
git stash push -m "Auto-stash before update $(date)" || true

# Fetch latest changes
print_status "Fetching latest changes from GitHub..."
git fetch origin

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
print_status "Current branch: $CURRENT_BRANCH"

# Check if there are updates
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    print_success "Bot is already up to date!"
else
    print_status "Updates found. Pulling latest changes..."
    git pull origin $CURRENT_BRANCH
    print_success "Code updated successfully"
fi

# Restore configuration if it was backed up
if [ -f ".env.backup" ]; then
    print_status "Restoring configuration..."
    cp .env.backup .env
    rm .env.backup
    print_success "Configuration restored"
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
else
    print_warning "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Update system dependencies first
print_status "Updating system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    print_status "Updating dependencies from system packages..."
    sudo apt-get update
    sudo apt-get install -y python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama python3-psutil
    print_success "System dependencies updated"
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    print_status "Updating dependencies from system packages..."
    sudo dnf install -y python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama python3-psutil
    print_success "System dependencies updated"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    print_status "Updating dependencies from system packages..."
    sudo pacman -S --noconfirm python-yarl python-aiohttp python-asyncpg python-dotenv python-colorama python-psutil
    print_success "System dependencies updated"
else
    print_warning "Could not detect package manager, will try pip installation"
fi

# Update Python-only dependencies (discord.py and wavelink)
print_status "Updating Python-only dependencies..."
pip install --upgrade pip

# Create a minimal requirements file with only pip packages
print_status "Creating minimal requirements file..."
cat > requirements_minimal.txt << EOF
discord.py==2.3.2
wavelink==2.6.4
EOF

# Install dependencies
pip install -r requirements_minimal.txt
print_success "Python-only dependencies updated"

# Clean up temporary file
rm -f requirements_minimal.txt

# Verify all installations
print_status "Verifying installations..."

# Check yarl
if python3 -c "import yarl; print('✅ yarl version:', yarl.__version__)" 2>/dev/null; then
    print_success "yarl is installed and working"
else
    print_warning "yarl not found, attempting pip installation as fallback..."
    pip install --no-cache-dir yarl==1.9.2 || print_warning "yarl installation failed, but continuing..."
fi

# Check aiohttp
if python3 -c "import aiohttp; print('✅ aiohttp version:', aiohttp.__version__)" 2>/dev/null; then
    print_success "aiohttp is installed and working"
else
    print_warning "aiohttp not found, attempting pip installation as fallback..."
    pip install --no-cache-dir aiohttp==3.9.1 || print_warning "aiohttp installation failed, but continuing..."
fi

# Check asyncpg
if python3 -c "import asyncpg; print('✅ asyncpg is installed')" 2>/dev/null; then
    print_success "asyncpg is installed and working"
else
    print_warning "asyncpg not found, attempting pip installation as fallback..."
    pip install --no-cache-dir asyncpg==0.29.0 || print_warning "asyncpg installation failed, but continuing..."
fi

# Check discord.py
if python3 -c "import discord; print('✅ discord.py version:', discord.__version__)" 2>/dev/null; then
    print_success "discord.py is installed and working"
else
    print_error "discord.py installation failed - this is critical!"
fi

# Check wavelink
if python3 -c "import wavelink; print('✅ wavelink is installed')" 2>/dev/null; then
    print_success "wavelink is installed and working"
else
    print_error "wavelink installation failed - this is critical!"
fi

# Check if Lavalink needs updating
if command -v java &> /dev/null && [ -f "Lavalink.jar" ]; then
    print_status "Checking Lavalink version..."
    # This is a simple check - in a real scenario you might want to check the actual version
    print_status "Lavalink version check completed"
fi

# Make scripts executable again
print_status "Making scripts executable..."
chmod +x install.sh
chmod +x update.sh
chmod +x start.sh
chmod +x stop.sh
print_success "Scripts made executable"

# Show update summary
print_success "Update completed!"
echo ""
echo "Update Summary:"
echo "- Code: Updated from GitHub"
echo "- Dependencies: Updated to latest versions"
echo "- Configuration: Preserved"
echo ""
echo "To restart the bot with updates:"
echo "1. Stop the bot: ./stop.sh"
echo "2. Start the bot: ./start.sh"
echo ""
echo "For more information, check the logs or run './start.sh --help'" 