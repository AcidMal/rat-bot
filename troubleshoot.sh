#!/bin/bash

# RatBot Troubleshooting Script
# This script helps resolve common installation and dependency issues

set -e

echo "🔧 RatBot Troubleshooting Script"
echo "================================"

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

# Check system information
print_status "Checking system information..."
echo "OS: $(uname -s)"
echo "Architecture: $(uname -m)"
echo "Python version: $(python3 --version 2>/dev/null || echo 'Python3 not found')"
echo "Pip version: $(pip3 --version 2>/dev/null || echo 'Pip3 not found')"
echo "Java version: $(java -version 2>&1 | head -n 1 || echo 'Java not found')"

# Check if virtual environment exists
if [ -d "venv" ]; then
    print_status "Virtual environment found"
    source venv/bin/activate
    echo "Virtual environment activated"
    echo "Python in venv: $(which python)"
    echo "Pip in venv: $(which pip)"
else
    print_warning "Virtual environment not found"
fi

# Function to fix pip issues
fix_pip() {
    print_status "Fixing pip issues..."
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install build tools
    print_status "Installing build tools..."
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3-dev build-essential
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3-devel
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf groupinstall -y "Development Tools"
        sudo dnf install -y python3-devel
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S --noconfirm base-devel python-pip
    else
        print_warning "Could not install build tools automatically"
        print_status "Please install build tools manually for your system"
    fi
}

# Function to fix yarl installation
fix_yarl() {
    print_status "Fixing yarl installation..."
    
    # Try different installation methods
    print_status "Method 1: Installing with --no-cache-dir"
    pip install --no-cache-dir yarl>=1.7.2 || true
    
    print_status "Method 2: Installing with --force-reinstall"
    pip install --force-reinstall yarl>=1.7.2 || true
    
    print_status "Method 3: Installing from wheel"
    pip install --only-binary=all yarl>=1.7.2 || true
    
    print_status "Method 4: Installing with setuptools"
    pip install --upgrade setuptools wheel
    pip install yarl>=1.7.2 || true
}

# Function to check and fix dependencies
check_dependencies() {
    print_status "Checking installed dependencies..."
    
    # List of required packages
    packages=("discord.py" "wavelink" "aiohttp" "asyncpg" "python-dotenv" "colorama" "psutil" "yarl")
    
    missing_packages=()
    
    for package in "${packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            print_success "$package is installed"
        else
            print_warning "$package is missing"
            missing_packages+=("$package")
        fi
    done
    
    if [ ${#missing_packages[@]} -eq 0 ]; then
        print_success "All dependencies are installed!"
    else
        print_status "Missing packages: ${missing_packages[*]}"
        print_status "Attempting to install missing packages..."
        
        for package in "${missing_packages[@]}"; do
            print_status "Installing $package..."
            pip install --no-cache-dir "$package" || print_warning "Failed to install $package"
        done
    fi
}

# Function to fix common issues
fix_common_issues() {
    print_status "Fixing common issues..."
    
    # Clear pip cache
    print_status "Clearing pip cache..."
    pip cache purge || true
    
    # Upgrade setuptools and wheel
    print_status "Upgrading setuptools and wheel..."
    pip install --upgrade setuptools wheel
    
    # Install Cython if needed
    print_status "Installing Cython..."
    pip install --no-cache-dir Cython || true
    
    # Fix permissions
    print_status "Checking permissions..."
    if [ -d "venv" ]; then
        chmod -R 755 venv/
    fi
}

# Main menu
show_menu() {
    echo ""
    echo "Select an option:"
    echo "1) Fix pip and build tools"
    echo "2) Fix yarl installation"
    echo "3) Check and fix dependencies"
    echo "4) Fix common issues"
    echo "5) Run all fixes"
    echo "6) Exit"
    echo ""
}

# Main function
main() {
    while true; do
        show_menu
        read -p "Enter your choice (1-6): " choice
        
        case $choice in
            1)
                fix_pip
                ;;
            2)
                fix_yarl
                ;;
            3)
                check_dependencies
                ;;
            4)
                fix_common_issues
                ;;
            5)
                print_status "Running all fixes..."
                fix_pip
                fix_yarl
                check_dependencies
                fix_common_issues
                print_success "All fixes completed!"
                ;;
            6)
                print_status "Exiting..."
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please enter 1-6."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main 