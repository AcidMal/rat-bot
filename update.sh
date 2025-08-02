#!/bin/bash

echo "🔄 Rat Bot Update Script"
echo "========================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Run the update script
echo "🚀 Starting update process..."
python update.py

echo ""
echo "✅ Update script completed!" 