const { ClusterManager } = require('discord-hybrid-sharding');
const path = require('path');
require('dotenv').config();

// Create a new cluster manager
const manager = new ClusterManager(path.join(__dirname, 'index.js'), {
  token: process.env.DISCORD_TOKEN,
  totalShards: process.env.TOTAL_SHARDS ? parseInt(process.env.TOTAL_SHARDS) : 'auto',
  totalClusters: process.env.TOTAL_CLUSTERS ? parseInt(process.env.TOTAL_CLUSTERS) : 'auto',
  respawn: true,
  spawnTimeout: 30000,
  killTimeout: 5000,
  restarts: {
    max: 5,
    interval: 60000,
  },
});

// Handle cluster events
manager.on('clusterCreate', cluster => {
  console.log(`[CLUSTER] Launched cluster ${cluster.id}`);
});

manager.on('clusterReady', cluster => {
  console.log(`[CLUSTER] Cluster ${cluster.id} is ready`);
});

manager.on('clusterReconnecting', cluster => {
  console.log(`[CLUSTER] Cluster ${cluster.id} is reconnecting`);
});

manager.on('clusterDisconnect', (event, cluster) => {
  console.log(`[CLUSTER] Cluster ${cluster.id} disconnected: ${event.code} ${event.reason}`);
});

manager.on('clusterError', (error, cluster) => {
  console.error(`[CLUSTER] Cluster ${cluster.id} encountered an error:`, error);
});

manager.on('clusterResume', (cluster, replayed) => {
  console.log(`[CLUSTER] Cluster ${cluster.id} resumed, replayed ${replayed} events`);
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('[CLUSTER MANAGER] Received SIGINT, shutting down gracefully...');
  manager.destroy();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('[CLUSTER MANAGER] Received SIGTERM, shutting down gracefully...');
  manager.destroy();
  process.exit(0);
});

// Spawn the clusters
manager.spawn().catch(console.error);

module.exports = manager; 