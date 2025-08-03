#!/bin/bash

# Quick fix for missing dependencies
echo "🔧 Quick Fix for Missing Dependencies"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
else
    print_warning "Virtual environment not found"
fi

# Install system dependencies
print_status "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    print_status "Installing from apt..."
    sudo apt-get update
    sudo apt-get install -y python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama python3-psutil
    print_success "System dependencies installed"
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    print_status "Installing from dnf..."
    sudo dnf install -y python3-yarl python3-aiohttp python3-asyncpg python3-dotenv python3-colorama python3-psutil
    print_success "System dependencies installed"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    print_status "Installing from pacman..."
    sudo pacman -S --noconfirm python-yarl python-aiohttp python-asyncpg python-dotenv python-colorama python-psutil
    print_success "System dependencies installed"
else
    print_warning "Could not detect package manager"
fi

# Install Python-only dependencies
print_status "Installing Python-only dependencies..."
pip install --upgrade pip
pip install discord.py==2.3.2 wavelink==2.6.4

# Verify installations
print_status "Verifying installations..."

# Check critical dependencies
critical_deps=("discord" "wavelink" "yarl" "aiohttp" "asyncpg" "dotenv" "colorama" "psutil")

for dep in "${critical_deps[@]}"; do
    if python3 -c "import $dep; print('✅ $dep is installed')" 2>/dev/null; then
        print_success "$dep is installed and working"
    else
        print_error "$dep is missing!"
    fi
done

print_status "Quick fix completed!"
print_status "Try running the bot again: python3 main.py" 