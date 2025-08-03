#!/bin/bash

# Advanced Discord Bot Stop Script

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

print_status "Stopping Discord Bot and Lavalink..."

# Stop bot process
if pgrep -f "python.*main.py" > /dev/null; then
    print_status "Stopping Discord Bot..."
    pkill -f "python.*main.py"
    sleep 2
    
    if pgrep -f "python.*main.py" > /dev/null; then
        print_status "Force killing Discord Bot..."
        pkill -9 -f "python.*main.py"
    fi
    
    print_success "Discord Bot stopped"
else
    print_status "Discord Bot is not running"
fi

# Stop Lavalink process (check both new and old filenames)
if pgrep -f "java.*Lavalink-latest.jar" > /dev/null; then
    print_status "Stopping Lavalink..."
    pkill -f "java.*Lavalink-latest.jar"
    sleep 3
    
    if pgrep -f "java.*Lavalink-latest.jar" > /dev/null; then
        print_status "Force killing Lavalink..."
        pkill -9 -f "java.*Lavalink-latest.jar"
    fi
    
    print_success "Lavalink stopped"
elif pgrep -f "java.*Lavalink.jar" > /dev/null; then
    print_status "Stopping Lavalink (legacy)..."
    pkill -f "java.*Lavalink.jar"
    sleep 3
    
    if pgrep -f "java.*Lavalink.jar" > /dev/null; then
        print_status "Force killing Lavalink..."
        pkill -9 -f "java.*Lavalink.jar"
    fi
    
    print_success "Lavalink stopped"
else
    print_status "Lavalink is not running"
fi

print_success "All processes stopped"