#!/bin/bash

# RatBot Start Script
# This script starts the bot with proper environment setup

set -e

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

# Show help
show_help() {
    echo "🐀 RatBot Start Script"
    echo "======================"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -d, --daemon   Run in daemon mode (background)"
    echo "  -v, --verbose  Enable verbose logging"
    echo "  --no-lavalink  Don't start Lavalink server"
    echo ""
    echo "Examples:"
    echo "  $0              # Start bot normally"
    echo "  $0 -d           # Start bot in background"
    echo "  $0 -v           # Start with verbose logging"
    echo "  $0 --no-lavalink # Start without Lavalink"
}

# Parse command line arguments
DAEMON_MODE=false
VERBOSE=false
NO_LAVALINK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -d|--daemon)
            DAEMON_MODE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-lavalink)
            NO_LAVALINK=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🐀 RatBot Start Script"
echo "======================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please run install.sh first or create .env file manually."
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    print_error "main.py not found. Please make sure you're in the correct directory."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Check if bot is already running
if [ -f "bot.pid" ]; then
    PID=$(cat bot.pid)
    if ps -p $PID > /dev/null 2>&1; then
        print_warning "Bot is already running (PID: $PID)"
        echo "To stop the bot, run: ./stop.sh"
        exit 1
    else
        print_status "Removing stale PID file..."
        rm bot.pid
    fi
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Set log level
if [ "$VERBOSE" = true ]; then
    export LOG_LEVEL=DEBUG
    print_status "Verbose logging enabled"
fi

# Start Lavalink if not disabled
if [ "$NO_LAVALINK" = false ]; then
    if command -v java &> /dev/null && [ -f "Lavalink.jar" ]; then
        print_status "Starting Lavalink server..."
        java -jar Lavalink.jar > logs/lavalink.log 2>&1 &
        LAVALINK_PID=$!
        echo $LAVALINK_PID > lavalink.pid
        print_success "Lavalink started (PID: $LAVALINK_PID)"
        
        # Wait for Lavalink to start
        print_status "Waiting for Lavalink to start..."
        sleep 5
    else
        print_warning "Lavalink not available. Music features will not work."
    fi
else
    print_status "Skipping Lavalink startup"
fi

# Start the bot
print_status "Starting RatBot..."

if [ "$DAEMON_MODE" = true ]; then
    # Run in background
    nohup python main.py > logs/bot.log 2>&1 &
    BOT_PID=$!
    echo $BOT_PID > bot.pid
    print_success "Bot started in daemon mode (PID: $BOT_PID)"
    echo "Logs are being written to logs/bot.log"
    echo "To stop the bot, run: ./stop.sh"
else
    # Run in foreground
    print_status "Starting bot in foreground..."
    print_status "Press Ctrl+C to stop the bot"
    echo ""
    python main.py
fi 