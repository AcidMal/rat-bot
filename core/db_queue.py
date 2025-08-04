"""
Database-backed music queue implementation
Replaces wavelink's built-in queue with persistent database storage
"""

import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger
import wavelink
from datetime import datetime, timezone

class DatabaseQueue:
    """Database-backed queue for music tracks"""
    
    def __init__(self, guild_id: int, db):
        self.guild_id = guild_id
        self.db = db
        self._cache = []  # Local cache for performance
        self._cache_valid = False
        self._lock = asyncio.Lock()
    
    async def put_wait(self, track: wavelink.Playable) -> None:
        """Add a track to the queue"""
        async with self._lock:
            # Convert track to database format
            track_data = {
                'title': track.title,
                'uri': track.uri,
                'length': track.length,
                'source': track.source,
                'requester_id': getattr(track.requester, 'id', None) if hasattr(track, 'requester') else None,
                'requester_name': getattr(track.requester, 'display_name', 'Unknown') if hasattr(track, 'requester') else 'Unknown',
                'requested_at': getattr(track, 'requested_at', datetime.now(timezone.utc)).isoformat() if hasattr(track, 'requested_at') else datetime.now(timezone.utc).isoformat(),
                'track_id': getattr(track, 'identifier', track.uri),
                'thumbnail': getattr(track, 'thumbnail', None) if hasattr(track, 'thumbnail') else None
            }
            
            # Add to database
            position = await self.db.add_to_queue(self.guild_id, track_data)
            logger.info(f"Added track to DB queue: {track.title} at position {position}")
            
            # Invalidate cache
            self._cache_valid = False
    
    async def get_wait(self) -> Optional[wavelink.Playable]:
        """Get the next track from the queue"""
        async with self._lock:
            # Get next track from database
            track_data = await self.db.get_next_in_queue(self.guild_id)
            
            if not track_data:
                return None
            
            logger.info(f"Retrieved track from DB queue: {track_data['title']}")
            
            # Convert back to wavelink.Playable
            try:
                # Search for the track to get a fresh Playable object
                tracks = await wavelink.Playable.search(track_data['uri'])
                if tracks:
                    track = tracks[0]
                    
                    # Restore metadata
                    if track_data.get('requester_id'):
                        # We can't restore the full User object, but we can store the ID
                        track._db_requester_id = track_data['requester_id']
                        track._db_requester_name = track_data['requester_name']
                    
                    if track_data.get('requested_at'):
                        track._db_requested_at = track_data['requested_at']
                    
                    # Invalidate cache
                    self._cache_valid = False
                    
                    return track
                else:
                    logger.warning(f"Could not find track for URI: {track_data['uri']}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error converting track data to Playable: {e}")
                return None
    
    async def get_count(self) -> int:
        """Get the current queue size (async method)"""
        return await self.db.get_queue_size(self.guild_id)
    
    @property
    def count(self) -> int:
        """Synchronous count property (for compatibility)"""
        # This is a hack for compatibility with existing code
        # We'll need to use async get_count() in practice
        try:
            # Return cached size if available
            if hasattr(self, '_cached_size'):
                return self._cached_size
            return 0  # Default to 0, actual count should use get_count()
        except Exception:
            return 0
    
    async def get_is_empty(self) -> bool:
        """Check if the queue is empty (async method)"""
        size = await self.db.get_queue_size(self.guild_id)
        return size == 0
    
    @property
    def is_empty(self) -> bool:
        """Synchronous is_empty property (for compatibility)"""
        try:
            # Return cached status if available
            if hasattr(self, '_cached_empty'):
                return self._cached_empty
            return True  # Default to empty, actual status should use get_is_empty()
        except Exception:
            return True
    
    async def clear(self) -> int:
        """Clear the entire queue"""
        async with self._lock:
            cleared = await self.db.clear_queue(self.guild_id)
            self._cache_valid = False
            logger.info(f"Cleared {cleared} tracks from DB queue")
            return cleared
    
    async def remove(self, position: int) -> bool:
        """Remove a track at specific position"""
        async with self._lock:
            success = await self.db.remove_from_queue(self.guild_id, position)
            if success:
                self._cache_valid = False
                logger.info(f"Removed track at position {position} from DB queue")
            return success
    
    async def get_preview(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get a preview of the queue without removing tracks"""
        return await self.db.get_queue_preview(self.guild_id, limit)
    
    def __iter__(self):
        """Iterator support (returns cached data)"""
        # This is for compatibility with existing code that iterates over the queue
        # We'll need to populate cache first
        return iter(self._cache)
    
    def __len__(self):
        """Length support (returns cached length)"""
        return len(self._cache)
    
    async def populate_cache(self):
        """Populate local cache for sync operations"""
        try:
            preview = await self.get_preview(50)  # Cache up to 50 tracks
            self._cache = preview
            self._cache_valid = True
        except Exception as e:
            logger.error(f"Failed to populate queue cache: {e}")
            self._cache = []
            self._cache_valid = False