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