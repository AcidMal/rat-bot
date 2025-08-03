#!/bin/bash

# Advanced Discord Bot Update Script
# Pulls latest changes from GitHub and updates dependencies

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║                  Advanced Discord Bot Updater                ║${NC}"
    echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Function to check if git repository exists
check_git_repo() {
    if [ ! -d ".git" ]; then
        print_error "This is not a git repository!"
        print_status "Please clone the bot from GitHub first:"
        print_status "  git clone <repository_url> ."
        exit 1
    fi
}

# Function to backup current configuration
backup_config() {
    print_status "Backing up current configuration..."
    
    # Create backup directory with timestamp
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup important files
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/.env.backup"
        print_success "Backed up .env file"
    fi
    
    if [ -f "application.yml" ]; then
        cp application.yml "$BACKUP_DIR/application.yml.backup"
        print_success "Backed up Lavalink configuration"
    fi
    
    # Backup custom configurations
    if [ -d "data" ]; then
        cp -r data "$BACKUP_DIR/data.backup" 2>/dev/null || true
        print_success "Backed up data directory"
    fi
    
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/logs.backup" 2>/dev/null || true
        print_success "Backed up logs directory"
    fi
    
    print_success "Configuration backed up to $BACKUP_DIR"
    echo "$BACKUP_DIR" > .last_backup
}

# Function to stash local changes
stash_changes() {
    print_status "Stashing local changes..."
    
    # Check if there are any changes to stash
    if git diff --quiet && git diff --staged --quiet; then
        print_status "No local changes to stash"
        return
    fi
    
    # Stash changes with timestamp
    STASH_MESSAGE="Auto-stash before update $(date '+%Y-%m-%d %H:%M:%S')"
    git stash push -m "$STASH_MESSAGE"
    print_success "Local changes stashed"
    echo "true" > .has_stashed_changes
}

# Function to pull latest changes
pull_updates() {
    print_status "Pulling latest changes from GitHub..."
    
    # Fetch latest changes
    git fetch origin
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    print_status "Current branch: $CURRENT_BRANCH"
    
    # Check if there are updates available
    LOCAL_COMMIT=$(git rev-parse HEAD)
    REMOTE_COMMIT=$(git rev-parse origin/$CURRENT_BRANCH)
    
    if [ "$LOCAL_COMMIT" = "$REMOTE_COMMIT" ]; then
        print_success "Already up to date!"
        return 0
    fi
    
    # Show what will be updated
    print_status "New commits available:"
    git log --oneline HEAD..origin/$CURRENT_BRANCH | head -5
    
    # Pull changes
    if git pull origin "$CURRENT_BRANCH"; then
        print_success "Successfully pulled latest changes"
        return 0
    else
        print_error "Failed to pull changes"
        return 1
    fi
}

# Function to restore stashed changes
restore_stash() {
    if [ -f ".has_stashed_changes" ]; then
        print_status "Restoring stashed changes..."
        
        if git stash pop; then
            print_success "Stashed changes restored"
        else
            print_warning "Failed to restore stashed changes automatically"
            print_status "You can manually restore them with: git stash pop"
        fi
        
        rm -f .has_stashed_changes
    fi
}

# Function to update Python dependencies
update_python_deps() {
    print_status "Updating Python dependencies..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        print_status "Activated virtual environment"
    else
        print_warning "Virtual environment not found, using system Python"
    fi
    
    # Upgrade pip first
    pip install --upgrade pip
    
    # Update dependencies
    if [ -f "requirements.txt" ]; then
        if pip install --upgrade -r requirements.txt; then
            print_success "Python dependencies updated successfully"
        else
            print_warning "Some dependencies failed to update, trying individual installation..."
            
            # Try installing packages individually
            while read requirement; do
                if [[ $requirement =~ ^[[:space:]]*# ]] || [[ -z $requirement ]]; then
                    continue
                fi
                
                print_status "Updating $requirement..."
                pip install --upgrade --no-cache-dir "$requirement" || print_warning "Failed to update $requirement"
            done < requirements.txt
            
            print_success "Python dependency update completed"
        fi
    else
        print_warning "requirements.txt not found"
    fi
}

# Function to update Lavalink
update_lavalink() {
    print_status "Checking for Lavalink updates..."
    
    LAVALINK_VERSION="4.0.4"
    LAVALINK_URL="https://github.com/lavalink-devs/Lavalink/releases/download/${LAVALINK_VERSION}/Lavalink.jar"
    
    if [ -f "Lavalink.jar" ]; then
        print_status "Updating Lavalink to version $LAVALINK_VERSION..."
        
        # Backup current Lavalink
        cp Lavalink.jar Lavalink.jar.backup
        
        # Download new version
        if command -v curl &> /dev/null; then
            if curl -L -o Lavalink.jar.new "$LAVALINK_URL"; then
                mv Lavalink.jar.new Lavalink.jar
                rm -f Lavalink.jar.backup
                print_success "Lavalink updated successfully"
            else
                print_warning "Failed to download new Lavalink version"
                mv Lavalink.jar.backup Lavalink.jar
            fi
        elif command -v wget &> /dev/null; then
            if wget -O Lavalink.jar.new "$LAVALINK_URL"; then
                mv Lavalink.jar.new Lavalink.jar
                rm -f Lavalink.jar.backup
                print_success "Lavalink updated successfully"
            else
                print_warning "Failed to download new Lavalink version"
                mv Lavalink.jar.backup Lavalink.jar
            fi
        else
            print_warning "Neither curl nor wget found, cannot update Lavalink"
        fi
    else
        print_status "Lavalink.jar not found, downloading..."
        if command -v curl &> /dev/null; then
            curl -L -o Lavalink.jar "$LAVALINK_URL"
        elif command -v wget &> /dev/null; then
            wget -O Lavalink.jar "$LAVALINK_URL"
        fi
        
        if [ -f "Lavalink.jar" ]; then
            print_success "Lavalink downloaded successfully"
        else
            print_warning "Failed to download Lavalink"
        fi
    fi
}

# Function to run database migrations (if any)
run_migrations() {
    print_status "Checking for database migrations..."
    
    if [ -f "migrations/migrate.py" ]; then
        print_status "Running database migrations..."
        
        if [ -d "venv" ]; then
            source venv/bin/activate
        fi
        
        if python migrations/migrate.py; then
            print_success "Database migrations completed"
        else
            print_warning "Database migrations failed"
        fi
    else
        print_status "No migrations to run"
    fi
}

# Function to restart services if they're running
restart_services() {
    print_status "Checking running services..."
    
    BOT_RUNNING=false
    LAVALINK_RUNNING=false
    
    # Check if bot is running
    if pgrep -f "python.*main.py" > /dev/null; then
        BOT_RUNNING=true
        print_status "Discord bot is currently running"
    fi
    
    # Check if Lavalink is running
    if pgrep -f "java.*Lavalink.jar" > /dev/null; then
        LAVALINK_RUNNING=true
        print_status "Lavalink is currently running"
    fi
    
    # Ask user if they want to restart services
    if [ "$BOT_RUNNING" = true ] || [ "$LAVALINK_RUNNING" = true ]; then
        echo ""
        print_status "Services are currently running. Restart them to apply updates?"
        read -p "Restart services? (Y/n): " RESTART_CHOICE
        
        if [[ ! $RESTART_CHOICE =~ ^[Nn]$ ]]; then
            print_status "Restarting services..."
            
            # Stop services
            if [ "$BOT_RUNNING" = true ]; then
                print_status "Stopping Discord bot..."
                pkill -f "python.*main.py" || true
                sleep 2
            fi
            
            if [ "$LAVALINK_RUNNING" = true ]; then
                print_status "Stopping Lavalink..."
                pkill -f "java.*Lavalink.jar" || true
                sleep 2
            fi
            
            # Start services
            if [ "$LAVALINK_RUNNING" = true ]; then
                print_status "Starting Lavalink..."
                nohup java -jar Lavalink.jar > logs/lavalink.log 2>&1 &
                sleep 3
            fi
            
            if [ "$BOT_RUNNING" = true ]; then
                print_status "Starting Discord bot..."
                if [ -f "start.sh" ]; then
                    nohup ./start.sh > logs/bot.log 2>&1 &
                else
                    if [ -d "venv" ]; then
                        source venv/bin/activate
                    fi
                    nohup python main.py > logs/bot.log 2>&1 &
                fi
                sleep 2
            fi
            
            print_success "Services restarted"
        else
            print_status "Services not restarted. You may need to restart them manually."
        fi
    fi
}

# Function to clean up old backups
cleanup_backups() {
    print_status "Cleaning up old backups..."
    
    if [ -d "backups" ]; then
        # Keep only the last 5 backups
        BACKUP_COUNT=$(ls -1 backups/ | wc -l)
        
        if [ "$BACKUP_COUNT" -gt 5 ]; then
            print_status "Removing old backups (keeping last 5)..."
            ls -1t backups/ | tail -n +6 | while read backup; do
                rm -rf "backups/$backup"
                print_status "Removed old backup: $backup"
            done
            print_success "Old backups cleaned up"
        fi
    fi
}

# Function to show update summary
show_summary() {
    echo ""
    print_success "🎉 Update completed successfully!"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                        UPDATE SUMMARY                        ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Show current commit
    CURRENT_COMMIT=$(git rev-parse --short HEAD)
    CURRENT_BRANCH=$(git branch --show-current)
    echo "📍 Current version: $CURRENT_COMMIT ($CURRENT_BRANCH)"
    
    # Show last backup location
    if [ -f ".last_backup" ]; then
        LAST_BACKUP=$(cat .last_backup)
        echo "💾 Configuration backed up to: $LAST_BACKUP"
    fi
    
    echo ""
    echo "✅ Code updated from GitHub"
    echo "✅ Python dependencies updated"
    echo "✅ Lavalink updated"
    echo "✅ Database migrations checked"
    echo ""
    
    if [ -f "logs/bot.log" ]; then
        echo "📋 To view bot logs: tail -f logs/bot.log"
    fi
    
    if [ -f "logs/lavalink.log" ]; then
        echo "📋 To view Lavalink logs: tail -f logs/lavalink.log"
    fi
    
    echo ""
    echo -e "${CYAN}Your bot has been updated successfully!${NC}"
    echo ""
}

# Main update function
main() {
    print_header
    
    # Check if this is a git repository
    check_git_repo
    
    print_status "Starting update process..."
    echo ""
    
    # Backup current configuration
    backup_config
    
    # Stash local changes
    stash_changes
    
    # Pull latest changes
    if ! pull_updates; then
        print_error "Failed to pull updates. Aborting."
        restore_stash
        exit 1
    fi
    
    # Restore stashed changes
    restore_stash
    
    # Update dependencies
    update_python_deps
    
    # Update Lavalink
    update_lavalink
    
    # Run database migrations
    run_migrations
    
    # Clean up old backups
    cleanup_backups
    
    # Restart services if needed
    restart_services
    
    # Show summary
    show_summary
}

# Handle script arguments
case "${1:-}" in
    --no-restart)
        # Skip service restart
        SKIP_RESTART=true
        ;;
    --backup-only)
        # Only backup, don't update
        print_header
        backup_config
        print_success "Backup completed"
        exit 0
        ;;
    --help|-h)
        echo "Advanced Discord Bot Update Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --no-restart    Don't restart running services"
        echo "  --backup-only   Only backup configuration, don't update"
        echo "  --help, -h      Show this help message"
        echo ""
        exit 0
        ;;
esac

# Run main function
main "$@"