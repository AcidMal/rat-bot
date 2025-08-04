#!/bin/bash

# Advanced Discord Bot Installation Script
# Supports Ubuntu/Debian, CentOS/RHEL/Fedora, and Arch Linux

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables
PYTHON_VERSION="3.9"
JAVA_VERSION="17"
LAVALINK_VERSION="4.0.8"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  Advanced Discord Bot Installer              ║${NC}"
    echo -e "${PURPLE}║                     Interactive Setup                        ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

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

print_question() {
    echo -e "${CYAN}[QUESTION]${NC} $1"
}

# Function to detect OS
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/redhat-release ]; then
        OS="CentOS"
        VER=$(cat /etc/redhat-release | grep -oE '[0-9]+\.[0-9]+')
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    print_status "Detected OS: $OS $VER"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root!"
        print_status "Run as a regular user with sudo privileges."
        exit 1
    fi
}

# Function to check sudo access
check_sudo() {
    if ! sudo -n true 2>/dev/null; then
        print_status "This script requires sudo privileges for system package installation."
        print_status "You may be prompted for your password."
        sudo -v
    fi
}

# Function to update system packages
update_system() {
    print_status "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -y
        sudo apt-get upgrade -y
    elif command -v dnf &> /dev/null; then
        sudo dnf update -y
    elif command -v yum &> /dev/null; then
        sudo yum update -y
    elif command -v pacman &> /dev/null; then
        sudo pacman -Syu --noconfirm
    else
        print_warning "Could not detect package manager. Skipping system update."
    fi
    
    print_success "System packages updated"
}

# Function to install Python
install_python() {
    print_status "Installing Python ${PYTHON_VERSION}..."
    
    if command -v python3 &> /dev/null; then
        CURRENT_PYTHON=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ $(echo "$CURRENT_PYTHON >= $PYTHON_VERSION" | bc -l 2>/dev/null || echo "1") -eq 1 ]]; then
            print_success "Python $CURRENT_PYTHON is already installed"
            return
        fi
    fi
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y python3 python3-pip python3-venv python3-dev build-essential libssl-dev libffi-dev ffmpeg
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip python3-venv python3-devel gcc openssl-devel libffi-devel ffmpeg
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip python3-venv python3-devel gcc openssl-devel libffi-devel ffmpeg
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python python-pip base-devel ffmpeg
    else
        print_error "Could not install Python. Please install Python ${PYTHON_VERSION}+ manually."
        exit 1
    fi
    
    print_success "Python installed successfully"
}

# Function to install Java (for Lavalink)
install_java() {
    print_status "Installing Java ${JAVA_VERSION}..."
    
    if command -v java &> /dev/null; then
        JAVA_VER=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2 | cut -d'.' -f1)
        if [ "$JAVA_VER" -ge "$JAVA_VERSION" ] 2>/dev/null; then
            print_success "Java $JAVA_VER is already installed"
            return
        fi
    fi
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y openjdk-${JAVA_VERSION}-jdk
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y java-${JAVA_VERSION}-openjdk java-${JAVA_VERSION}-openjdk-devel
    elif command -v yum &> /dev/null; then
        sudo yum install -y java-${JAVA_VERSION}-openjdk java-${JAVA_VERSION}-openjdk-devel
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm jdk${JAVA_VERSION}-openjdk
    fi
    
    print_success "Java installed successfully"
}

# Function to install MongoDB
install_mongodb() {
    print_status "Installing MongoDB..."
    
    if command -v mongod &> /dev/null; then
        print_success "MongoDB is already installed"
        return
    fi
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        curl -fsSL https://pgp.mongodb.com/server-7.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -cs)/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
        sudo apt-get update
        sudo apt-get install -y mongodb-org
        
        # Start and enable MongoDB
        sudo systemctl start mongod
        sudo systemctl enable mongod
        
    elif command -v dnf &> /dev/null; then
        # Fedora
        cat <<EOF | sudo tee /etc/yum.repos.d/mongodb-org-7.0.repo
[mongodb-org-7.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/redhat/\$releasever/mongodb-org/7.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-7.0.asc
EOF
        sudo dnf install -y mongodb-org
        sudo systemctl start mongod
        sudo systemctl enable mongod
        
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm mongodb-bin
        sudo systemctl start mongodb
        sudo systemctl enable mongodb
    else
        print_warning "Could not install MongoDB automatically. Please install it manually."
        return
    fi
    
    print_success "MongoDB installed and started"
}

# Function to install Redis
install_redis() {
    print_status "Installing Redis..."
    
    if command -v redis-server &> /dev/null; then
        print_success "Redis is already installed"
        return
    fi
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y redis-server
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y redis
        sudo systemctl start redis
        sudo systemctl enable redis
    elif command -v yum &> /dev/null; then
        sudo yum install -y redis
        sudo systemctl start redis
        sudo systemctl enable redis
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm redis
        sudo systemctl start redis
        sudo systemctl enable redis
    fi
    
    print_success "Redis installed and started"
}

# Function to download Lavalink and plugins
download_lavalink() {
    print_status "Setting up Lavalink ${LAVALINK_VERSION} music server..."
    
    if [ -f "Lavalink-latest.jar" ]; then
        print_success "Lavalink-latest.jar already exists"
    else
        LAVALINK_URL="https://github.com/lavalink-devs/Lavalink/releases/download/${LAVALINK_VERSION}/Lavalink.jar"
        
        if command -v curl &> /dev/null; then
            curl -L -o Lavalink-latest.jar "$LAVALINK_URL"
        elif command -v wget &> /dev/null; then
            wget -O Lavalink-latest.jar "$LAVALINK_URL"
        else
            print_error "Neither curl nor wget found. Please install one of them."
            exit 1
        fi
        
        if [ -f "Lavalink-latest.jar" ]; then
            print_success "Lavalink downloaded successfully"
        else
            print_error "Failed to download Lavalink"
            exit 1
        fi
    fi
    
    # Create plugins directory
    print_status "Setting up Lavalink plugins..."
    mkdir -p plugins
    
    # Download LavaSrc plugin
    if [ ! -f "plugins/lavasrc-plugin-4.2.0.jar" ]; then
        print_status "Downloading LavaSrc plugin..."
        LAVASRC_URL="https://maven.topi.wtf/releases/com/github/topi314/lavasrc/lavasrc-plugin/4.2.0/lavasrc-plugin-4.2.0.jar"
        
        if command -v curl &> /dev/null; then
            curl -L -o plugins/lavasrc-plugin-4.2.0.jar "$LAVASRC_URL"
        elif command -v wget &> /dev/null; then
            wget -O plugins/lavasrc-plugin-4.2.0.jar "$LAVASRC_URL"
        fi
        
        if [ -f "plugins/lavasrc-plugin-4.2.0.jar" ]; then
            print_success "LavaSrc plugin downloaded"
        else
            print_warning "Failed to download LavaSrc plugin"
        fi
    fi
    
    # Download LavaSearch plugin
    if [ ! -f "plugins/lavasearch-plugin-1.0.0.jar" ]; then
        print_status "Downloading LavaSearch plugin..."
        LAVASEARCH_URL="https://maven.topi.wtf/releases/com/github/topi314/lavasearch/lavasearch-plugin/1.0.0/lavasearch-plugin-1.0.0.jar"
        
        if command -v curl &> /dev/null; then
            curl -L -o plugins/lavasearch-plugin-1.0.0.jar "$LAVASEARCH_URL"
        elif command -v wget &> /dev/null; then
            wget -O plugins/lavasearch-plugin-1.0.0.jar "$LAVASEARCH_URL"
        fi
        
        if [ -f "plugins/lavasearch-plugin-1.0.0.jar" ]; then
            print_success "LavaSearch plugin downloaded"
        else
            print_warning "Failed to download LavaSearch plugin"
        fi
    fi
}

# Function to create Python virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_success "Virtual environment already exists"
        return
    fi
    
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    print_success "Virtual environment created and activated"
}

# Function to install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    source venv/bin/activate
    
    # Install dependencies with better error handling
    if pip install -r requirements.txt; then
        print_success "Python dependencies installed successfully"
    else
        print_warning "Some packages failed to install, trying alternative method..."
        
        # Try installing packages individually
        while read requirement; do
            if [[ $requirement =~ ^[[:space:]]*# ]] || [[ -z $requirement ]]; then
                continue
            fi
            
            print_status "Installing $requirement..."
            if ! pip install --no-cache-dir "$requirement"; then
                print_warning "Failed to install $requirement, continuing..."
            fi
        done < requirements.txt
        
        print_success "Python dependency installation completed"
    fi
}

# Interactive configuration function
interactive_config() {
    print_header
    echo -e "${CYAN}Welcome to the Advanced Discord Bot Setup!${NC}"
    echo ""
    echo "This script will guide you through setting up your Discord bot with:"
    echo "• Hybrid music system (Lavalink + yt-dlp for YouTube bypass)"
    echo "• Multiple music sources (SoundCloud, Bandcamp, YouTube)"
    echo "• Smart fallback system for failed YouTube tracks"
    echo "• MongoDB database with moderation logging"
    echo "• Redis for node communication and caching"
    echo "• Web API for configuration"
    echo "• Sharding and clustering support"
    echo ""
    
    # Discord Bot Token
    while true; do
        print_question "Enter your Discord Bot Token:"
        read -s DISCORD_TOKEN
        echo ""
        
        if [[ ${#DISCORD_TOKEN} -eq 0 ]]; then
            print_error "Token cannot be empty!"
            continue
        fi
        
        if [[ ${#DISCORD_TOKEN} -lt 50 ]]; then
            print_error "Token seems too short. Please check and try again."
            continue
        fi
        
        break
    done
    
    # Guild ID (optional)
    print_question "Enter your main Guild/Server ID (optional, for slash commands):"
    read GUILD_ID
    
    # Bot Prefix
    print_question "Enter bot command prefix (default: !):"
    read BOT_PREFIX
    BOT_PREFIX=${BOT_PREFIX:-!}
    
    # Database Configuration
    echo ""
    print_status "Database Configuration"
    print_question "Choose database type:"
    echo "1) MongoDB (recommended for production)"
    echo "2) JSON file (simple, good for testing)"
    read -p "Enter choice (1-2): " DB_CHOICE
    
    case $DB_CHOICE in
        1)
            DATABASE_TYPE="mongodb"
            print_question "MongoDB URI (default: mongodb://localhost:27017):"
            read MONGODB_URI
            MONGODB_URI=${MONGODB_URI:-mongodb://localhost:27017}
            DATABASE_URL=$MONGODB_URI
            ;;
        2)
            DATABASE_TYPE="json"
            DATABASE_URL="data/database.json"
            ;;
        *)
            print_warning "Invalid choice, defaulting to JSON database"
            DATABASE_TYPE="json"
            DATABASE_URL="data/database.json"
            ;;
    esac
    
    # Lavalink Configuration
    echo ""
    print_status "Lavalink Configuration"
    print_question "Lavalink host (default: localhost):"
    read LAVALINK_HOST
    LAVALINK_HOST=${LAVALINK_HOST:-localhost}
    
    print_question "Lavalink port (default: 2333):"
    read LAVALINK_PORT
    LAVALINK_PORT=${LAVALINK_PORT:-2333}
    
    print_question "Lavalink password (default: youshallnotpass):"
    read LAVALINK_PASSWORD
    LAVALINK_PASSWORD=${LAVALINK_PASSWORD:-youshallnotpass}
    
    # Redis Configuration (for clustering)
    echo ""
    print_status "Redis Configuration (for node clustering)"
    print_question "Enable Redis clustering? (y/N):"
    read ENABLE_REDIS
    
    if [[ $ENABLE_REDIS =~ ^[Yy]$ ]]; then
        print_question "Redis host (default: localhost):"
        read REDIS_HOST
        REDIS_HOST=${REDIS_HOST:-localhost}
        
        print_question "Redis port (default: 6379):"
        read REDIS_PORT
        REDIS_PORT=${REDIS_PORT:-6379}
        
        print_question "Redis password (optional):"
        read REDIS_PASSWORD
    else
        REDIS_HOST="localhost"
        REDIS_PORT="6379"
        REDIS_PASSWORD=""
    fi
    
    # Web API Configuration
    echo ""
    print_status "Web API Configuration"
    print_question "Enable web API for configuration? (y/N):"
    read ENABLE_WEB_API
    
    if [[ $ENABLE_WEB_API =~ ^[Yy]$ ]]; then
        WEB_API_ENABLED="true"
        
        print_question "Web API port (default: 8080):"
        read WEB_PORT
        WEB_PORT=${WEB_PORT:-8080}
        
        print_question "Web API secret key (will be generated if empty):"
        read WEB_SECRET_KEY
        if [[ -z $WEB_SECRET_KEY ]]; then
            WEB_SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || echo "generated_secret_key_$(date +%s)")
        fi
    else
        WEB_API_ENABLED="false"
        WEB_PORT="8080"
        WEB_SECRET_KEY=""
    fi
    
    # Sharding Configuration
    echo ""
    print_status "Sharding Configuration"
    print_question "Enable automatic sharding? (y/N):"
    read ENABLE_SHARDING
    
    if [[ $ENABLE_SHARDING =~ ^[Yy]$ ]]; then
        SHARDING_ENABLED="true"
        
        print_question "Manual shard count (leave empty for auto-detection):"
        read SHARD_COUNT
    else
        SHARDING_ENABLED="false"
        SHARD_COUNT=""
    fi
    
    # Node Configuration
    echo ""
    print_status "Node/Cluster Configuration"
    print_question "Node ID (default: node-1):"
    read NODE_ID
    NODE_ID=${NODE_ID:-node-1}
    
    print_question "Is this the primary node? (Y/n):"
    read IS_PRIMARY
    if [[ $IS_PRIMARY =~ ^[Nn]$ ]]; then
        IS_PRIMARY_NODE="false"
    else
        IS_PRIMARY_NODE="true"
    fi
}

# Continue with remaining functions...
source ./install_functions.sh 2>/dev/null || true

# Main installation flow
main() {
    print_header
    
    # Pre-installation checks
    check_root
    detect_os
    check_sudo
    
    # Interactive configuration
    interactive_config
    
    echo ""
    print_status "Starting installation with your configuration..."
    echo ""
    
    # System updates and package installation
    update_system
    install_python
    install_java
    
    # Database installation based on choice
    if [[ $DATABASE_TYPE == "mongodb" ]]; then
        install_mongodb
    fi
    
    # Redis installation if enabled
    if [[ $ENABLE_REDIS =~ ^[Yy]$ ]]; then
        install_redis
    fi
    
    # Download Lavalink
    download_lavalink
    
    # Python environment setup
    create_venv
    install_python_deps
    
    # Create directories and files
    mkdir -p logs data cogs core database web static templates
    
    # Create .env file
    cat > .env << EOF
# Discord Bot Configuration
DISCORD_TOKEN=$DISCORD_TOKEN
GUILD_ID=$GUILD_ID
PREFIX=$BOT_PREFIX
EMBED_COLOR=0x7289da

# Database Configuration
DATABASE_TYPE=$DATABASE_TYPE
MONGODB_URI=$DATABASE_URL
DATABASE_NAME=discord_bot
JSON_DATABASE_PATH=data/database.json

# Lavalink Configuration
LAVALINK_HOST=$LAVALINK_HOST
LAVALINK_PORT=$LAVALINK_PORT
LAVALINK_PASSWORD=$LAVALINK_PASSWORD
LAVALINK_SSL=false

# Redis Configuration
REDIS_HOST=$REDIS_HOST
REDIS_PORT=$REDIS_PORT
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_DB=0

# Web API Configuration
WEB_API_ENABLED=$WEB_API_ENABLED
WEB_HOST=0.0.0.0
WEB_PORT=$WEB_PORT
WEB_SECRET_KEY=$WEB_SECRET_KEY
CORS_ORIGINS=*

# Sharding Configuration
SHARDING_ENABLED=$SHARDING_ENABLED
SHARD_COUNT=$SHARD_COUNT
AUTO_SHARD=true

# Node Configuration
NODE_ID=$NODE_ID
CLUSTER_NAME=discord-bot-cluster
IS_PRIMARY_NODE=$IS_PRIMARY_NODE
NODE_HEARTBEAT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Owner Configuration (comma-separated user IDs)
OWNER_IDS=
EOF
    
    # Create management scripts
    cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python main.py
EOF
    chmod +x start.sh
    
    cat > update.sh << 'EOF'
#!/bin/bash
echo "Updating Discord Bot..."
git stash
git pull origin main
source venv/bin/activate
pip install --upgrade -r requirements.txt
echo "Update completed!"
EOF
    chmod +x update.sh
    
    cat > stop.sh << 'EOF'
#!/bin/bash
echo "Stopping Discord Bot..."
pkill -f "python main.py" || echo "Bot not running"
pkill -f "java.*Lavalink.jar" || echo "Lavalink not running"
echo "Stopped"
EOF
    chmod +x stop.sh
    
    # Create main.py if it doesn't exist
    if [ ! -f "main.py" ]; then
        cat > main.py << 'EOF'
#!/usr/bin/env python3

import asyncio
import sys
from loguru import logger
from core import create_bot
from config import config

async def main():
    """Main function to run the bot"""
    
    # Validate configuration
    errors = config.validate()
    if errors:
        logger.error("Configuration errors found:")
        for error in errors:
            logger.error(f"  - {error}")
        sys.exit(1)
    
    # Create and run bot
    bot = create_bot()
    
    try:
        logger.info("Starting Advanced Discord Bot...")
        await bot.start(config.token)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
EOF
    fi
    
    # Final instructions
    echo ""
    print_success "🎉 Installation completed successfully!"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        NEXT STEPS                            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "1. Review your configuration in .env file"
    echo "2. Start the bot: ./start.sh"
    echo "3. View logs: tail -f logs/bot.log"
    echo "4. Update the bot: ./update.sh"
    echo "5. Stop the bot: ./stop.sh"
    echo ""
    echo -e "${GREEN}🎵 Music Features:${NC}"
    echo "• Regular search: !play song name (SoundCloud/Bandcamp)"
    echo "• YouTube search: !play yt:song name (direct YouTube)"
    echo "• Automatic fallback: YouTube failures auto-retry"
    echo ""
    echo -e "${YELLOW}🍪 Optional YouTube Enhancement:${NC}"
    echo "• For better YouTube access, set up cookies:"
    echo "  python setup_cookies.py"
    echo "• This enables age-restricted and region-locked content"
    echo ""
    echo -e "${CYAN}Your hybrid music bot is ready to run!${NC}"
    echo ""
}

# Run main function
main "$@"