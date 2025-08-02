#!/usr/bin/env python3
"""
Rat Bot Update Script
Automatically updates the bot's code, dependencies, and database schema.
"""

import os
import sys
import subprocess
import sqlite3
import shutil
from datetime import datetime
import json

def check_git():
    """Check if git is available."""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_current_version():
    """Get current bot version."""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
            for line in content.split('\n'):
                if 'BOT_VERSION' in line and '=' in line:
                    version = line.split('=')[1].strip().strip('"\'')
                    return version
    except FileNotFoundError:
        pass
    return "1.0.0"

def update_dependencies():
    """Update Python dependencies."""
    print("📦 Updating Python dependencies...")
    
    try:
        # Update pip first
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      capture_output=True, check=True)
        
        # Install/update requirements
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      capture_output=True, check=True)
        
        print("✅ Dependencies updated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update dependencies: {e}")
        return False

def backup_database():
    """Create a backup of the database."""
    if not os.path.exists('data/bot.db'):
        print("📝 No database found to backup.")
        return True
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"data/bot_backup_{timestamp}.db"
    
    try:
        shutil.copy2('data/bot.db', backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup database: {e}")
        return False

def update_database_schema():
    """Update database schema if needed."""
    if not os.path.exists('data/bot.db'):
        print("📝 No database found. Creating new database...")
        try:
            os.makedirs('data', exist_ok=True)
            conn = sqlite3.connect('data/bot.db')
            cursor = conn.cursor()
            
            # Create all tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mod_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    command_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS server_settings (
                    guild_id INTEGER PRIMARY KEY,
                    mod_log_channel INTEGER,
                    welcome_channel INTEGER,
                    welcome_message TEXT,
                    prefix TEXT DEFAULT '!',
                    auto_role INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    messages_sent INTEGER DEFAULT 0,
                    commands_used INTEGER DEFAULT 0,
                    last_message DATETIME,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            print("✅ New database created successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False
    
    print("📝 Checking database schema...")
    try:
        conn = sqlite3.connect('data/bot.db')
        cursor = conn.cursor()
        
        # Check if all tables exist
        tables = ['mod_logs', 'user_warnings', 'custom_commands', 'server_settings', 'user_stats']
        existing_tables = []
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for row in cursor.fetchall():
            existing_tables.append(row[0])
        
        # Create missing tables
        if 'mod_logs' not in existing_tables:
            cursor.execute('''
                CREATE TABLE mod_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Added mod_logs table")
        
        if 'user_warnings' not in existing_tables:
            cursor.execute('''
                CREATE TABLE user_warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    reason TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Added user_warnings table")
        
        if 'custom_commands' not in existing_tables:
            cursor.execute('''
                CREATE TABLE custom_commands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    command_name TEXT NOT NULL,
                    response TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Added custom_commands table")
        
        if 'server_settings' not in existing_tables:
            cursor.execute('''
                CREATE TABLE server_settings (
                    guild_id INTEGER PRIMARY KEY,
                    mod_log_channel INTEGER,
                    welcome_channel INTEGER,
                    welcome_message TEXT,
                    prefix TEXT DEFAULT '!',
                    auto_role INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            print("✅ Added server_settings table")
        
        if 'user_stats' not in existing_tables:
            cursor.execute('''
                CREATE TABLE user_stats (
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    messages_sent INTEGER DEFAULT 0,
                    commands_used INTEGER DEFAULT 0,
                    last_message DATETIME,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, guild_id)
                )
            ''')
            print("✅ Added user_stats table")
        
        conn.commit()
        conn.close()
        print("✅ Database schema updated successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to update database schema: {e}")
        return False

def check_for_updates():
    """Check for git updates."""
    if not check_git():
        print("⚠️ Git not found. Skipping code updates.")
        return False
    
    try:
        # Check if we're in a git repository
        subprocess.run(['git', 'status'], capture_output=True, check=True)
        
        # Fetch latest changes
        subprocess.run(['git', 'fetch'], capture_output=True, check=True)
        
        # Check if there are updates
        result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip() != '0':
            return True
        else:
            print("📝 No code updates available.")
            return False
    except subprocess.CalledProcessError:
        print("⚠️ Not a git repository or no remote configured.")
        return False

def pull_updates():
    """Pull latest updates from git."""
    try:
        subprocess.run(['git', 'pull'], capture_output=True, check=True)
        print("✅ Code updated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to pull updates: {e}")
        return False

def create_update_log():
    """Create an update log entry."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    version = get_current_version()
    
    log_entry = {
        'timestamp': timestamp,
        'version': version,
        'update_type': 'automatic'
    }
    
    try:
        os.makedirs('logs', exist_ok=True)
        with open('logs/updates.log', 'a') as f:
            f.write(f"{json.dumps(log_entry)}\n")
    except Exception as e:
        print(f"⚠️ Failed to create update log: {e}")

def main():
    """Main update function."""
    print("🔄 Rat Bot Update Script")
    print("========================")
    print()
    
    # Check if we're in the right directory
    if not os.path.exists('bot.py'):
        print("❌ Please run this script from the bot directory.")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Virtual environment not detected. Please activate it first.")
        print("   Linux/macOS: source venv/bin/activate")
        print("   Windows: venv\\Scripts\\activate.bat")
        sys.exit(1)
    
    print(f"📅 Update started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Current version: {get_current_version()}")
    print()
    
    # Backup database
    if not backup_database():
        print("❌ Database backup failed. Aborting update.")
        sys.exit(1)
    
    # Check for code updates
    has_updates = check_for_updates()
    
    # Update dependencies
    if not update_dependencies():
        print("❌ Dependency update failed. Aborting update.")
        sys.exit(1)
    
    # Pull code updates if available
    if has_updates:
        if not pull_updates():
            print("❌ Code update failed. Aborting update.")
            sys.exit(1)
    
    # Update database schema
    if not update_database_schema():
        print("❌ Database schema update failed. Aborting update.")
        sys.exit(1)
    
    # Create update log
    create_update_log()
    
    print()
    print("✅ Update completed successfully!")
    print()
    print("📝 What was updated:")
    print("   • Python dependencies")
    if has_updates:
        print("   • Bot code (from git)")
    print("   • Database schema (if needed)")
    print()
    print("🚀 You can now restart your bot!")
    print("   Linux/macOS: ./run.sh")
    print("   Windows: run.bat")

if __name__ == "__main__":
    main() 