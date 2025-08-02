#!/bin/bash

# Rat Bot Run Script
# This script runs the bot with various options

echo "🤖 Rat Bot Run Script"
echo "===================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check command line arguments
if [ "$1" = "--sharded" ]; then
    echo "Starting bot with automatic sharding..."
    python run_sharded.py
elif [ "$1" = "--shard-manager" ]; then
    echo "Starting shard manager..."
    if [ -n "$2" ]; then
        python shard_manager.py --shards "$2"
    else
        echo "Usage: ./run.sh --shard-manager <number_of_shards>"
        exit 1
    fi
elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage:"
    echo "  ./run.sh                    - Run bot normally (single instance)"
    echo "  ./run.sh --sharded          - Run bot with automatic sharding"
    echo "  ./run.sh --shard-manager N  - Run shard manager with N shards"
    echo "  ./run.sh --help             - Show this help message"
    exit 0
else
    echo "Starting bot normally..."
    python bot.py
fi 