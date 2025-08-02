const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('queue')
    .setDescription('Show the current music queue'),
  async execute(interaction) {
    try {
      const guildId = interaction.guild.id;
      const queue = musicManager.getQueueInfo(guildId);
      
      if (queue.length === 0) {
        return await interaction.reply({ 
          content: '📭 The queue is empty!', 
          ephemeral: true 
        });
      }

      const embed = new EmbedBuilder()
        .setColor('#0099ff')
        .setTitle('🎵 Music Queue')
        .setDescription(`**${queue.length}** songs in queue`)
        .setTimestamp();

      // Show first 10 songs in queue
      const songsToShow = queue.slice(0, 10);
      let queueText = '';
      
      songsToShow.forEach((song, index) => {
        const duration = musicManager.formatDuration(song.duration);
        queueText += `**${index + 1}.** ${song.title} (${duration})\n`;
      });

      if (queue.length > 10) {
        queueText += `\n... and ${queue.length - 10} more songs`;
      }

      embed.addFields({
        name: 'Upcoming Songs',
        value: queueText || 'No songs in queue',
        inline: false
      });

      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Queue command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 