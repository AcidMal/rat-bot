import asyncpg
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool"""
        self.pool = await asyncpg.create_pool(self.connection_string)
        await self.create_tables()
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
    
    async def create_tables(self):
        """Create necessary database tables"""
        async with self.pool.acquire() as conn:
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
    
    # ModLog methods
    async def add_modlog(self, guild_id: int, user_id: int, moderator_id: int, 
                        action_type: str, reason: str = None, additional_data: Dict = None):
        """Add a new modlog entry"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO modlogs (guild_id, user_id, moderator_id, action_type, reason, additional_data)
                VALUES ($1, $2, $3, $4, $5, $6)
            ''', guild_id, user_id, moderator_id, action_type, reason, additional_data)
    
    async def get_modlogs(self, guild_id: int, user_id: int = None, limit: int = 50) -> List[Dict]:
        """Get modlogs for a guild or specific user"""
        async with self.pool.acquire() as conn:
            if user_id:
                rows = await conn.fetch('''
                    SELECT * FROM modlogs 
                    WHERE guild_id = $1 AND user_id = $2 
                    ORDER BY timestamp DESC 
                    LIMIT $3
                ''', guild_id, user_id, limit)
            else:
                rows = await conn.fetch('''
                    SELECT * FROM modlogs 
                    WHERE guild_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2
                ''', guild_id, limit)
            
            return [dict(row) for row in rows]
    
    # Guild settings methods
    async def get_guild_settings(self, guild_id: int) -> Dict:
        """Get guild settings"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM guild_settings WHERE guild_id = $1
            ''', guild_id)
            
            if row:
                return dict(row)
            return None
    
    async def update_guild_settings(self, guild_id: int, **kwargs):
        """Update guild settings"""
        async with self.pool.acquire() as conn:
            # Check if guild settings exist
            exists = await conn.fetchval('''
                SELECT 1 FROM guild_settings WHERE guild_id = $1
            ''', guild_id)
            
            if exists:
                # Update existing settings
                set_clause = ', '.join([f"{k} = ${i+2}" for i, k in enumerate(kwargs.keys())])
                await conn.execute(f'''
                    UPDATE guild_settings SET {set_clause} WHERE guild_id = $1
                ''', guild_id, *kwargs.values())
            else:
                # Insert new settings
                columns = ['guild_id'] + list(kwargs.keys())
                values = [guild_id] + list(kwargs.values())
                placeholders = ', '.join([f'${i+1}' for i in range(len(values))])
                await conn.execute(f'''
                    INSERT INTO guild_settings ({', '.join(columns)}) VALUES ({placeholders})
                ''', *values)
    
    # Music queue methods
    async def get_music_queue(self, guild_id: int) -> Dict:
        """Get music queue for a guild"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow('''
                SELECT * FROM music_queues WHERE guild_id = $1
            ''', guild_id)
            
            if row:
                return dict(row)
            return None
    
    async def update_music_queue(self, guild_id: int, queue: List = None, 
                               current_track: Dict = None, volume: int = None, 
                               loop_mode: str = None):
        """Update music queue for a guild"""
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval('''
                SELECT 1 FROM music_queues WHERE guild_id = $1
            ''', guild_id)
            
            if exists:
                updates = []
                values = [guild_id]
                param_count = 1
                
                if queue is not None:
                    updates.append(f"queue = ${param_count + 1}")
                    values.append(queue)
                    param_count += 1
                
                if current_track is not None:
                    updates.append(f"current_track = ${param_count + 1}")
                    values.append(current_track)
                    param_count += 1
                
                if volume is not None:
                    updates.append(f"volume = ${param_count + 1}")
                    values.append(volume)
                    param_count += 1
                
                if loop_mode is not None:
                    updates.append(f"loop_mode = ${param_count + 1}")
                    values.append(loop_mode)
                    param_count += 1
                
                if updates:
                    set_clause = ', '.join(updates)
                    await conn.execute(f'''
                        UPDATE music_queues SET {set_clause} WHERE guild_id = $1
                    ''', *values)
            else:
                await conn.execute('''
                    INSERT INTO music_queues (guild_id, queue, current_track, volume, loop_mode)
                    VALUES ($1, $2, $3, $4, $5)
                ''', guild_id, queue or [], current_track, volume or 100, loop_mode or 'none') 