@echo off
REM Advanced Discord Bot Start Script for Windows

title Discord Bot - Starting...

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Advanced Discord Bot                      ║
echo ║                       Starting Up...                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found!
    echo Please run install.bat or copy env.example to .env
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Lavalink should be started
if exist Lavalink-latest.jar (
    echo [INFO] Checking if Lavalink is running...
    tasklist /fi "imagename eq java.exe" /fo csv | find /i "java.exe" >nul
    if errorlevel 1 (
        echo [INFO] Starting Lavalink server...
        if not exist logs mkdir logs
        start /b java -jar Lavalink-latest.jar > logs\lavalink.log 2>&1
        timeout /t 5 >nul
        echo [SUCCESS] Lavalink started
    ) else (
        echo [INFO] Lavalink is already running
    )
) else (
    echo [WARNING] Lavalink-latest.jar not found - music features will not work
    echo Please run install.bat to download Lavalink
)

REM Start the bot
echo [INFO] Starting Discord Bot...
title Discord Bot - Running

python main.py

REM If we get here, the bot has stopped
echo.
echo [INFO] Bot has stopped
title Discord Bot - Stopped
pause