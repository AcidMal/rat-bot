#!/usr/bin/env python3
"""
Database Setup Script for RatBot
This script helps you set up the PostgreSQL database for the bot.
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def setup_database():
    """Set up the database and create necessary tables"""
    print("🐀 RatBot Database Setup")
    print("========================")
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Error: DATABASE_URL not found in .env file")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database successfully")
        
        # Create tables
        print("📋 Creating tables...")
        
        # ModLogs table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS modlogs (
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                moderator_id BIGINT NOT NULL,
                action_type VARCHAR(50) NOT NULL,
                reason TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                additional_data JSONB
            )
        ''')
        print("✅ Created modlogs table")
        
        # Guild settings table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS guild_settings (
                guild_id BIGINT PRIMARY KEY,
                modlog_channel_id BIGINT,
                prefix VARCHAR(10) DEFAULT '!',
                welcome_channel_id BIGINT,
                auto_role_id BIGINT,
                settings JSONB DEFAULT '{}'::jsonb
            )
        ''')
        print("✅ Created guild_settings table")
        
        # Music queue table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS music_queues (
                guild_id BIGINT PRIMARY KEY,
                queue JSONB DEFAULT '[]'::jsonb,
                current_track JSONB,
                volume INTEGER DEFAULT 100,
                loop_mode VARCHAR(20) DEFAULT 'none'
            )
        ''')
        print("✅ Created music_queues table")
        
        # Create indexes for better performance
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_modlogs_guild_id ON modlogs(guild_id)
        ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_modlogs_user_id ON modlogs(user_id)
        ''')
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_modlogs_timestamp ON modlogs(timestamp)
        ''')
        print("✅ Created database indexes")
        
        await conn.close()
        print("✅ Database setup completed successfully!")
        return True
        
    except asyncpg.InvalidPasswordError:
        print("❌ Error: Invalid database password")
        print("Please check your DATABASE_URL in .env file")
        return False
    except asyncpg.InvalidCatalogNameError:
        print("❌ Error: Database does not exist")
        print("Please create the database first:")
        print("1. Connect to PostgreSQL: psql -U postgres")
        print("2. Create database: CREATE DATABASE ratbot;")
        print("3. Exit: \\q")
        return False
    except asyncpg.ConnectionDoesNotExistError:
        print("❌ Error: Cannot connect to database server")
        print("Please ensure PostgreSQL is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("This script will set up the database for RatBot.")
    print("Make sure PostgreSQL is running and your DATABASE_URL is correct in .env")
    print()
    
    response = input("Continue with database setup? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    success = asyncio.run(setup_database())
    
    if success:
        print()
        print("🎉 Database setup completed!")
        print("You can now start the bot with: ./start.sh")
    else:
        print()
        print("❌ Database setup failed.")
        print("Please check the error messages above and try again.")

if __name__ == "__main__":
    main() 