import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from loguru import logger

class ShardManager:
    """Manages bot sharding and shard communication"""
    
    def __init__(self, bot):
        self.bot = bot
        self.shard_stats = {}
        self.shard_events = {}
    
    async def initialize(self):
        """Initialize shard manager"""
        if not hasattr(self.bot, 'shards'):
            logger.warning("Bot is not sharded, shard manager disabled")
            return
        
        # Initialize shard stats
        for shard_id in self.bot.shards.keys():
            self.shard_stats[shard_id] = {
                'guilds': 0,
                'users': 0,
                'latency': 0,
                'status': 'unknown',
                'last_update': datetime.now(timezone.utc)
            }
        
        # Start monitoring task
        asyncio.create_task(self._monitor_shards())
        
        logger.info(f"⚡ Shard manager initialized for {len(self.bot.shards)} shards")
    
    async def _monitor_shards(self):
        """Monitor shard health and statistics"""
        while True:
            try:
                await self._update_shard_stats()
                await asyncio.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.error(f"Shard monitoring error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _update_shard_stats(self):
        """Update statistics for all shards"""
        for shard_id, shard in self.bot.shards.items():
            try:
                # Get guilds for this shard
                shard_guilds = [g for g in self.bot.guilds if g.shard_id == shard_id]
                
                # Calculate stats
                guild_count = len(shard_guilds)
                user_count = sum(guild.member_count for guild in shard_guilds if guild.member_count)
                latency = shard.latency * 1000  # Convert to ms
                
                # Determine status
                if shard.is_closed():
                    status = 'offline'
                elif latency > 500:
                    status = 'degraded'
                else:
                    status = 'online'
                
                # Update stats
                self.shard_stats[shard_id] = {
                    'guilds': guild_count,
                    'users': user_count,
                    'latency': round(latency, 2),
                    'status': status,
                    'last_update': datetime.now(timezone.utc)
                }
                
            except Exception as e:
                logger.error(f"Failed to update stats for shard {shard_id}: {e}")
                self.shard_stats[shard_id]['status'] = 'error'
    
    def get_shard_stats(self, shard_id: Optional[int] = None) -> Dict:
        """Get statistics for a specific shard or all shards"""
        if shard_id is not None:
            return self.shard_stats.get(shard_id, {})
        return self.shard_stats.copy()
    
    def get_total_stats(self) -> Dict:
        """Get combined statistics for all shards"""
        total_guilds = sum(stats['guilds'] for stats in self.shard_stats.values())
        total_users = sum(stats['users'] for stats in self.shard_stats.values())
        avg_latency = sum(stats['latency'] for stats in self.shard_stats.values()) / len(self.shard_stats) if self.shard_stats else 0
        
        # Count shard statuses
        status_counts = {}
        for stats in self.shard_stats.values():
            status = stats['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_shards': len(self.shard_stats),
            'total_guilds': total_guilds,
            'total_users': total_users,
            'average_latency': round(avg_latency, 2),
            'status_counts': status_counts
        }
    
    async def restart_shard(self, shard_id: int) -> bool:
        """Restart a specific shard"""
        try:
            if shard_id not in self.bot.shards:
                return False
            
            logger.info(f"🔄 Restarting shard {shard_id}")
            
            # Close the shard
            await self.bot.shards[shard_id].close()
            
            # Wait a moment
            await asyncio.sleep(2)
            
            # Reconnect the shard
            await self.bot.shards[shard_id].connect()
            
            logger.info(f"✅ Shard {shard_id} restarted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart shard {shard_id}: {e}")
            return False
    
    async def broadcast_to_shards(self, event_type: str, data: Dict):
        """Broadcast an event to all shards"""
        for shard_id in self.bot.shards.keys():
            await self.send_to_shard(shard_id, event_type, data)
    
    async def send_to_shard(self, shard_id: int, event_type: str, data: Dict):
        """Send an event to a specific shard"""
        if shard_id not in self.shard_events:
            self.shard_events[shard_id] = []
        
        event = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.now(timezone.utc)
        }
        
        self.shard_events[shard_id].append(event)
        
        # Keep only last 100 events per shard
        if len(self.shard_events[shard_id]) > 100:
            self.shard_events[shard_id] = self.shard_events[shard_id][-100:]
    
    def get_shard_events(self, shard_id: int, limit: int = 50) -> List[Dict]:
        """Get recent events for a shard"""
        if shard_id not in self.shard_events:
            return []
        
        return self.shard_events[shard_id][-limit:]
    
    def get_healthy_shards(self) -> List[int]:
        """Get list of healthy shard IDs"""
        healthy = []
        for shard_id, stats in self.shard_stats.items():
            if stats['status'] in ['online', 'degraded']:
                healthy.append(shard_id)
        return healthy
    
    def get_unhealthy_shards(self) -> List[int]:
        """Get list of unhealthy shard IDs"""
        unhealthy = []
        for shard_id, stats in self.shard_stats.items():
            if stats['status'] in ['offline', 'error']:
                unhealthy.append(shard_id)
        return unhealthy
    
    async def health_check(self) -> Dict:
        """Perform comprehensive health check"""
        total_stats = self.get_total_stats()
        healthy_shards = self.get_healthy_shards()
        unhealthy_shards = self.get_unhealthy_shards()
        
        # Calculate health score (0-100)
        total_shards = len(self.shard_stats)
        healthy_count = len(healthy_shards)
        health_score = (healthy_count / total_shards * 100) if total_shards > 0 else 0
        
        # Determine overall status
        if health_score >= 90:
            overall_status = 'healthy'
        elif health_score >= 70:
            overall_status = 'degraded'
        else:
            overall_status = 'unhealthy'
        
        return {
            'overall_status': overall_status,
            'health_score': round(health_score, 1),
            'total_shards': total_shards,
            'healthy_shards': healthy_count,
            'unhealthy_shards': len(unhealthy_shards),
            'unhealthy_shard_ids': unhealthy_shards,
            'stats': total_stats,
            'timestamp': datetime.now(timezone.utc)
        }