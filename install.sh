#!/bin/bash

# RatBot Installation Script
# This script installs all dependencies and sets up the bot

set -e

echo "🐀 RatBot Installation Script"
echo "=============================="

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

# Check if Python 3.8+ is installed
print_status "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.8+ is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
print_status "Checking pip..."
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
else
    print_error "pip3 is required but not installed. Please install pip."
    exit 1
fi

# Check if Java is installed (for Lavalink)
print_status "Checking Java..."
if command -v java &> /dev/null; then
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
    print_success "Java $JAVA_VERSION found"
else
    print_warning "Java not found. Lavalink will not work without Java 11+."
    print_status "Please install Java 11 or higher to use music features."
fi

# Create virtual environment
print_status "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install system dependencies first
print_status "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    # Ubuntu/Debian
    print_status "Installing yarl from system packages..."
    sudo apt-get update
    sudo apt-get install -y python3-yarl python3-dev build-essential libssl-dev libffi-dev
    print_success "System dependencies installed"
elif command -v dnf &> /dev/null; then
    # Fedora/RHEL
    print_status "Installing yarl from system packages..."
    sudo dnf install -y python3-yarl python3-devel openssl-devel libffi-devel
    print_success "System dependencies installed"
elif command -v pacman &> /dev/null; then
    # Arch Linux
    print_status "Installing yarl from system packages..."
    sudo pacman -S --noconfirm python-yarl base-devel
    print_success "System dependencies installed"
else
    print_warning "Could not detect package manager, will try pip installation"
fi

# Install Python dependencies
print_status "Installing Python dependencies..."
print_status "This may take a few minutes..."

# Create a temporary requirements file without yarl
print_status "Creating temporary requirements file..."
grep -v "yarl" requirements.txt > requirements_temp.txt

# Install dependencies with better error handling
if pip install -r requirements_temp.txt; then
    print_success "Python dependencies installed"
else
    print_warning "Some packages failed to install with pip, trying alternative method..."
    
    # Try installing with --no-cache-dir and --force-reinstall
    if pip install --no-cache-dir --force-reinstall -r requirements_temp.txt; then
        print_success "Python dependencies installed with alternative method"
    else
        print_error "Failed to install Python dependencies"
        print_status "Trying to install packages individually..."
        
        # Install packages individually (excluding yarl)
        packages=("discord.py==2.3.2" "wavelink==2.6.4" "aiohttp==3.9.1" "asyncpg==0.29.0" "python-dotenv==1.0.0" "colorama==0.4.6" "psutil==5.9.6")
        
        for package in "${packages[@]}"; do
            print_status "Installing $package..."
            if pip install --no-cache-dir "$package"; then
                print_success "Installed $package"
            else
                print_warning "Failed to install $package, continuing..."
            fi
        done
        
        print_success "Dependency installation completed"
    fi
fi

# Clean up temporary file
rm -f requirements_temp.txt

# Verify yarl installation
print_status "Verifying yarl installation..."
if python3 -c "import yarl; print('yarl version:', yarl.__version__)" 2>/dev/null; then
    print_success "yarl is installed and working"
else
    print_warning "yarl not found, attempting pip installation as fallback..."
    pip install --no-cache-dir yarl==1.9.2 || print_warning "yarl installation failed, but continuing..."
fi

# Download Lavalink if Java is available
if command -v java &> /dev/null; then
    print_status "Checking Lavalink..."
    if [ ! -f "Lavalink.jar" ]; then
        print_status "Downloading Lavalink..."
        LAVALINK_VERSION="4.0.0"
        LAVALINK_URL="https://github.com/lavalink-devs/Lavalink/releases/download/$LAVALINK_VERSION/Lavalink.jar"
        
        if command -v curl &> /dev/null; then
            curl -L -o Lavalink.jar "$LAVALINK_URL"
        elif command -v wget &> /dev/null; then
            wget -O Lavalink.jar "$LAVALINK_URL"
        else
            print_error "Neither curl nor wget found. Please install one of them or download Lavalink.jar manually."
            print_status "Download Lavalink from: https://github.com/lavalink-devs/Lavalink/releases"
        fi
        
        if [ -f "Lavalink.jar" ]; then
            print_success "Lavalink downloaded successfully"
        fi
    else
        print_success "Lavalink.jar already exists"
    fi
else
    print_warning "Java not found. Skipping Lavalink download."
    print_status "Please install Java 11+ and run this script again to download Lavalink."
fi

# Create necessary directories
print_status "Creating directories..."
mkdir -p logs
mkdir -p data
print_success "Directories created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file..."
    cat > .env << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/ratbot

# Lavalink Configuration
LAVALINK_HOST=localhost
LAVALINK_PORT=2333
LAVALINK_PASSWORD=youshallnotpass

# Bot Configuration
PREFIX=!
EMBED_COLOR=0x00ff00

# Logging Configuration
LOG_LEVEL=INFO

# ModLog Configuration
MODLOG_CHANNEL_ID=your_modlog_channel_id_here
EOF
    print_success ".env file created"
    print_warning "Please edit .env file with your actual configuration values"
else
    print_status ".env file already exists"
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x install.sh
chmod +x update.sh
chmod +x start.sh
chmod +x stop.sh
chmod +x troubleshoot.sh
print_success "Scripts made executable"

# Database setup instructions
print_status "Database setup instructions:"
echo "1. Install PostgreSQL if not already installed"
echo "2. Create a database named 'ratbot'"
echo "3. Update the DATABASE_URL in .env file"
echo "4. The bot will create the necessary tables automatically"

# Final instructions
print_success "Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Discord bot token and other settings"
echo "2. Set up PostgreSQL database"
echo "3. Run './start.sh' to start the bot"
echo "4. Use './stop.sh' to stop the bot"
echo "5. Use './update.sh' to update the bot from GitHub"
echo ""
echo "For help, check the README.md file or run './start.sh --help'" 