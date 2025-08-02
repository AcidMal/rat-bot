#!/bin/bash

echo "🎵 Starting LavaLink Server..."

if [ ! -d "lavalink" ]; then
    echo "❌ LavaLink not installed. Run install_lavalink.sh first."
    exit 1
fi

cd lavalink

if [ ! -f "Lavalink.jar" ]; then
    echo "❌ LavaLink.jar not found. Run install_lavalink.sh first."
    exit 1
fi

echo "🚀 Starting LavaLink server on port 2333..."
echo "📝 Press Ctrl+C to stop the server"
echo ""

java -jar Lavalink.jar 