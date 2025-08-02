@echo off
REM Rat Bot Update Script for Windows
REM This script updates the bot without requiring a full reinstallation

echo 🔄 Rat Bot Update Script
echo =======================
echo.

REM Check if we're in the right directory
if not exist bot.py (
    echo ❌ Please run this script from the bot directory.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the update script
echo Running update script...
python update.py

echo.
echo Update process completed!
pause 