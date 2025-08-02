#!/usr/bin/env python3
"""
Rat Bot Update Script
This script updates the bot without requiring a full reinstallation.
"""

import subprocess
import sys
import os
import shutil
import json
import requests
from datetime import datetime

def print_header():
    """Print the update script header."""
    print("🔄 Rat Bot Update Script")
    print("=======================")
    print()

def check_git():
    """Check if git is available."""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def get_current_version():
    """Get the current bot version."""
    try:
        with open('config.py', 'r') as f:
            for line in f:
                if 'BOT_VERSION' in line and '=' in line:
                    version = line.split('=')[1].strip().strip('"\'')
                    return version
    except FileNotFoundError:
        pass
    return "Unknown"

def update_dependencies():
    """Update Python dependencies."""
    print("📦 Updating Python dependencies...")
    
    try:
        # Activate virtual environment if it exists
        if os.path.exists('venv'):
            if os.name == 'nt':  # Windows
                activate_script = os.path.join('venv', 'Scripts', 'activate.bat')
                python_exe = os.path.join('venv', 'Scripts', 'python.exe')
            else:  # Unix/Linux/Mac
                activate_script = os.path.join('venv', 'bin', 'activate')
                python_exe = os.path.join('venv', 'bin', 'python')
        else:
            python_exe = sys.executable
        
        # Update pip
        print("  Upgrading pip...")
        subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      capture_output=True, check=True)
        
        # Update requirements
        print("  Installing/updating requirements...")
        subprocess.run([python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      capture_output=True, check=True)
        
        # Update yt-dlp specifically (for music fixes)
        print("  Updating yt-dlp...")
        subprocess.run([python_exe, '-m', 'pip', 'install', '--upgrade', 'yt-dlp'], 
                      capture_output=True, check=True)
        
        print("✅ Dependencies updated successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error updating dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def backup_database():
    """Create a backup of the database."""
    if os.path.exists('data/bot.db'):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'data/bot_backup_{timestamp}.db'
        
        try:
            shutil.copy2('data/bot.db', backup_path)
            print(f"💾 Database backed up to: {backup_path}")
            return True
        except Exception as e:
            print(f"⚠️  Could not backup database: {e}")
            return False
    return True

def update_database_schema():
    """Update database schema if needed."""
    print("🗄️  Checking database schema...")
    
    try:
        import sqlite3
        
        # Create database connection
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # Get current tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        # Define required tables and their schemas
        required_tables = {
            'mod_logs': '''
                CREATE TABLE IF NOT EXISTS mod_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'user_warnings': '''
                CREATE TABLE IF NOT EXISTS user_warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'custom_commands': '''
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    command_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'server_settings': '''
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id INTEGER PRIMARY KEY,
                    mod_log_channel INTEGER,
                    welcome_channel INTEGER,
                    welcome_message TEXT,
                    prefix TEXT DEFAULT '!',
                    auto_role INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'user_stats': '''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    messages_sent INTEGER DEFAULT 0,
                    commands_used INTEGER DEFAULT 0,
                    last_message DATETIME,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            '''
        }
        
        # Create missing tables
        for table_name, schema in required_tables.items():
            if table_name not in existing_tables:
                print(f"  Creating table: {table_name}")
                cursor.execute(schema)
        
        conn.commit()
        conn.close()
        print("✅ Database schema updated!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating database schema: {e}")
        return False

def check_for_updates():
    """Check if there are updates available (if git is available)."""
    if not check_git():
        print("⚠️  Git not found. Cannot check for updates automatically.")
        return False
    
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️  Not in a git repository. Cannot check for updates.")
            return False
        
        # Fetch latest changes
        print("📡 Checking for updates...")
        subprocess.run(['git', 'fetch'], capture_output=True, check=True)
        
        # Check if there are updates
        result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], 
                              capture_output=True, text=True, check=True)
        commits_behind = int(result.stdout.strip())
        
        if commits_behind > 0:
            print(f"🔄 Found {commits_behind} new commit(s)!")
            return True
        else:
            print("✅ Bot is up to date!")
            return False
            
    except subprocess.CalledProcessError:
        print("⚠️  Could not check for updates.")
        return False
    except Exception as e:
        print(f"❌ Error checking for updates: {e}")
        return False

def pull_updates():
    """Pull the latest updates from git."""
    if not check_git():
        print("❌ Git not available. Cannot pull updates.")
        return False
    
    try:
        print("📥 Pulling latest updates...")
        subprocess.run(['git', 'pull'], check=True)
        print("✅ Updates pulled successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error pulling updates: {e}")
        return False

def create_update_log():
    """Create a log of the update."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] Bot updated\n"
    
    try:
        with open('logs/update.log', 'a') as f:
            f.write(log_entry)
    except Exception:
        pass  # Silently fail if we can't write the log

def main():
    """Main update function."""
    print_header()
    
    # Check if we're in the right directory
    if not os.path.exists('bot.py'):
        print("❌ Please run this script from the bot directory.")
        return
    
    # Get current version
    current_version = get_current_version()
    print(f"📋 Current version: {current_version}")
    print()
    
    # Check for updates
    has_updates = check_for_updates()
    
    if has_updates:
        response = input("Do you want to pull the latest updates? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            if not pull_updates():
                print("❌ Failed to pull updates. Continuing with dependency updates...")
        else:
            print("⏭️  Skipping code updates.")
    
    # Backup database
    backup_database()
    
    # Update dependencies
    if not update_dependencies():
        print("❌ Failed to update dependencies.")
        return
    
    # Update database schema
    if not update_database_schema():
        print("❌ Failed to update database schema.")
        return
    
    # Create update log
    create_update_log()
    
    print()
    print("🎉 Update completed successfully!")
    print()
    print("Next steps:")
    print("1. Restart your bot")
    print("2. Check the logs for any issues")
    print("3. Test the new features")
    print()
    print("💡 If you encounter any issues:")
    print("   - Check the logs in the logs/ directory")
    print("   - Run the installation script if needed")
    print("   - Restore from backup if necessary")

if __name__ == "__main__":
    main() 