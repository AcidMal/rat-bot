#!/bin/bash

# Discord Bot Auto-Installation Script for Debian-based Systems
# This script will install Node.js, FFmpeg, and set up the Discord bot

echo "🤖 Discord Bot Auto-Installation Script"
echo "========================================"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root. Please run as a regular user."
   exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Node.js (using NodeSource repository for latest version)
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify Node.js installation
echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Install FFmpeg
echo "📦 Installing FFmpeg..."
sudo apt install -y ffmpeg

# Verify FFmpeg installation
echo "✅ FFmpeg version: $(ffmpeg -version | head -n1)"

# Create bot directory
BOT_DIR="$HOME/discord-bot"
echo "📁 Creating bot directory at $BOT_DIR..."
mkdir -p "$BOT_DIR"
cd "$BOT_DIR"

# Create package.json
echo "📄 Creating package.json..."
cat > package.json << 'EOF'
{
  "name": "discord-bot-template",
  "version": "1.0.0",
  "description": "A template Discord bot using Discord.js",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "deploy": "node src/deploy-commands.js",
    "shard": "node src/shardManager.js",
    "cluster": "node src/clusterManager.js",
    "run": "node run.js",
    "update": "node update.js",
    "update:bash": "./update.sh",
    "update:win": "update.bat"
  },
  "keywords": [
    "discord",
    "bot",
    "discord.js",
    "template"
  ],
  "author": "Your Name",
  "license": "MIT",
  "dependencies": {
    "discord.js": "^14.14.1",
    "dotenv": "^16.3.1",
    "@discordjs/voice": "^0.16.1",
    "play-dl": "^1.9.7",
    "sodium": "^3.0.2",
    "libsodium-wrappers": "^0.7.13",
    "sqlite3": "^5.1.6",
    "better-sqlite3": "^9.2.2",
    "discord-hybrid-sharding": "^1.0.8"
  },
  "devDependencies": {
    "nodemon": "^3.0.2"
  },
  "engines": {
    "node": ">=16.9.0"
  }
}
EOF

# Create .env file with user input
echo "🔧 Setting up environment variables..."
echo "Please provide the following information:"

# Get Discord Bot Token
while true; do
    read -p "Discord Bot Token: " DISCORD_TOKEN
    if [[ ${#DISCORD_TOKEN} -ge 50 ]]; then
        break
    else
        echo "❌ Invalid token. Please enter a valid Discord bot token."
    fi
done

# Get Client ID
while true; do
    read -p "Client ID: " CLIENT_ID
    if [[ $CLIENT_ID =~ ^[0-9]+$ ]] && [[ ${#CLIENT_ID} -ge 15 ]]; then
        break
    else
        echo "❌ Invalid Client ID. Please enter a valid Discord client ID."
    fi
done

# Get Guild ID
while true; do
    read -p "Guild ID: " GUILD_ID
    if [[ $GUILD_ID =~ ^[0-9]+$ ]] && [[ ${#GUILD_ID} -ge 15 ]]; then
        break
    else
        echo "❌ Invalid Guild ID. Please enter a valid Discord guild ID."
    fi
done

# Create .env file
cat > .env << EOF
# Discord Bot Configuration
DISCORD_TOKEN=$DISCORD_TOKEN
CLIENT_ID=$CLIENT_ID
GUILD_ID=$GUILD_ID

# Sharding Configuration (Optional)
# Set to 'auto' for automatic sharding or specify a number
TOTAL_SHARDS=auto

# Clustering Configuration (Optional)
# Set to 'auto' for automatic clustering or specify a number
TOTAL_CLUSTERS=auto

# Shard/Cluster ID (Set automatically by managers)
SHARD_ID=
CLUSTER_ID=
EOF

# Create env.example
cat > env.example << 'EOF'
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_bot_token_here
CLIENT_ID=your_client_id_here
GUILD_ID=your_guild_id_here

# Sharding Configuration (Optional)
# Set to 'auto' for automatic sharding or specify a number
TOTAL_SHARDS=auto

# Clustering Configuration (Optional)
# Set to 'auto' for automatic clustering or specify a number
TOTAL_CLUSTERS=auto

# Shard/Cluster ID (Set automatically by managers)
SHARD_ID=
CLUSTER_ID=
EOF

# Create .gitignore
cat > .gitignore << 'EOF'
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/

# nyc test coverage
.nyc_output

# Dependency directories
node_modules/
jspm_packages/

# Optional npm cache directory
.npm

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# Database files
data/
*.db
*.sqlite
*.sqlite3

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
tmp/
temp/
EOF

# Create src directory structure
echo "📁 Creating source directory structure..."
mkdir -p src/{commands/{general,info,music,moderation},events,utils}

# Create basic files
touch src/index.js
touch src/shardManager.js
touch src/clusterManager.js
touch src/deploy-commands.js
touch src/events/ready.js
touch src/events/interactionCreate.js
touch src/events/messageCreate.js
touch src/utils/musicManager.js
touch src/utils/databaseManager.js

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Create helper scripts
echo "📄 Creating helper scripts..."

# start.sh
cat > start.sh << 'EOF'
#!/bin/bash
echo "🤖 Starting Discord Bot..."
npm start
EOF

# dev.sh
cat > dev.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting Discord Bot in development mode..."
npm run dev
EOF

# deploy.sh
cat > deploy.sh << 'EOF'
#!/bin/bash
echo "🚀 Deploying slash commands..."
npm run deploy
EOF

# shard.sh
cat > shard.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting Discord Bot with sharding..."
npm run shard
EOF

# cluster.sh
cat > cluster.sh << 'EOF'
#!/bin/bash
echo "🔧 Starting Discord Bot with clustering..."
npm run cluster
EOF

# update.sh
cat > update.sh << 'EOF'
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
EOF

# update.bat
cat > update.bat << 'EOF'
@echo off
setlocal enabledelayedexpansion

REM Discord Bot Updater Script for Windows
REM This script updates the bot from the GitHub repository and updates dependencies

echo 🔄 Discord Bot Updater
echo ======================
echo.

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ This directory is not a git repository.
    echo Please run this script from your bot directory.
    pause
    exit /b 1
)

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed. Please install git first.
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed. Please install Node.js first.
    pause
    exit /b 1
)

echo 📦 Checking for updates...

REM Store current branch
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo 📍 Current branch: !CURRENT_BRANCH!

REM Fetch latest changes
echo 📥 Fetching latest changes from remote...
git fetch origin

REM Check if there are any updates
for /f "tokens=*" %%i in ('git rev-parse HEAD') do set LOCAL_COMMIT=%%i
for /f "tokens=*" %%i in ('git rev-parse origin/!CURRENT_BRANCH!') do set REMOTE_COMMIT=%%i

if "!LOCAL_COMMIT!"=="!REMOTE_COMMIT!" (
    echo ✅ Bot is already up to date!
    echo.
    set /p update_deps="Would you like to update dependencies anyway? (y/N): "
    if /i "!update_deps!"=="y" (
        echo 📦 Updating dependencies...
        npm update
        echo ✅ Dependencies updated!
    ) else (
        echo 🔄 No updates needed.
        pause
        exit /b 0
    )
) else (
    echo 🔄 Updates found! Pulling latest changes...
    
    REM Check for uncommitted changes
    git status --porcelain >nul 2>&1
    if not errorlevel 1 (
        echo ⚠️  Warning: You have uncommitted changes.
        echo Your changes will be stashed before pulling.
        set /p continue_update="Continue? (y/N): "
        if /i not "!continue_update!"=="y" (
            echo ❌ Update cancelled.
            pause
            exit /b 1
        )
        
        REM Stash changes
        echo 📦 Stashing local changes...
        git stash push -m "Auto-stash before update %date% %time%"
    )
    
    REM Pull latest changes
    echo 📥 Pulling latest changes...
    git pull origin !CURRENT_BRANCH!
    if not errorlevel 1 (
        echo ✅ Successfully pulled latest changes!
        
        REM Update dependencies
        echo 📦 Updating dependencies...
        npm update
        
        REM Install any new dependencies
        echo 📦 Installing any new dependencies...
        npm install
        
        echo ✅ Bot updated successfully!
        
        REM Show recent commits
        echo.
        echo 📝 Recent changes:
        git log --oneline -5
        
        REM Restore stashed changes if any
        git stash list | findstr "Auto-stash before update" >nul 2>&1
        if not errorlevel 1 (
            echo.
            echo 📦 Restoring your local changes...
            git stash pop
            if not errorlevel 1 (
                echo ✅ Local changes restored!
            ) else (
                echo ⚠️  Warning: Could not automatically restore local changes.
                echo You can restore them manually with: git stash pop
            )
        )
        
    ) else (
        echo ❌ Failed to pull latest changes.
        echo Please check your internet connection and try again.
        pause
        exit /b 1
    )
)

REM Check for any new environment variables
echo.
echo 🔧 Checking for new environment variables...
if exist "env.example" (
    if exist ".env" (
        echo ✅ Environment variables file exists.
        echo Please manually check env.example for any new variables.
    ) else (
        echo ⚠️  No .env file found. Please create one based on env.example
    )
)

REM Check for any new scripts
echo.
echo 🔧 Checking for new scripts...
if exist "package.json" (
    echo Available npm scripts:
    npm run 2>nul | findstr /r "^  [a-z-]+" | findstr /v "npm ERR!"
)

REM Final status
echo.
echo 🎉 Update completed!
echo.
echo Next steps:
echo 1. Review any new environment variables and update your .env file
echo 2. Test your bot: npm start
echo 3. Deploy any new commands: npm run deploy
echo.
echo If you encounter any issues, check the logs and ensure all dependencies are properly installed.

pause
EOF

# update.js
cat > update.js << 'EOF'
#!/usr/bin/env node

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔄 Discord Bot Updater');
console.log('======================');
console.log('');

// Check if we're in a git repository
if (!fs.existsSync('.git')) {
  console.log('❌ This directory is not a git repository.');
  console.log('Please run this script from your bot directory.');
  process.exit(1);
}

// Check if git is installed
try {
  execSync('git --version', { stdio: 'ignore' });
} catch (error) {
  console.log('❌ Git is not installed. Please install git first.');
  process.exit(1);
}

// Check if npm is installed
try {
  execSync('npm --version', { stdio: 'ignore' });
} catch (error) {
  console.log('❌ npm is not installed. Please install Node.js first.');
  process.exit(1);
}

async function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function runCommand(command, options = {}) {
  try {
    const result = execSync(command, { 
      encoding: 'utf8', 
      stdio: options.silent ? 'ignore' : 'inherit',
      ...options 
    });
    return { success: true, output: result };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('📦 Checking for updates...');

  // Get current branch
  const branchResult = await runCommand('git branch --show-current', { silent: true });
  if (!branchResult.success) {
    console.log('❌ Failed to get current branch.');
    process.exit(1);
  }
  const currentBranch = branchResult.output.trim();
  console.log(`📍 Current branch: ${currentBranch}`);

  // Fetch latest changes
  console.log('📥 Fetching latest changes from remote...');
  const fetchResult = await runCommand('git fetch origin');
  if (!fetchResult.success) {
    console.log('❌ Failed to fetch from remote.');
    process.exit(1);
  }

  // Check if there are any updates
  const localCommitResult = await runCommand('git rev-parse HEAD', { silent: true });
  const remoteCommitResult = await runCommand(`git rev-parse origin/${currentBranch}`, { silent: true });
  
  if (!localCommitResult.success || !remoteCommitResult.success) {
    console.log('❌ Failed to get commit information.');
    process.exit(1);
  }

  const localCommit = localCommitResult.output.trim();
  const remoteCommit = remoteCommitResult.output.trim();

  if (localCommit === remoteCommit) {
    console.log('✅ Bot is already up to date!');
    console.log('');
    
    const updateDeps = await question('Would you like to update dependencies anyway? (y/N): ');
    if (updateDeps.toLowerCase() === 'y') {
      console.log('📦 Updating dependencies...');
      await runCommand('npm update');
      console.log('✅ Dependencies updated!');
    } else {
      console.log('🔄 No updates needed.');
      rl.close();
      return;
    }
  } else {
    console.log('🔄 Updates found! Pulling latest changes...');
    
    // Check for uncommitted changes
    const statusResult = await runCommand('git status --porcelain', { silent: true });
    const hasChanges = statusResult.success && statusResult.output.trim() !== '';
    
    if (hasChanges) {
      console.log('⚠️  Warning: You have uncommitted changes.');
      console.log('Your changes will be stashed before pulling.');
      const continueUpdate = await question('Continue? (y/N): ');
      if (continueUpdate.toLowerCase() !== 'y') {
        console.log('❌ Update cancelled.');
        rl.close();
        return;
      }
      
      // Stash changes
      console.log('📦 Stashing local changes...');
      await runCommand(`git stash push -m "Auto-stash before update ${new Date().toISOString()}"`);
    }
    
    // Pull latest changes
    console.log('📥 Pulling latest changes...');
    const pullResult = await runCommand(`git pull origin ${currentBranch}`);
    
    if (pullResult.success) {
      console.log('✅ Successfully pulled latest changes!');
      
      // Update dependencies
      console.log('📦 Updating dependencies...');
      await runCommand('npm update');
      
      // Install any new dependencies
      console.log('📦 Installing any new dependencies...');
      await runCommand('npm install');
      
      console.log('✅ Bot updated successfully!');
      
      // Show recent commits
      console.log('');
      console.log('📝 Recent changes:');
      await runCommand('git log --oneline -5');
      
      // Restore stashed changes if any
      const stashListResult = await runCommand('git stash list', { silent: true });
      if (stashListResult.success && stashListResult.output.includes('Auto-stash before update')) {
        console.log('');
        console.log('📦 Restoring your local changes...');
        const stashPopResult = await runCommand('git stash pop');
        if (stashPopResult.success) {
          console.log('✅ Local changes restored!');
        } else {
          console.log('⚠️  Warning: Could not automatically restore local changes.');
          console.log('You can restore them manually with: git stash pop');
        }
      }
      
    } else {
      console.log('❌ Failed to pull latest changes.');
      console.log('Please check your internet connection and try again.');
      process.exit(1);
    }
  }

  // Check for any new environment variables
  console.log('');
  console.log('🔧 Checking for new environment variables...');
  if (fs.existsSync('env.example')) {
    if (fs.existsSync('.env')) {
      console.log('✅ Environment variables file exists.');
      console.log('Please manually check env.example for any new variables.');
    } else {
      console.log('⚠️  No .env file found. Please create one based on env.example');
    }
  }

  // Check for any new scripts
  console.log('');
  console.log('🔧 Checking for new scripts...');
  if (fs.existsSync('package.json')) {
    console.log('Available npm scripts:');
    const scriptsResult = await runCommand('npm run', { silent: true });
    if (scriptsResult.success) {
      const lines = scriptsResult.output.split('\n');
      lines.forEach(line => {
        if (line.match(/^  [a-z-]+$/)) {
          console.log(`  npm run ${line.trim()}`);
        }
      });
    }
  }

  // Final status
  console.log('');
  console.log('🎉 Update completed!');
  console.log('');
  console.log('Next steps:');
  console.log('1. Review any new environment variables and update your .env file');
  console.log('2. Test your bot: npm start');
  console.log('3. Deploy any new commands: npm run deploy');
  console.log('');
  console.log('If you encounter any issues, check the logs and ensure all dependencies are properly installed.');

  rl.close();
}

main().catch(error => {
  console.error('❌ An error occurred:', error.message);
  rl.close();
  process.exit(1);
});
EOF

# run.js
cat > run.js << 'EOF'
#!/usr/bin/env node

const { spawn } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🤖 Discord Bot Launcher');
console.log('========================');
console.log('');
console.log('Choose how to run your bot:');
console.log('1. Normal mode (single process)');
console.log('2. Sharded mode (multiple shards)');
console.log('3. Clustered mode (multiple processes)');
console.log('4. Development mode (with auto-restart)');
console.log('5. Deploy commands only');
console.log('');

rl.question('Enter your choice (1-5): ', (choice) => {
  let command;
  let description;

  switch (choice.trim()) {
    case '1':
      command = 'npm start';
      description = 'Starting bot in normal mode...';
      break;
    case '2':
      command = 'npm run shard';
      description = 'Starting bot with sharding...';
      break;
    case '3':
      command = 'npm run cluster';
      description = 'Starting bot with clustering...';
      break;
    case '4':
      command = 'npm run dev';
      description = 'Starting bot in development mode...';
      break;
    case '5':
      command = 'npm run deploy';
      description = 'Deploying slash commands...';
      break;
    default:
      console.log('❌ Invalid choice. Please run the script again.');
      rl.close();
      return;
  }

  console.log(`\n${description}`);
  console.log('Press Ctrl+C to stop the bot\n');

  const child = spawn(command, [], {
    stdio: 'inherit',
    shell: true
  });

  child.on('error', (error) => {
    console.error('❌ Error starting bot:', error.message);
    rl.close();
  });

  child.on('close', (code) => {
    console.log(`\n✅ Bot process exited with code ${code}`);
    rl.close();
  });

  // Handle process termination
  process.on('SIGINT', () => {
    console.log('\n🛑 Stopping bot...');
    child.kill('SIGINT');
  });

  process.on('SIGTERM', () => {
    console.log('\n🛑 Stopping bot...');
    child.kill('SIGTERM');
  });
});
EOF

# Make scripts executable
chmod +x start.sh dev.sh deploy.sh shard.sh cluster.sh update.sh update.js run.js

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📁 Bot directory: $BOT_DIR"
echo "🔧 Environment file: $BOT_DIR/.env (already configured)"
echo ""
echo "🚀 Available commands:"
echo "  ./start.sh    - Start the bot normally"
echo "  ./dev.sh      - Start the bot in development mode"
echo "  ./deploy.sh   - Deploy slash commands"
echo "  ./shard.sh    - Start the bot with sharding"
echo "  ./cluster.sh  - Start the bot with clustering"
echo "  ./update.sh   - Update bot from GitHub repository"
echo "  npm run update - Update using Node.js script"
echo ""
echo "📚 Next steps:"
echo "1. Add your bot to your Discord server"
echo "2. Run './deploy.sh' to register slash commands"
echo "3. Run './start.sh' to start the bot"
echo "4. For large bots, consider using './shard.sh' or './cluster.sh'"
echo "5. Use './update.sh' to keep your bot updated"
echo ""
echo "📖 For more information, check the README.md file"
echo ""
echo "🎉 Your Discord bot is ready to use!" 