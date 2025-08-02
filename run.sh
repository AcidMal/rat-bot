#!/bin/bash

# Rat Bot Run Script
# This script runs the bot with various options

# Function to show help
show_help() {
    echo "🤖 Rat Bot Run Script"
    echo "====================="
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --sharded          Run with automatic sharding"
    echo "  --shard-manager N   Run with manual sharding (N = number of shards)"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Single instance (default)"
    echo "  $0 --sharded       # Automatic sharding"
    echo "  $0 --shard-manager 4  # Manual sharding with 4 shards"
    echo ""
    echo "🎵 Note: LavaLink server starts automatically with the bot!"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Parse command line arguments
case "${1:-}" in
    --sharded)
        echo "🚀 Starting bot with automatic sharding..."
        python run_sharded.py
        ;;
    --shard-manager)
        if [ -z "$2" ]; then
            echo "❌ Please specify number of shards: --shard-manager N"
            exit 1
        fi
        echo "🚀 Starting bot with manual sharding ($2 shards)..."
        python shard_manager.py --shards "$2"
        ;;
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        echo "🚀 Starting bot (single instance)..."
        echo "🎵 LavaLink server will start automatically!"
        python bot.py
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_help
        exit 1
        ;;
esac 