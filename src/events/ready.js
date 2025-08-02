const { Events, ActivityType } = require('discord.js');

module.exports = {
  name: Events.ClientReady,
  once: true,
  execute(client) {
    const shardInfo = client.shardId !== undefined ? ` | Shard ${client.shardId}` : '';
    const clusterInfo = client.clusterId !== undefined ? ` | Cluster ${client.clusterId}` : '';
    
    console.log(`[BOT] Ready! Logged in as ${client.user.tag}${shardInfo}${clusterInfo}`);
    
    // Set bot activity with shard/cluster info
    const activityText = `commands${shardInfo}${clusterInfo}`;
    client.user.setActivity(activityText, { type: ActivityType.Watching });
    
    // Log guild count for this shard
    console.log(`[BOT] Serving ${client.guilds.cache.size} guilds${shardInfo}${clusterInfo}`);
  },
}; 