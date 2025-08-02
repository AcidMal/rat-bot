# FFmpeg Installation Guide

FFmpeg is required for the music bot functionality. Follow the instructions below for your operating system.

## Windows

### Method 1: Using Chocolatey (Recommended)
1. Install Chocolatey if you haven't already: https://chocolatey.org/install
2. Open PowerShell as Administrator
3. Run: `choco install ffmpeg`

### Method 2: Manual Installation
1. Go to [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Download the Windows builds
3. Extract the ZIP file to a folder (e.g., `C:\ffmpeg`)
4. Add the `bin` folder to your system PATH:
   - Open System Properties → Advanced → Environment Variables
   - Edit the "Path" variable
   - Add the path to the bin folder (e.g., `C:\ffmpeg\bin`)
5. Restart your command prompt
6. Verify installation: `ffmpeg -version`

## macOS

### Using Homebrew (Recommended)
```bash
brew install ffmpeg
```

### Using MacPorts
```bash
sudo port install ffmpeg
```

## Linux

### Ubuntu/Debian
```bash
sudo apt update
sudo apt install ffmpeg
```

### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum install ffmpeg

# Fedora
sudo dnf install ffmpeg
```

### Arch Linux
```bash
sudo pacman -S ffmpeg
```

## Verify Installation

After installation, verify FFmpeg is working by running:
```bash
ffmpeg -version
```

You should see output similar to:
```
ffmpeg version 4.4.2 Copyright (c) 2000-2021 the FFmpeg developers
built with gcc 9 (Ubuntu 9.4.0-1ubuntu1~20.04.1)
...
```

## Troubleshooting

### "ffmpeg command not found"
- Make sure FFmpeg is installed correctly
- Check that the PATH environment variable includes the FFmpeg bin directory
- Restart your terminal/command prompt after installation

### Permission errors on Linux/macOS
- Use `sudo` when installing with package managers
- Make sure you have administrator privileges

### Windows PATH issues
- Double-check that the FFmpeg bin folder is added to the system PATH
- Restart your computer after adding to PATH
- Try running the command from a new command prompt window 