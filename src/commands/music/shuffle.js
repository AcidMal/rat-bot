const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('shuffle')
    .setDescription('Shuffle the music queue'),
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
      
      if (queue.length < 2) {
        return await interaction.reply({ 
          content: '📭 Need at least 2 songs in the queue to shuffle!', 
          ephemeral: true 
        });
      }

      // Shuffle the queue (Fisher-Yates algorithm)
      for (let i = queue.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [queue[i], queue[j]] = [queue[j], queue[i]];
      }
      
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🔀 Queue Shuffled')
        .setDescription(`Shuffled ${queue.length} songs in the queue`)
        .addFields(
          { name: 'Songs in queue', value: queue.length.toString(), inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Shuffle command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 