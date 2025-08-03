#!/bin/bash

# Advanced Discord Bot Start Script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_status "Please run ./install.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_status "Please run ./install.sh or copy env.example to .env"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if Lavalink should be started
if [ -f "Lavalink-latest.jar" ] && command -v java &> /dev/null; then
    if ! pgrep -f "java.*Lavalink-latest.jar" > /dev/null; then
        print_status "Starting Lavalink server..."
        mkdir -p logs
        nohup java -jar Lavalink-latest.jar > logs/lavalink.log 2>&1 &
        sleep 5
        print_success "Lavalink started"
    else
        print_status "Lavalink is already running"
    fi
elif [ -f "Lavalink.jar" ] && command -v java &> /dev/null; then
    # Fallback to old filename for compatibility
    if ! pgrep -f "java.*Lavalink.jar" > /dev/null; then
        print_status "Starting Lavalink server (legacy)..."
        mkdir -p logs
        nohup java -jar Lavalink.jar > logs/lavalink.log 2>&1 &
        sleep 5
        print_success "Lavalink started"
    else
        print_status "Lavalink is already running"
    fi
else
    print_error "Lavalink not found or Java not installed"
    print_status "Music features will not work. Please run ./install.sh"
fi

# Start the bot
print_status "Starting Discord Bot..."
python main.py