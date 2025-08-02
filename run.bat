@echo off
REM Rat Bot Run Script for Windows
REM This script runs the bot with various options

echo 🤖 Rat Bot Run Script
echo ====================

REM Check if virtual environment exists
if not exist venv (
    echo ❌ Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please run install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check command line arguments
if "%1"=="--sharded" (
    echo Starting bot with automatic sharding...
    python run_sharded.py
) else if "%1"=="--shard-manager" (
    echo Starting shard manager...
    if not "%2"=="" (
        python shard_manager.py --shards %2
    ) else (
        echo Usage: run.bat --shard-manager ^<number_of_shards^>
        pause
        exit /b 1
    )
) else if "%1"=="--help" (
    echo Usage:
    echo   run.bat                    - Run bot normally (single instance)
    echo   run.bat --sharded          - Run bot with automatic sharding
    echo   run.bat --shard-manager N  - Run shard manager with N shards
    echo   run.bat --help             - Show this help message
    pause
    exit /b 0
) else (
    echo Starting bot normally...
    python bot.py
) 