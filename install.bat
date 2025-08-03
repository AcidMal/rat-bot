@echo off
REM Advanced Discord Bot Installation Script for Windows
REM Batch file wrapper for PowerShell script

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                  Advanced Discord Bot Installer              ║
echo ║                        Windows Batch                         ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if PowerShell is available
powershell -Command "exit 0" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PowerShell is not available!
    echo Please install PowerShell or use install.ps1 directly
    pause
    exit /b 1
)

REM Check execution policy
echo [INFO] Checking PowerShell execution policy...
for /f "tokens=*" %%i in ('powershell -Command "Get-ExecutionPolicy"') do set EXEC_POLICY=%%i

if "%EXEC_POLICY%"=="Restricted" (
    echo [WARNING] PowerShell execution policy is Restricted
    echo [INFO] Attempting to set execution policy for current user...
    powershell -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force" >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to set execution policy
        echo Please run the following command as Administrator:
        echo Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
        pause
        exit /b 1
    )
    echo [SUCCESS] Execution policy updated
)

REM Run PowerShell installation script
echo [INFO] Starting PowerShell installation script...
echo.

powershell -ExecutionPolicy Bypass -File "install.ps1"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed!
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Installation completed!
echo You can now run start.bat to start your Discord bot
pause