#!/bin/bash

# RatBot Stop Script
# This script safely stops the bot and Lavalink server

set -e

echo "🛑 RatBot Stop Script"
echo "====================="

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

# Function to stop a process by PID file
stop_process() {
    local pid_file=$1
    local process_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null 2>&1; then
            print_status "Stopping $process_name (PID: $pid)..."
            kill $pid
            
            # Wait for process to stop
            local count=0
            while ps -p $pid > /dev/null 2>&1 && [ $count -lt 10 ]; do
                sleep 1
                count=$((count + 1))
            done
            
            if ps -p $pid > /dev/null 2>&1; then
                print_warning "$process_name didn't stop gracefully, force killing..."
                kill -9 $pid
                sleep 1
            fi
            
            if ! ps -p $pid > /dev/null 2>&1; then
                print_success "$process_name stopped successfully"
                rm -f "$pid_file"
            else
                print_error "Failed to stop $process_name"
            fi
        else
            print_warning "$process_name is not running (stale PID file)"
            rm -f "$pid_file"
        fi
    else
        print_status "$process_name PID file not found"
    fi
}

# Stop the bot
print_status "Stopping RatBot..."
stop_process "bot.pid" "RatBot"

# Stop Lavalink
print_status "Stopping Lavalink server..."
stop_process "lavalink.pid" "Lavalink"

# Check for any remaining Python processes
print_status "Checking for remaining processes..."
PYTHON_PROCESSES=$(ps aux | grep "python main.py" | grep -v grep | awk '{print $2}')
if [ ! -z "$PYTHON_PROCESSES" ]; then
    print_warning "Found remaining Python processes: $PYTHON_PROCESSES"
    echo "These processes will be terminated..."
    echo $PYTHON_PROCESSES | xargs kill -9 2>/dev/null || true
fi

# Check for any remaining Java processes (Lavalink)
JAVA_PROCESSES=$(ps aux | grep "java -jar Lavalink.jar" | grep -v grep | awk '{print $2}')
if [ ! -z "$JAVA_PROCESSES" ]; then
    print_warning "Found remaining Java processes: $JAVA_PROCESSES"
    echo "These processes will be terminated..."
    echo $JAVA_PROCESSES | xargs kill -9 2>/dev/null || true
fi

# Clean up PID files
rm -f bot.pid lavalink.pid

print_success "All processes stopped successfully!"
echo ""
echo "Summary:"
echo "- RatBot: Stopped"
echo "- Lavalink: Stopped"
echo "- PID files: Cleaned up"
echo ""
echo "To start the bot again, run: ./start.sh" 