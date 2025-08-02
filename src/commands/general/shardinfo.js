const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('shardinfo')
    .setDescription('Display shard and cluster information'),
  async execute(interaction) {
    try {
      const client = interaction.client;
      const shardId = client.shardId || 0;
      const clusterId = client.clusterId || 0;
      
      // Get shard information
      let shardInfo = 'N/A';
      let clusterInfo = 'N/A';
      let totalGuilds = client.guilds.cache.size;
      let totalUsers = client.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0);
      
      if (client.shard) {
        const shard = client.shard;
        shardInfo = `Shard ${shard.id}`;
        
        // Get total guilds and users across all shards
        try {
          const evalResult = await client.shard.broadcastEval(c => ({
            guilds: c.guilds.cache.size,
            users: c.guilds.cache.reduce((acc, guild) => acc + guild.memberCount, 0)
          }));
          
          totalGuilds = evalResult.reduce((acc, result) => acc + result.guilds, 0);
          totalUsers = evalResult.reduce((acc, result) => acc + result.users, 0);
        } catch (error) {
          console.error('Error getting shard info:', error);
        }
      }
      
      if (client.cluster) {
        clusterInfo = `Cluster ${client.cluster.id}`;
      }
      
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🔧 Shard & Cluster Information')
        .addFields(
          { name: 'Current Shard', value: shardInfo, inline: true },
          { name: 'Current Cluster', value: clusterInfo, inline: true },
          { name: 'Guilds (This Shard)', value: client.guilds.cache.size.toString(), inline: true },
          { name: 'Total Guilds', value: totalGuilds.toString(), inline: true },
          { name: 'Total Users', value: totalUsers.toLocaleString(), inline: true },
          { name: 'Ping', value: `${client.ws.ping}ms`, inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Shardinfo command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 