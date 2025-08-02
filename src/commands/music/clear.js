const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('clear')
    .setDescription('Clear the music queue'),
  async execute(interaction) {
    try {
      const guildId = interaction.guild.id;
      
      // Check if bot is in a voice channel
      const member = interaction.member;
      if (!member.voice.channel) {
        return await interaction.reply({ 
          content: '❌ You need to be in a voice channel to use this command!', 
          ephemeral: true 
        });
      }

      const queue = musicManager.getQueueInfo(guildId);
      
      if (queue.length === 0) {
        return await interaction.reply({ 
          content: '📭 The queue is already empty!', 
          ephemeral: true 
        });
      }

      // Clear the queue
      queue.length = 0;
      
      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('🗑️ Queue Cleared')
        .setDescription('All songs have been removed from the queue.')
        .addFields(
          { name: 'Songs removed', value: queue.length.toString(), inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Clear command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 