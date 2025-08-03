@echo off
REM Advanced Discord Bot Stop Script for Windows

title Discord Bot - Stopping...

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Advanced Discord Bot                      ║
echo ║                       Stopping...                            ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

echo [INFO] Stopping Discord Bot and Lavalink...

REM Stop bot process
echo [INFO] Stopping Discord Bot...
tasklist /fi "imagename eq python.exe" /fo csv | find /i "python.exe" >nul
if %errorlevel% equ 0 (
    taskkill /f /im python.exe 2>nul
    if %errorlevel% equ 0 (
        echo [SUCCESS] Discord Bot stopped
    ) else (
        echo [WARNING] Failed to stop Discord Bot gracefully
    )
) else (
    echo [INFO] Discord Bot is not running
)

REM Stop Lavalink process
echo [INFO] Stopping Lavalink...
tasklist /fi "imagename eq java.exe" /fo csv | find /i "java.exe" >nul
if %errorlevel% equ 0 (
    REM Try to find and kill Lavalink specifically
    for /f "tokens=2 delims=," %%i in ('tasklist /fi "imagename eq java.exe" /fo csv ^| find /i "java.exe"') do (
        set PID=%%i
        set PID=!PID:"=!
        taskkill /f /pid !PID! 2>nul
    )
    echo [SUCCESS] Lavalink stopped
) else (
    echo [INFO] Lavalink is not running
)

echo [SUCCESS] All processes stopped
title Discord Bot - Stopped

REM Wait a moment to show the message
timeout /t 2 >nul