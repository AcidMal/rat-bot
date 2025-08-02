#!/bin/bash

echo "🎵 Installing LavaLink Server..."

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "❌ Java is not installed. Please install Java 11 or higher first."
    echo "Visit: https://adoptium.net/ or use your system's package manager"
    exit 1
fi

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
if [ "$JAVA_VERSION" -lt 11 ]; then
    echo "❌ Java version $JAVA_VERSION detected. LavaLink requires Java 11 or higher."
    exit 1
fi

echo "✅ Java $JAVA_VERSION detected"

# Create LavaLink directory
mkdir -p lavalink
cd lavalink

# Download LavaLink server
echo "📥 Downloading LavaLink server..."
wget -O Lavalink.jar https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar

if [ ! -f "Lavalink.jar" ]; then
    echo "❌ Failed to download LavaLink server"
    exit 1
fi

# Create application.yml configuration
echo "⚙️ Creating LavaLink configuration..."
cat > application.yml << 'EOF'
server:
  port: 2333
  address: 127.0.0.1
lavalink:
  server:
    password: "youshallnotpass"
    sources:
      youtube: true
      bandcamp: true
      soundcloud: true
      twitch: true
      vimeo: true
      http: true
      local: false
    bufferDurationMs: 400
    youtubeSearchEnabled: true
    soundcloudSearchEnabled: true
    gc-warnings: true

metrics:
  prometheus:
    enabled: false
    endpoint: /metrics

sentry:
  dsn: ""
  environment: ""

logging:
  file:
    max-history: 30
    max-size: 1GB
  path: ./logs/

  level:
    root: INFO
    lavalink: INFO
EOF

echo "✅ LavaLink installation complete!"
echo ""
echo "🎵 To start LavaLink server, run:"
echo "   cd lavalink && java -jar Lavalink.jar"
echo ""
echo "📝 The bot will automatically connect to LavaLink on startup."
echo "🔧 Configuration:"
echo "   - Port: 2333"
echo "   - Password: youshallnotpass"
echo "   - Address: 127.0.0.1" 