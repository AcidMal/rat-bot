@echo off
REM Rat Bot Run Script for Windows
REM This script runs the bot with various options

REM Function to show help
:show_help
echo 🤖 Rat Bot Run Script
echo =====================
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --sharded          Run with automatic sharding
echo   --shard-manager N   Run with manual sharding (N = number of shards)
echo   --help             Show this help message
echo.
echo Examples:
echo   %0                 # Single instance (default)
echo   %0 --sharded       # Automatic sharding
echo   %0 --shard-manager 4  # Manual sharding with 4 shards
echo.
echo 🎵 Note: LavaLink server starts automatically with the bot!
goto :eof

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Parse command line arguments
if "%1"=="--sharded" (
    echo 🚀 Starting bot with automatic sharding...
    python run_sharded.py
    goto :eof
)

if "%1"=="--shard-manager" (
    if "%2"=="" (
        echo ❌ Please specify number of shards: --shard-manager N
        pause
        exit /b 1
    )
    echo 🚀 Starting bot with manual sharding (%2 shards)...
    python shard_manager.py --shards %2
    goto :eof
)

if "%1"=="--help" (
    call :show_help
    goto :eof
)

if "%1"=="-h" (
    call :show_help
    goto :eof
)

if "%1"=="" (
    echo 🚀 Starting bot (single instance)...
    echo 🎵 LavaLink server will start automatically!
    python bot.py
    goto :eof
)

echo ❌ Unknown option: %1
call :show_help
pause
exit /b 1 