#!/bin/bash

# Discord Bot Standalone Updater Script
# This script updates dependencies and provides guidance for manual updates

echo "🔄 Discord Bot Standalone Updater"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first."
    exit 1
fi

echo "📦 Checking for updates..."

# Check if package.json exists
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from your bot directory."
    exit 1
fi

echo "✅ Found package.json"

# Update dependencies
echo "📦 Updating dependencies..."
npm update

# Install any new dependencies
echo "📦 Installing any new dependencies..."
npm install

echo "✅ Dependencies updated successfully!"

# Check for any new environment variables
echo ""
echo "🔧 Checking for new environment variables..."
if [ -f "env.example" ]; then
    if [ -f ".env" ]; then
        echo "✅ Environment variables file exists."
        echo "Please manually check env.example for any new variables."
    else
        echo "⚠️  No .env file found. Please create one based on env.example"
    fi
else
    echo "⚠️  No env.example file found. Please check for updates manually."
fi

# Check for any new scripts
echo ""
echo "🔧 Checking for new scripts..."
if [ -f "package.json" ]; then
    echo "Available npm scripts:"
    npm run 2>/dev/null | grep -E "^  [a-z-]+" | sed 's/^  /  npm run /' || echo "No scripts found"
fi

# Provide guidance for manual updates
echo ""
echo "📚 Manual Update Instructions:"
echo "Since this bot was installed without git, you'll need to manually update:"
echo ""
echo "1. Download the latest version from the repository"
echo "2. Compare files with your current installation"
echo "3. Copy new files and update existing ones"
echo "4. Run this script again to update dependencies"
echo ""
echo "Alternatively, you can:"
echo "1. Initialize git: git init"
echo "2. Add remote: git remote add origin <repository-url>"
echo "3. Use the regular updater: ./update.sh"
echo ""

# Final status
echo ""
echo "🎉 Update completed!"
echo ""
echo "Next steps:"
echo "1. Review any new environment variables and update your .env file"
echo "2. Test your bot: npm start"
echo "3. Deploy any new commands: npm run deploy"
echo ""
echo "If you encounter any issues, check the logs and ensure all dependencies are properly installed." 