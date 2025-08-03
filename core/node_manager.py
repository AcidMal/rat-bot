import asyncio
import json
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone
import redis.asyncio as aioredis
from loguru import logger
from config import config

class NodeManager:
    """Manages node communication and clustering"""
    
    def __init__(self, bot, redis: aioredis.Redis):
        self.bot = bot
        self.redis = redis
        self.node_id = config.node.node_id
        self.cluster_name = config.node.cluster_name
        self.is_primary = config.node.is_primary
        
        # Node state
        self.is_registered = False
        self.last_heartbeat = time.time()
        self.connected_nodes = {}
        
        # Event handlers
        self.event_handlers = {}
    
    async def initialize(self):
        """Initialize node manager"""
        try:
            # Subscribe to cluster events
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(f"{self.cluster_name}:events")
            
            # Start event listener
            asyncio.create_task(self._event_listener())
            
            logger.info(f"🌐 Node manager initialized: {self.node_id}")
        except Exception as e:
            logger.error(f"Failed to initialize node manager: {e}")
    
    async def register_node(self):
        """Register this node with the cluster"""
        try:
            node_info = {
                "node_id": self.node_id,
                "cluster_name": self.cluster_name,
                "is_primary": self.is_primary,
                "shard_count": getattr(self.bot, 'shard_count', 1),
                "shard_ids": getattr(self.bot, 'shard_ids', [0]),
                "guilds": len(self.bot.guilds),
                "users": sum(guild.member_count for guild in self.bot.guilds if guild.member_count),
                "status": "online",
                "last_heartbeat": time.time(),
                "registered_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Store node info in Redis
            await self.redis.hset(
                f"{self.cluster_name}:nodes",
                self.node_id,
                json.dumps(node_info)
            )
            
            # Set TTL for node info (expires if heartbeat stops)
            await self.redis.expire(f"{self.cluster_name}:nodes:{self.node_id}", 120)
            
            # Announce node registration
            await self._publish_event("node_registered", node_info)
            
            self.is_registered = True
            logger.info(f"✅ Node registered: {self.node_id}")
            
        except Exception as e:
            logger.error(f"Failed to register node: {e}")
    
    async def send_heartbeat(self):
        """Send heartbeat to maintain node presence"""
        if not self.is_registered:
            return
        
        try:
            heartbeat_data = {
                "node_id": self.node_id,
                "timestamp": time.time(),
                "guilds": len(self.bot.guilds),
                "users": sum(guild.member_count for guild in self.bot.guilds if guild.member_count),
                "status": "online",
                "uptime": (datetime.now(timezone.utc) - self.bot.start_time).total_seconds()
            }
            
            # Update node info
            await self.redis.hset(
                f"{self.cluster_name}:nodes",
                self.node_id,
                json.dumps(heartbeat_data)
            )
            
            # Reset TTL
            await self.redis.expire(f"{self.cluster_name}:nodes:{self.node_id}", 120)
            
            self.last_heartbeat = time.time()
            
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
    
    async def get_cluster_nodes(self) -> Dict[str, dict]:
        """Get all nodes in the cluster"""
        try:
            nodes_data = await self.redis.hgetall(f"{self.cluster_name}:nodes")
            nodes = {}
            
            for node_id, node_data in nodes_data.items():
                try:
                    nodes[node_id] = json.loads(node_data)
                except json.JSONDecodeError:
                    continue
            
            return nodes
        except Exception as e:
            logger.error(f"Failed to get cluster nodes: {e}")
            return {}
    
    async def get_primary_node(self) -> Optional[str]:
        """Get the primary node ID"""
        nodes = await self.get_cluster_nodes()
        
        for node_id, node_data in nodes.items():
            if node_data.get("is_primary", False):
                return node_id
        
        return None
    
    async def promote_to_primary(self):
        """Promote this node to primary"""
        try:
            # Update node info
            node_data = await self.redis.hget(f"{self.cluster_name}:nodes", self.node_id)
            if node_data:
                node_info = json.loads(node_data)
                node_info["is_primary"] = True
                
                await self.redis.hset(
                    f"{self.cluster_name}:nodes",
                    self.node_id,
                    json.dumps(node_info)
                )
                
                self.is_primary = True
                
                # Announce promotion
                await self._publish_event("primary_promoted", {"node_id": self.node_id})
                
                logger.info(f"🏆 Node promoted to primary: {self.node_id}")
        except Exception as e:
            logger.error(f"Failed to promote to primary: {e}")
    
    async def broadcast_command(self, command: str, data: dict):
        """Broadcast a command to all nodes"""
        try:
            event_data = {
                "type": "command",
                "command": command,
                "data": data,
                "sender": self.node_id,
                "timestamp": time.time()
            }
            
            await self._publish_event("command", event_data)
            logger.debug(f"📡 Broadcasted command: {command}")
        except Exception as e:
            logger.error(f"Failed to broadcast command: {e}")
    
    async def send_to_node(self, target_node: str, command: str, data: dict):
        """Send a command to a specific node"""
        try:
            event_data = {
                "type": "direct_command",
                "target": target_node,
                "command": command,
                "data": data,
                "sender": self.node_id,
                "timestamp": time.time()
            }
            
            await self._publish_event("direct_command", event_data)
            logger.debug(f"📤 Sent command to {target_node}: {command}")
        except Exception as e:
            logger.error(f"Failed to send command to node: {e}")
    
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _publish_event(self, event_type: str, data: dict):
        """Publish an event to the cluster"""
        event = {
            "type": event_type,
            "data": data,
            "sender": self.node_id,
            "timestamp": time.time()
        }
        
        await self.redis.publish(
            f"{self.cluster_name}:events",
            json.dumps(event)
        )
    
    async def _event_listener(self):
        """Listen for cluster events"""
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        event = json.loads(message["data"])
                        await self._handle_event(event)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Event listener error: {e}")
    
    async def _handle_event(self, event: dict):
        """Handle incoming cluster events"""
        event_type = event.get("type")
        sender = event.get("sender")
        
        # Ignore events from self
        if sender == self.node_id:
            return
        
        try:
            if event_type == "node_registered":
                await self._handle_node_registered(event["data"])
            elif event_type == "command":
                await self._handle_command(event["data"])
            elif event_type == "direct_command":
                await self._handle_direct_command(event["data"])
            elif event_type == "primary_promoted":
                await self._handle_primary_promoted(event["data"])
            
            # Call registered handlers
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {e}")
        except Exception as e:
            logger.error(f"Failed to handle event {event_type}: {e}")
    
    async def _handle_node_registered(self, data: dict):
        """Handle node registration event"""
        node_id = data.get("node_id")
        logger.info(f"🔗 Node joined cluster: {node_id}")
        
        # Update connected nodes
        self.connected_nodes[node_id] = data
    
    async def _handle_command(self, data: dict):
        """Handle broadcast command"""
        command = data.get("command")
        command_data = data.get("data", {})
        
        logger.debug(f"📥 Received broadcast command: {command}")
        
        # Handle built-in commands
        if command == "reload_config":
            # Reload configuration
            pass
        elif command == "sync_guilds":
            # Sync guild data
            pass
    
    async def _handle_direct_command(self, data: dict):
        """Handle direct command"""
        target = data.get("target")
        
        # Only process if targeted at this node
        if target != self.node_id:
            return
        
        command = data.get("command")
        command_data = data.get("data", {})
        
        logger.debug(f"📨 Received direct command: {command}")
        
        # Handle direct commands
        if command == "get_stats":
            # Send stats back to sender
            stats = {
                "guilds": len(self.bot.guilds),
                "users": sum(guild.member_count for guild in self.bot.guilds if guild.member_count),
                "uptime": (datetime.now(timezone.utc) - self.bot.start_time).total_seconds()
            }
            await self.send_to_node(data.get("sender"), "stats_response", stats)
    
    async def _handle_primary_promoted(self, data: dict):
        """Handle primary node promotion"""
        new_primary = data.get("node_id")
        
        if new_primary == self.node_id:
            return
        
        # Update primary status
        if self.is_primary:
            self.is_primary = False
            logger.info(f"🔄 Primary status transferred to: {new_primary}")
    
    async def cleanup(self):
        """Cleanup node manager"""
        try:
            # Unregister node
            await self.redis.hdel(f"{self.cluster_name}:nodes", self.node_id)
            
            # Announce departure
            await self._publish_event("node_leaving", {"node_id": self.node_id})
            
            # Close pubsub
            if hasattr(self, 'pubsub'):
                await self.pubsub.unsubscribe()
                await self.pubsub.close()
            
            logger.info(f"🔌 Node manager cleanup complete: {self.node_id}")
        except Exception as e:
            logger.error(f"Node manager cleanup error: {e}")