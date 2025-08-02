#!/bin/bash

# Rat Bot Update Script
# This script updates the bot without requiring a full reinstallation

echo "🔄 Rat Bot Update Script"
echo "======================="
echo

# Check if we're in the right directory
if [ ! -f "bot.py" ]; then
    echo "❌ Please run this script from the bot directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the update script
echo "Running update script..."
python update.py

echo
echo "Update process completed!" 