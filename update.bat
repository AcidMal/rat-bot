@echo off
echo 🔄 Rat Bot Update Script
echo ========================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the update script
echo 🚀 Starting update process...
python update.py

echo.
echo ✅ Update script completed!
pause 