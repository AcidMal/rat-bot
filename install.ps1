# Advanced Discord Bot Installation Script for Windows
Write-Host "Advanced Discord Bot Installer v2.0" -ForegroundColor Magenta
Write-Host "===================================" -ForegroundColor Magenta
Write-Host "This script will install:" -ForegroundColor White
Write-Host "- Java (required for Lavalink)" -ForegroundColor White
Write-Host "- Python dependencies (including yt-dlp)" -ForegroundColor White
Write-Host "- Lavalink music server" -ForegroundColor White
Write-Host "- Bot configuration" -ForegroundColor White
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "[WARNING] Not running as administrator. Some features may not work properly." -ForegroundColor Yellow
    Write-Host "[INFO] Consider running as administrator for best results." -ForegroundColor Yellow
    Write-Host ""
}

# Check FFmpeg
Write-Host "[INFO] Checking FFmpeg..." -ForegroundColor Cyan
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-String "ffmpeg version" | Select-Object -First 1
    if ($ffmpegVersion) {
        Write-Host "[SUCCESS] FFmpeg found: $ffmpegVersion" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] FFmpeg not found. Installing FFmpeg..." -ForegroundColor Yellow
        try {
            winget install "FFmpeg (Essentials Build)" --accept-source-agreements --accept-package-agreements
            Write-Host "[SUCCESS] FFmpeg installed" -ForegroundColor Green
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        } catch {
            Write-Host "[ERROR] Failed to install FFmpeg automatically." -ForegroundColor Red
            Write-Host "[INFO] Please install FFmpeg manually from: https://ffmpeg.org/download.html" -ForegroundColor Cyan
            Write-Host "[INFO] After installing FFmpeg, run this script again." -ForegroundColor Cyan
            exit 1
        }
    }
} catch {
    Write-Host "[WARNING] FFmpeg not found. Attempting to install..." -ForegroundColor Yellow
    try {
        winget install "FFmpeg (Essentials Build)" --accept-source-agreements --accept-package-agreements
        Write-Host "[SUCCESS] FFmpeg installed" -ForegroundColor Green
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "[ERROR] Failed to install FFmpeg automatically." -ForegroundColor Red
        Write-Host "[INFO] Please install FFmpeg manually from: https://ffmpeg.org/download.html" -ForegroundColor Cyan
        Write-Host "[INFO] After installing FFmpeg, run this script again." -ForegroundColor Cyan
        exit 1
    }
}

# Check Java
Write-Host "[INFO] Checking Java..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-String "version" | Select-Object -First 1
    if ($javaVersion) {
        Write-Host "[SUCCESS] Java found: $javaVersion" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] Java not found. Installing Java..." -ForegroundColor Yellow
        # Install Java using winget if available
        try {
            winget install Microsoft.OpenJDK.21 --accept-source-agreements --accept-package-agreements
            Write-Host "[SUCCESS] Java installed" -ForegroundColor Green
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        } catch {
            Write-Host "[ERROR] Failed to install Java automatically." -ForegroundColor Red
            Write-Host "[INFO] Please install Java manually from: https://adoptium.net/" -ForegroundColor Cyan
            Write-Host "[INFO] After installing Java, run this script again." -ForegroundColor Cyan
            exit 1
        }
    }
} catch {
    Write-Host "[WARNING] Java not found. Attempting to install..." -ForegroundColor Yellow
    try {
        winget install Microsoft.OpenJDK.21 --accept-source-agreements --accept-package-agreements
        Write-Host "[SUCCESS] Java installed" -ForegroundColor Green
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "[ERROR] Failed to install Java automatically." -ForegroundColor Red
        Write-Host "[INFO] Please install Java manually from: https://adoptium.net/" -ForegroundColor Cyan
        Write-Host "[INFO] After installing Java, run this script again." -ForegroundColor Cyan
        exit 1
    }
}

# Check Python
Write-Host "[INFO] Checking Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "[SUCCESS] Python found: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Python not found. Installing Python..." -ForegroundColor Red
        try {
            winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
            Write-Host "[SUCCESS] Python installed" -ForegroundColor Green
            # Refresh environment variables
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        } catch {
            Write-Host "[ERROR] Failed to install Python automatically." -ForegroundColor Red
            Write-Host "[INFO] Please install Python 3.11+ from: https://python.org" -ForegroundColor Cyan
            exit 1
        }
    }
} catch {
    Write-Host "[ERROR] Python not found. Installing Python..." -ForegroundColor Red
    try {
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        Write-Host "[SUCCESS] Python installed" -ForegroundColor Green
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } catch {
        Write-Host "[ERROR] Failed to install Python automatically." -ForegroundColor Red
        Write-Host "[INFO] Please install Python 3.11+ from: https://python.org" -ForegroundColor Cyan
        exit 1
    }
}

# Get Discord token
Write-Host "[INFO] Enter your Discord Bot Token:" -ForegroundColor Cyan
$token = Read-Host -AsSecureString
$tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))

if ([string]::IsNullOrEmpty($tokenPlain)) {
    Write-Host "[ERROR] Bot token is required!" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "[INFO] Creating Python virtual environment..." -ForegroundColor Cyan
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "[SUCCESS] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[INFO] Virtual environment already exists" -ForegroundColor Yellow
}

# Install dependencies
Write-Host "[INFO] Installing Python dependencies..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    pip install discord.py wavelink motor pymongo fastapi uvicorn loguru aioredis psutil colorama python-dotenv aiofiles aiohttp yt-dlp cryptography pydantic PyNaCl
}
Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green

# Download Lavalink
Write-Host "[INFO] Setting up Lavalink music server..." -ForegroundColor Cyan
if (!(Test-Path "Lavalink-latest.jar")) {
    try {
        Write-Host "[INFO] Downloading Lavalink v4.0.8..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri "https://github.com/lavalink-devs/Lavalink/releases/download/4.0.8/Lavalink.jar" -OutFile "Lavalink-latest.jar" -UseBasicParsing
        Write-Host "[SUCCESS] Lavalink downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Failed to download Lavalink automatically" -ForegroundColor Yellow
        Write-Host "[INFO] Please download Lavalink manually from: https://github.com/lavalink-devs/Lavalink/releases" -ForegroundColor Cyan
    }
} else {
    Write-Host "[INFO] Lavalink already exists" -ForegroundColor Yellow
}

# Create plugins directory and download plugins
Write-Host "[INFO] Setting up Lavalink plugins..." -ForegroundColor Cyan
if (!(Test-Path "plugins")) {
    New-Item -ItemType Directory -Path "plugins" -Force | Out-Null
}

# Download LavaSrc plugin for additional music sources
if (!(Test-Path "plugins\lavasrc-plugin-4.2.0.jar")) {
    try {
        Write-Host "[INFO] Downloading LavaSrc plugin..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri "https://maven.topi.wtf/releases/com/github/topi314/lavasrc/lavasrc-plugin/4.2.0/lavasrc-plugin-4.2.0.jar" -OutFile "plugins\lavasrc-plugin-4.2.0.jar" -UseBasicParsing
        Write-Host "[SUCCESS] LavaSrc plugin downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Failed to download LavaSrc plugin" -ForegroundColor Yellow
    }
}

# Download LavaSearch plugin for advanced search
if (!(Test-Path "plugins\lavasearch-plugin-1.0.0.jar")) {
    try {
        Write-Host "[INFO] Downloading LavaSearch plugin..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri "https://maven.topi.wtf/releases/com/github/topi314/lavasearch/lavasearch-plugin/1.0.0/lavasearch-plugin-1.0.0.jar" -OutFile "plugins\lavasearch-plugin-1.0.0.jar" -UseBasicParsing
        Write-Host "[SUCCESS] LavaSearch plugin downloaded" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Failed to download LavaSearch plugin" -ForegroundColor Yellow
    }
}

# Create directories
Write-Host "[INFO] Creating directories..." -ForegroundColor Cyan
$dirs = @("logs", "data", "backups")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "[SUCCESS] Directories created" -ForegroundColor Green

# Create .env file
Write-Host "[INFO] Creating configuration file..." -ForegroundColor Cyan
$envContent = "# Discord Bot Configuration`nDISCORD_TOKEN=$tokenPlain`nGUILD_ID=`nPREFIX=!`nEMBED_COLOR=0x7289da`n`n# Database Configuration`nDATABASE_TYPE=json`nMONGODB_URI=mongodb://localhost:27017`nDATABASE_NAME=discord_bot`nJSON_DATABASE_PATH=data/database.json`n`n# Lavalink Configuration`nLAVALINK_HOST=localhost`nLAVALINK_PORT=2333`nLAVALINK_PASSWORD=youshallnotpass`nLAVALINK_SSL=false`n`n# Logging Configuration`nLOG_LEVEL=INFO`nLOG_FILE=logs/bot.log`n"
$envContent | Out-File -FilePath ".env" -Encoding UTF8
Write-Host "[SUCCESS] Configuration file created" -ForegroundColor Green

# Test Java installation
Write-Host "[INFO] Testing Java installation..." -ForegroundColor Cyan
try {
    $javaTest = java -version 2>&1
    Write-Host "[SUCCESS] Java is working properly" -ForegroundColor Green
} catch {
    Write-Host "[WARNING] Java test failed. You may need to restart your terminal." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Installation completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "📦 Installed Components:" -ForegroundColor Cyan
Write-Host "✅ Java (for Lavalink)" -ForegroundColor White
Write-Host "✅ Python dependencies (including yt-dlp)" -ForegroundColor White
Write-Host "✅ Lavalink music server v4.0.8" -ForegroundColor White
Write-Host "✅ LavaSrc and LavaSearch plugins" -ForegroundColor White
Write-Host "✅ Bot configuration" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start the bot: .\start.bat" -ForegroundColor White
Write-Host "2. View logs: Get-Content logs\bot.log -Tail 50 -Wait" -ForegroundColor White
Write-Host "3. Test music: !play yt:your favorite song" -ForegroundColor White
Write-Host ""
Write-Host "🎵 Music Features:" -ForegroundColor Cyan
Write-Host "• Regular search: !play song name (uses SoundCloud/Bandcamp)" -ForegroundColor White
Write-Host "• YouTube search: !play yt:song name (direct YouTube via yt-dlp)" -ForegroundColor White
Write-Host "• Automatic fallback: YouTube failures auto-retry with alternatives" -ForegroundColor White
Write-Host ""
Write-Host "🍪 Optional YouTube Enhancement:" -ForegroundColor Yellow
Write-Host "• For better YouTube access, set up cookies:" -ForegroundColor White
Write-Host "  python setup_cookies.py" -ForegroundColor Gray
Write-Host "• This enables age-restricted and region-locked content" -ForegroundColor White
Write-Host ""
Write-Host "📖 For help: !help" -ForegroundColor Cyan
Write-Host ""