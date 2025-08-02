@echo off
echo 🎵 Starting LavaLink Server...

if not exist "lavalink" (
    echo ❌ LavaLink not installed. Run install_lavalink.bat first.
    pause
    exit /b 1
)

cd lavalink

if not exist "Lavalink.jar" (
    echo ❌ LavaLink.jar not found. Run install_lavalink.bat first.
    pause
    exit /b 1
)

echo 🚀 Starting LavaLink server on port 2333...
echo 📝 Press Ctrl+C to stop the server
echo.

java -jar Lavalink.jar 