@echo off
REM Advanced Discord Bot Update Script for Windows
REM Batch file wrapper for PowerShell script

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  Advanced Discord Bot Updater                ║
echo ║                        Windows Batch                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if this is a git repository
if not exist .git (
    echo [ERROR] This is not a git repository!
    echo Please clone the bot from GitHub first
    pause
    exit /b 1
)

REM Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell is not available!
    echo Please install PowerShell or use update.ps1 directly
    pause
    exit /b 1
)

REM Parse command line arguments
set ARGS=
if "%1"=="--no-restart" set ARGS=-NoRestart
if "%1"=="--backup-only" set ARGS=-BackupOnly

REM Run PowerShell update script
echo [INFO] Starting PowerShell update script...
echo.

if defined ARGS (
    powershell -ExecutionPolicy Bypass -File "update.ps1" %ARGS%
) else (
    powershell -ExecutionPolicy Bypass -File "update.ps1"
)

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Update failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Update completed!
pause