#!/bin/bash

# Quick fix for yarl installation issues
echo "🔧 Quick fix for yarl installation issues"
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

# Upgrade pip and setuptools
echo "Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

# Clear pip cache
echo "Clearing pip cache..."
pip cache purge

# Try different methods to install yarl
echo "Attempting to install yarl..."

# Method 1: Install with --no-cache-dir
echo "Method 1: Installing with --no-cache-dir"
pip install --no-cache-dir yarl>=1.7.2

# Method 2: Install with --force-reinstall
echo "Method 2: Installing with --force-reinstall"
pip install --force-reinstall yarl>=1.7.2

# Method 3: Install from wheel only
echo "Method 3: Installing from wheel only"
pip install --only-binary=all yarl>=1.7.2

# Method 4: Install with specific version
echo "Method 4: Installing specific version"
pip install yarl==1.9.2

echo "Yarl installation attempts completed!"
echo "Check if yarl is now installed:"
python3 -c "import yarl; print('yarl version:', yarl.__version__)" 2>/dev/null || echo "yarl still not installed" 