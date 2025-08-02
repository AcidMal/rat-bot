#!/bin/bash

# Discord Bot Updater Script
# This script updates the bot from the GitHub repository and updates dependencies

echo "🔄 Discord Bot Updater"
echo "======================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ This directory is not a git repository."
    echo "Please run this script from your bot directory."
    exit 1
fi

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js first."
    exit 1
fi

echo "📦 Checking for updates..."

# Store current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Fetch latest changes
echo "📥 Fetching latest changes from remote..."
git fetch origin

# Check if there are any updates
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH)

if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
    echo "✅ Bot is already up to date!"
    echo ""
    echo "Would you like to update dependencies anyway? (y/N)"
    read -r update_deps
    if [[ $update_deps =~ ^[Yy]$ ]]; then
        echo "📦 Updating dependencies..."
        npm update
        echo "✅ Dependencies updated!"
    else
        echo "🔄 No updates needed."
        exit 0
    fi
else
    echo "🔄 Updates found! Pulling latest changes..."
    
    # Check for uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        echo "⚠️  Warning: You have uncommitted changes."
        echo "Your changes will be stashed before pulling."
        echo "Continue? (y/N)"
        read -r continue_update
        if [[ ! $continue_update =~ ^[Yy]$ ]]; then
            echo "❌ Update cancelled."
            exit 1
        fi
        
        # Stash changes
        echo "📦 Stashing local changes..."
        git stash push -m "Auto-stash before update $(date)"
    fi
    
    # Pull latest changes
    echo "📥 Pulling latest changes..."
    if git pull origin $CURRENT_BRANCH; then
        echo "✅ Successfully pulled latest changes!"
        
        # Update dependencies
        echo "📦 Updating dependencies..."
        npm update
        
        # Install any new dependencies
        echo "📦 Installing any new dependencies..."
        npm install
        
        echo "✅ Bot updated successfully!"
        
        # Show recent commits
        echo ""
        echo "📝 Recent changes:"
        git log --oneline -5
        
        # Restore stashed changes if any
        if git stash list | grep -q "Auto-stash before update"; then
            echo ""
            echo "📦 Restoring your local changes..."
            if git stash pop; then
                echo "✅ Local changes restored!"
            else
                echo "⚠️  Warning: Could not automatically restore local changes."
                echo "You can restore them manually with: git stash pop"
            fi
        fi
        
    else
        echo "❌ Failed to pull latest changes."
        echo "Please check your internet connection and try again."
        exit 1
    fi
fi

# Check for any new environment variables
echo ""
echo "🔧 Checking for new environment variables..."
if [ -f "env.example" ]; then
    if [ -f ".env" ]; then
        # Compare .env with env.example to find new variables
        NEW_VARS=$(comm -23 <(grep -E '^[A-Z_]+=' env.example | cut -d'=' -f1 | sort) <(grep -E '^[A-Z_]+=' .env | cut -d'=' -f1 | sort))
        
        if [ -n "$NEW_VARS" ]; then
            echo "⚠️  New environment variables found:"
            echo "$NEW_VARS"
            echo ""
            echo "Please update your .env file with these new variables."
        else
            echo "✅ Environment variables are up to date."
        fi
    else
        echo "⚠️  No .env file found. Please create one based on env.example"
    fi
fi

# Check for any new scripts
echo ""
echo "🔧 Checking for new scripts..."
if [ -f "package.json" ]; then
    # Check if there are new scripts in package.json
    echo "Available npm scripts:"
    npm run 2>/dev/null | grep -E "^  [a-z-]+" | sed 's/^  /  npm run /'
fi

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