@echo off
echo 🎵 Installing LavaLink Server...

REM Check if Java is installed
java -version >nul 2>&1
if errorlevel 1 (
    echo ❌ Java is not installed. Please install Java 11 or higher first.
    echo Visit: https://adoptium.net/
    pause
    exit /b 1
)

echo ✅ Java detected

REM Create LavaLink directory
if not exist "lavalink" mkdir lavalink
cd lavalink

REM Download LavaLink server
echo 📥 Downloading LavaLink server...
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/lavalink-devs/Lavalink/releases/download/4.0.0/Lavalink.jar' -OutFile 'Lavalink.jar'"

if not exist "Lavalink.jar" (
    echo ❌ Failed to download LavaLink server
    pause
    exit /b 1
)

REM Create application.yml configuration
echo ⚙️ Creating LavaLink configuration...
(
echo server:
echo   port: 2333
echo   address: 127.0.0.1
echo lavalink:
echo   server:
echo     password: "youshallnotpass"
echo     sources:
echo       youtube: true
echo       bandcamp: true
echo       soundcloud: true
echo       twitch: true
echo       vimeo: true
echo       http: true
echo       local: false
echo     bufferDurationMs: 400
echo     youtubeSearchEnabled: true
echo     soundcloudSearchEnabled: true
echo     gc-warnings: true
echo.
echo metrics:
echo   prometheus:
echo     enabled: false
echo     endpoint: /metrics
echo.
echo sentry:
echo   dsn: ""
echo   environment: ""
echo.
echo logging:
echo   file:
echo     max-history: 30
echo     max-size: 1GB
echo   path: ./logs/
echo.
echo   level:
echo     root: INFO
echo     lavalink: INFO
) > application.yml

echo ✅ LavaLink installation complete!
echo.
echo 🎵 To start LavaLink server, run:
echo    cd lavalink ^&^& java -jar Lavalink.jar
echo.
echo 📝 The bot will automatically connect to LavaLink on startup.
echo 🔧 Configuration:
echo    - Port: 2333
echo    - Password: youshallnotpass
echo    - Address: 127.0.0.1
pause 