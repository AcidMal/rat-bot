import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class Database:
    """Database manager for the bot."""
    
    def __init__(self, db_path: str = "data/bot.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create mod_logs table
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
        
        # Create user_warnings table
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
        
        # Create custom_commands table
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
        
        # Create server_settings table
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
        
        # Create user_stats table
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
        logger.info("Database initialized successfully")
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    # Moderation Log Methods
    def log_mod_action(self, guild_id: int, user_id: int, moderator_id: int, 
                      action_type: str, reason: Optional[str] = None) -> bool:
        """Log a moderation action."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO mod_logs (guild_id, user_id, moderator_id, action_type, reason)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, user_id, moderator_id, action_type, reason))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging mod action: {e}")
            return False
    
    def get_mod_logs(self, guild_id: int, user_id: Optional[int] = None, 
                    limit: int = 10) -> List[Dict[str, Any]]:
        """Get moderation logs for a guild or specific user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT * FROM mod_logs 
                    WHERE guild_id = ? AND user_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (guild_id, user_id, limit))
            else:
                cursor.execute('''
                    SELECT * FROM mod_logs 
                    WHERE guild_id = ?
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (guild_id, limit))
            
            columns = [description[0] for description in cursor.description]
            logs = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return logs
        except Exception as e:
            logger.error(f"Error getting mod logs: {e}")
            return []
    
    # Warning Methods
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> bool:
        """Add a warning for a user."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_warnings (guild_id, user_id, moderator_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, user_id, moderator_id, reason))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding warning: {e}")
            return False
    
    def get_user_warnings(self, guild_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all warnings for a user in a guild."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_warnings 
                WHERE guild_id = ? AND user_id = ?
                ORDER BY timestamp DESC
            ''', (guild_id, user_id))
            
            columns = [description[0] for description in cursor.description]
            warnings = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return warnings
        except Exception as e:
            logger.error(f"Error getting user warnings: {e}")
            return []
    
    def clear_user_warnings(self, guild_id: int, user_id: int) -> bool:
        """Clear all warnings for a user in a guild."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM user_warnings 
                WHERE guild_id = ? AND user_id = ?
            ''', (guild_id, user_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error clearing user warnings: {e}")
            return False
    
    # Server Settings Methods
    def get_server_setting(self, guild_id: int, setting: str) -> Optional[Any]:
        """Get a server setting."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(f'SELECT {setting} FROM server_settings WHERE guild_id = ?', (guild_id,))
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting server setting: {e}")
            return None
    
    def set_server_setting(self, guild_id: int, setting: str, value: Any) -> bool:
        """Set a server setting."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if guild exists in settings
            cursor.execute('SELECT guild_id FROM server_settings WHERE guild_id = ?', (guild_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute(f'UPDATE server_settings SET {setting} = ? WHERE guild_id = ?', (value, guild_id))
            else:
                cursor.execute(f'INSERT INTO server_settings (guild_id, {setting}) VALUES (?, ?)', (guild_id, value))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting server setting: {e}")
            return False
    
    # Custom Commands Methods
    def add_custom_command(self, guild_id: int, command_name: str, response: str, created_by: int) -> bool:
        """Add a custom command."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO custom_commands (guild_id, command_name, response, created_by)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, command_name, response, created_by))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding custom command: {e}")
            return False
    
    def get_custom_command(self, guild_id: int, command_name: str) -> Optional[Dict[str, Any]]:
        """Get a custom command."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM custom_commands 
                WHERE guild_id = ? AND command_name = ?
            ''', (guild_id, command_name))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = ['id', 'guild_id', 'command_name', 'response', 'created_by', 'created_at']
                return dict(zip(columns, result))
            return None
        except Exception as e:
            logger.error(f"Error getting custom command: {e}")
            return None
    
    def get_guild_custom_commands(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all custom commands for a guild."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM custom_commands 
                WHERE guild_id = ?
                ORDER BY command_name
            ''', (guild_id,))
            
            columns = ['id', 'guild_id', 'command_name', 'response', 'created_by', 'created_at']
            commands = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            conn.close()
            return commands
        except Exception as e:
            logger.error(f"Error getting guild custom commands: {e}")
            return []
    
    def delete_custom_command(self, guild_id: int, command_name: str) -> bool:
        """Delete a custom command."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM custom_commands 
                WHERE guild_id = ? AND command_name = ?
            ''', (guild_id, command_name))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error deleting custom command: {e}")
            return False
    
    # User Stats Methods
    def increment_user_stats(self, user_id: int, guild_id: int, stat_type: str = "messages") -> bool:
        """Increment user statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if stat_type == "messages":
                cursor.execute('''
                    INSERT OR REPLACE INTO user_stats (user_id, guild_id, messages_sent, last_message)
                    VALUES (?, ?, COALESCE((SELECT messages_sent FROM user_stats WHERE user_id = ? AND guild_id = ?), 0) + 1, ?)
                ''', (user_id, guild_id, user_id, guild_id, datetime.now()))
            elif stat_type == "commands":
                cursor.execute('''
                    INSERT OR REPLACE INTO user_stats (user_id, guild_id, commands_used)
                    VALUES (?, ?, COALESCE((SELECT commands_used FROM user_stats WHERE user_id = ? AND guild_id = ?), 0) + 1)
                ''', (user_id, guild_id, user_id, guild_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error incrementing user stats: {e}")
            return False
    
    def get_user_stats(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get user statistics."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM user_stats 
                WHERE user_id = ? AND guild_id = ?
            ''', (user_id, guild_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = ['user_id', 'guild_id', 'messages_sent', 'commands_used', 'last_message', 'joined_at']
                return dict(zip(columns, result))
            return None
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return None

# Global database instance
db = Database() 