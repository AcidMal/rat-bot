#!/bin/bash

# RatBot Database Setup Script
# This script sets up PostgreSQL database for RatBot

set -e

echo "🗄️ RatBot Database Setup"
echo "========================"

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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Function to install PostgreSQL
install_postgresql() {
    print_status "Installing PostgreSQL..."
    
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y postgresql postgresql-contrib
        print_success "PostgreSQL installed"
        
        # Start and enable PostgreSQL service
        print_status "Starting PostgreSQL service..."
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        print_success "PostgreSQL service started and enabled"
        
    elif command -v dnf &> /dev/null; then
        # Fedora/RHEL
        sudo dnf install -y postgresql postgresql-server postgresql-contrib
        print_success "PostgreSQL installed"
        
        # Initialize and start PostgreSQL
        print_status "Initializing PostgreSQL database..."
        sudo postgresql-setup --initdb
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        print_success "PostgreSQL service started and enabled"
        
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm postgresql
        print_success "PostgreSQL installed"
        
        # Initialize and start PostgreSQL
        print_status "Initializing PostgreSQL database..."
        sudo -u postgres initdb -D /var/lib/postgres/data
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
        print_success "PostgreSQL service started and enabled"
        
    else
        print_error "Could not detect package manager for PostgreSQL installation"
        print_status "Please install PostgreSQL manually and ensure it's running"
        return 1
    fi
    
    return 0
}

# Function to create database and user
create_database() {
    print_status "Creating database and user..."
    
    # Generate random password for database user
    DB_PASSWORD=$(openssl rand -base64 32)
    
    # Create database user and database
    sudo -u postgres psql -c "CREATE USER ratbot WITH PASSWORD '$DB_PASSWORD';" 2>/dev/null || print_warning "User ratbot might already exist"
    sudo -u postgres psql -c "CREATE DATABASE ratbot OWNER ratbot;" 2>/dev/null || print_warning "Database ratbot might already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ratbot TO ratbot;" 2>/dev/null || print_warning "Privileges might already be granted"
    
    print_success "Database and user created"
    
    # Update .env file with database credentials
    print_status "Updating .env file with database credentials..."
    if [ -f ".env" ]; then
        # Backup existing .env
        cp .env .env.backup
        print_status "Backed up existing .env file"
    fi
    
    # Create new .env with database credentials
    cat > .env << EOF
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here
GUILD_ID=your_guild_id_here

# Database Configuration
DATABASE_URL=postgresql://ratbot:$DB_PASSWORD@localhost/ratbot

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
    
    print_success "Database credentials added to .env file"
    print_warning "Database password: $DB_PASSWORD (saved in .env file)"
    
    return 0
}

# Function to test database connection
test_database() {
    print_status "Testing database connection..."
    
    # Check if virtual environment exists and activate it
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if python3 -c "
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_db():
    try:
        conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
        await conn.close()
        print('✅ Database connection successful!')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        exit(1)

asyncio.run(test_db())
" 2>/dev/null; then
        print_success "Database connection test passed"
        return 0
    else
        print_warning "Database connection test failed - you may need to configure PostgreSQL manually"
        return 1
    fi
}

# Function to create database tables
create_tables() {
    print_status "Creating database tables..."
    
    # Check if virtual environment exists and activate it
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    if python3 setup_database.py; then
        print_success "Database tables created successfully"
        return 0
    else
        print_warning "Failed to create database tables - you may need to run setup_database.py manually"
        return 1
    fi
}

# Main execution
print_status "Starting database setup..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    print_status "PostgreSQL not found. Installing..."
    if ! install_postgresql; then
        print_error "Failed to install PostgreSQL"
        exit 1
    fi
else
    print_success "PostgreSQL is already installed"
fi

# Create database and user
if create_database; then
    print_success "Database setup completed"
else
    print_error "Failed to create database"
    exit 1
fi

# Test database connection
if test_database; then
    print_success "Database connection verified"
else
    print_warning "Database connection test failed"
fi

# Create tables
if create_tables; then
    print_success "Database tables created"
else
    print_warning "Table creation failed"
fi

# Final summary
print_success "Database setup completed!"
echo ""
echo "✅ Database Information:"
echo "   • Database: ratbot"
echo "   • User: ratbot"
echo "   • Password: (saved in .env file)"
echo "   • Connection: PostgreSQL running on localhost"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env file with your Discord bot token"
echo "2. Run './start.sh' to start the bot"
echo ""
echo "For help, check the README.md file" 