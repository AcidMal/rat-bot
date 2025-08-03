# Advanced Discord Bot Update Script for Windows
# PowerShell script for updating from GitHub

param(
    [switch]$NoRestart,
    [switch]$BackupOnly
)

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Cyan"
    Purple = "Magenta"
}

function Write-Header {
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Purple
    Write-Host "║                  Advanced Discord Bot Updater                ║" -ForegroundColor $Colors.Purple
    Write-Host "║                     Windows PowerShell                       ║" -ForegroundColor $Colors.Purple
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Purple
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Colors.Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Colors.Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Colors.Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Colors.Red
}

function Test-GitRepository {
    if (!(Test-Path ".git")) {
        Write-Error "This is not a git repository!"
        Write-Status "Please clone the bot from GitHub first:"
        Write-Status "  git clone <repository_url> ."
        return $false
    }
    return $true
}

function Backup-Configuration {
    Write-Status "Backing up current configuration..."
    
    # Create backup directory with timestamp
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups\$timestamp"
    
    if (!(Test-Path "backups")) {
        New-Item -ItemType Directory -Path "backups" -Force | Out-Null
    }
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # Backup important files
    $filesToBackup = @(".env", "application.yml")
    
    foreach ($file in $filesToBackup) {
        if (Test-Path $file) {
            Copy-Item $file "$backupDir\$file.backup" -Force
            Write-Success "Backed up $file"
        }
    }
    
    # Backup directories
    $dirsToBackup = @("data", "logs")
    
    foreach ($dir in $dirsToBackup) {
        if (Test-Path $dir) {
            Copy-Item $dir "$backupDir\$dir.backup" -Recurse -Force
            Write-Success "Backed up $dir directory"
        }
    }
    
    Write-Success "Configuration backed up to $backupDir"
    $backupDir | Out-File ".last_backup" -Encoding UTF8
    
    return $backupDir
}

function Save-LocalChanges {
    Write-Status "Saving local changes..."
    
    # Check if there are any changes to stash
    $status = git status --porcelain
    if ([string]::IsNullOrEmpty($status)) {
        Write-Status "No local changes to save"
        return $true
    }
    
    # Stash changes with timestamp
    $stashMessage = "Auto-stash before update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    
    try {
        git stash push -m $stashMessage
        Write-Success "Local changes saved"
        "true" | Out-File ".has_stashed_changes" -Encoding UTF8
        return $true
    }
    catch {
        Write-Error "Failed to save local changes: $_"
        return $false
    }
}

function Get-Updates {
    Write-Status "Pulling latest changes from GitHub..."
    
    try {
        # Fetch latest changes
        git fetch origin
        
        # Get current branch
        $currentBranch = git branch --show-current
        Write-Status "Current branch: $currentBranch"
        
        # Check if there are updates available
        $localCommit = git rev-parse HEAD
        $remoteCommit = git rev-parse "origin/$currentBranch"
        
        if ($localCommit -eq $remoteCommit) {
            Write-Success "Already up to date!"
            return $true
        }
        
        # Show what will be updated
        Write-Status "New commits available:"
        $commits = git log --oneline HEAD.."origin/$currentBranch" | Select-Object -First 5
        $commits | ForEach-Object { Write-Host "  $_" }
        
        # Pull changes
        git pull origin $currentBranch
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully pulled latest changes"
            return $true
        }
        else {
            Write-Error "Failed to pull changes"
            return $false
        }
    }
    catch {
        Write-Error "Failed to pull updates: $_"
        return $false
    }
}

function Restore-LocalChanges {
    if (Test-Path ".has_stashed_changes") {
        Write-Status "Restoring saved changes..."
        
        try {
            git stash pop
            Write-Success "Saved changes restored"
        }
        catch {
            Write-Warning "Failed to restore saved changes automatically"
            Write-Status "You can manually restore them with: git stash pop"
        }
        
        Remove-Item ".has_stashed_changes" -Force -ErrorAction SilentlyContinue
    }
}

function Update-PythonDependencies {
    Write-Status "Updating Python dependencies..."
    
    # Check if virtual environment exists
    if (!(Test-Path "venv")) {
        Write-Warning "Virtual environment not found, using system Python"
    }
    else {
        Write-Status "Activating virtual environment..."
        & "venv\Scripts\Activate.ps1"
    }
    
    try {
        # Upgrade pip first
        python -m pip install --upgrade pip
        
        # Update dependencies
        if (Test-Path "requirements.txt") {
            pip install --upgrade -r requirements.txt
            Write-Success "Python dependencies updated successfully"
        }
        else {
            Write-Warning "requirements.txt not found"
        }
        
        return $true
    }
    catch {
        Write-Warning "Some dependencies failed to update: $_"
        
        # Try installing packages individually
        Write-Status "Trying individual package installation..."
        
        if (Test-Path "requirements.txt") {
            $requirements = Get-Content "requirements.txt" | Where-Object { $_ -notmatch "^\s*#" -and $_ -ne "" }
            
            foreach ($requirement in $requirements) {
                Write-Status "Updating $requirement..."
                try {
                    pip install --upgrade --no-cache-dir $requirement
                }
                catch {
                    Write-Warning "Failed to update $requirement"
                }
            }
        }
        
        Write-Success "Python dependency update completed"
        return $true
    }
}

function Update-Lavalink {
    Write-Status "Checking for Lavalink updates..."
    
    $lavalinkVersion = "4.0.4"
    $lavalinkUrl = "https://github.com/lavalink-devs/Lavalink/releases/download/$lavalinkVersion/Lavalink.jar"
    
    if (Test-Path "Lavalink.jar") {
        Write-Status "Updating Lavalink to version $lavalinkVersion..."
        
        # Backup current Lavalink
        Copy-Item "Lavalink.jar" "Lavalink.jar.backup" -Force
        
        try {
            # Download new version
            Write-Status "Downloading new Lavalink version..."
            Invoke-WebRequest -Uri $lavalinkUrl -OutFile "Lavalink.jar.new" -UseBasicParsing
            
            # Replace old version
            Move-Item "Lavalink.jar.new" "Lavalink.jar" -Force
            Remove-Item "Lavalink.jar.backup" -Force
            
            Write-Success "Lavalink updated successfully"
        }
        catch {
            Write-Warning "Failed to download new Lavalink version: $_"
            if (Test-Path "Lavalink.jar.backup") {
                Move-Item "Lavalink.jar.backup" "Lavalink.jar" -Force
                Write-Status "Restored backup Lavalink.jar"
            }
        }
    }
    else {
        Write-Status "Lavalink.jar not found, downloading..."
        try {
            Invoke-WebRequest -Uri $lavalinkUrl -OutFile "Lavalink.jar" -UseBasicParsing
            Write-Success "Lavalink downloaded successfully"
        }
        catch {
            Write-Warning "Failed to download Lavalink: $_"
        }
    }
}

function Test-RunningProcesses {
    $botRunning = Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    $lavalinkRunning = Get-Process java -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*Lavalink.jar*" }
    
    return @{
        BotRunning = $botRunning -ne $null
        LavalinkRunning = $lavalinkRunning -ne $null
    }
}

function Restart-Services {
    Write-Status "Checking running services..."
    
    $processes = Test-RunningProcesses
    
    if ($processes.BotRunning -or $processes.LavalinkRunning) {
        Write-Host ""
        Write-Status "Services are currently running. Restart them to apply updates?"
        $restartChoice = Read-Host "Restart services? (Y/n)"
        
        if ($restartChoice -notmatch "^[Nn]") {
            Write-Status "Restarting services..."
            
            # Stop services
            if ($processes.BotRunning) {
                Write-Status "Stopping Discord bot..."
                Get-Process python | Where-Object { $_.CommandLine -like "*main.py*" } | Stop-Process -Force
                Start-Sleep -Seconds 2
            }
            
            if ($processes.LavalinkRunning) {
                Write-Status "Stopping Lavalink..."
                Get-Process java | Where-Object { $_.CommandLine -like "*Lavalink.jar*" } | Stop-Process -Force
                Start-Sleep -Seconds 2
            }
            
            # Start services
            if ($processes.LavalinkRunning -and (Test-Path "Lavalink.jar")) {
                Write-Status "Starting Lavalink..."
                Start-Process -FilePath "java" -ArgumentList "-jar", "Lavalink.jar" -WindowStyle Hidden
                Start-Sleep -Seconds 3
            }
            
            if ($processes.BotRunning) {
                Write-Status "Starting Discord bot..."
                if (Test-Path "start.bat") {
                    Start-Process -FilePath "start.bat" -WindowStyle Hidden
                }
                else {
                    if (Test-Path "venv") {
                        & "venv\Scripts\Activate.ps1"
                    }
                    Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Hidden
                }
                Start-Sleep -Seconds 2
            }
            
            Write-Success "Services restarted"
        }
        else {
            Write-Status "Services not restarted. You may need to restart them manually."
        }
    }
}

function Remove-OldBackups {
    Write-Status "Cleaning up old backups..."
    
    if (Test-Path "backups") {
        $backups = Get-ChildItem "backups" | Sort-Object CreationTime -Descending
        
        if ($backups.Count -gt 5) {
            Write-Status "Removing old backups (keeping last 5)..."
            $backups | Select-Object -Skip 5 | ForEach-Object {
                Remove-Item $_.FullName -Recurse -Force
                Write-Status "Removed old backup: $($_.Name)"
            }
            Write-Success "Old backups cleaned up"
        }
    }
}

function Show-UpdateSummary {
    Write-Host ""
    Write-Success "🎉 Update completed successfully!"
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor $Colors.Green
    Write-Host "║                        UPDATE SUMMARY                        ║" -ForegroundColor $Colors.Green
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor $Colors.Green
    Write-Host ""
    
    # Show current commit
    $currentCommit = git rev-parse --short HEAD
    $currentBranch = git branch --show-current
    Write-Host "📍 Current version: $currentCommit ($currentBranch)"
    
    # Show last backup location
    if (Test-Path ".last_backup") {
        $lastBackup = Get-Content ".last_backup"
        Write-Host "💾 Configuration backed up to: $lastBackup"
    }
    
    Write-Host ""
    Write-Host "✅ Code updated from GitHub"
    Write-Host "✅ Python dependencies updated"
    Write-Host "✅ Lavalink updated"
    Write-Host ""
    
    if (Test-Path "logs\bot.log") {
        Write-Host "📋 To view bot logs: Get-Content logs\bot.log -Tail 50 -Wait"
    }
    
    if (Test-Path "logs\lavalink.log") {
        Write-Host "📋 To view Lavalink logs: Get-Content logs\lavalink.log -Tail 50 -Wait"
    }
    
    Write-Host ""
    Write-Host "Your bot has been updated successfully!" -ForegroundColor $Colors.Blue
    Write-Host ""
}

# Main update function
function Start-Update {
    Write-Header
    
    # Check if this is a git repository
    if (!(Test-GitRepository)) {
        exit 1
    }
    
    Write-Status "Starting update process..."
    Write-Host ""
    
    # Backup current configuration
    $backupDir = Backup-Configuration
    
    if ($BackupOnly) {
        Write-Success "Backup completed: $backupDir"
        return
    }
    
    # Save local changes
    if (!(Save-LocalChanges)) {
        Write-Error "Failed to save local changes. Aborting."
        exit 1
    }
    
    # Pull latest changes
    if (!(Get-Updates)) {
        Write-Error "Failed to pull updates. Aborting."
        Restore-LocalChanges
        exit 1
    }
    
    # Restore local changes
    Restore-LocalChanges
    
    # Update dependencies
    Update-PythonDependencies | Out-Null
    
    # Update Lavalink
    Update-Lavalink
    
    # Clean up old backups
    Remove-OldBackups
    
    # Restart services if needed
    if (!$NoRestart) {
        Restart-Services
    }
    
    # Show summary
    Show-UpdateSummary
}

# Handle script arguments
switch ($args[0]) {
    "--help" {
        Write-Host "Advanced Discord Bot Update Script for Windows"
        Write-Host ""
        Write-Host "Usage: .\update.ps1 [options]"
        Write-Host ""
        Write-Host "Options:"
        Write-Host "  -NoRestart     Don't restart running services"
        Write-Host "  -BackupOnly    Only backup configuration, don't update"
        Write-Host "  --help         Show this help message"
        Write-Host ""
        exit 0
    }
}

# Run main function
try {
    Start-Update
}
catch {
    Write-Error "Update failed: $_"
    Write-Host "Please check the error message above and try again."
    exit 1
}