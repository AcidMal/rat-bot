const { ShardingManager } = require('discord.js');
const path = require('path');
require('dotenv').config();

// Create a new sharding manager
const manager = new ShardingManager(path.join(__dirname, 'index.js'), {
  token: process.env.DISCORD_TOKEN,
  totalShards: process.env.TOTAL_SHARDS ? parseInt(process.env.TOTAL_SHARDS) : 'auto',
  respawn: true,
  spawnTimeout: 30000,
  killTimeout: 5000,
});

// Handle shard events
manager.on('shardCreate', shard => {
  console.log(`[SHARD] Launched shard ${shard.id}`);
});

manager.on('shardReady', shard => {
  console.log(`[SHARD] Shard ${shard.id} is ready`);
});

manager.on('shardReconnecting', shard => {
  console.log(`[SHARD] Shard ${shard.id} is reconnecting`);
});

manager.on('shardDisconnect', (event, shard) => {
  console.log(`[SHARD] Shard ${shard.id} disconnected: ${event.code} ${event.reason}`);
});

manager.on('shardError', (error, shard) => {
  console.error(`[SHARD] Shard ${shard.id} encountered an error:`, error);
});

manager.on('shardResume', (shard, replayed) => {
  console.log(`[SHARD] Shard ${shard.id} resumed, replayed ${replayed} events`);
});

// Spawn the shards
manager.spawn().catch(console.error);

// Handle process termination
process.on('SIGINT', () => {
  console.log('[SHARD MANAGER] Received SIGINT, shutting down gracefully...');
  manager.destroy();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('[SHARD MANAGER] Received SIGTERM, shutting down gracefully...');
  manager.destroy();
  process.exit(0);
});

module.exports = manager; 