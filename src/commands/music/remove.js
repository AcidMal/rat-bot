const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('remove')
    .setDescription('Remove a song from the queue')
    .addIntegerOption(option =>
      option.setName('position')
        .setDescription('Position of the song to remove (1, 2, 3, etc.)')
        .setMinValue(1)
        .setRequired(true)),
  async execute(interaction) {
    try {
      const guildId = interaction.guild.id;
      const position = interaction.options.getInteger('position');
      
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
          content: '📭 The queue is empty!', 
          ephemeral: true 
        });
      }

      if (position > queue.length) {
        return await interaction.reply({ 
          content: `❌ Invalid position! Queue only has ${queue.length} songs.`, 
          ephemeral: true 
        });
      }

      // Remove the song at the specified position
      const removedSong = queue.splice(position - 1, 1)[0];
      
      const embed = new EmbedBuilder()
        .setColor(0xff8800)
        .setTitle('🗑️ Song Removed')
        .setDescription(`**${removedSong.title}** has been removed from position ${position}`)
        .addFields(
          { name: 'Songs remaining', value: queue.length.toString(), inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Remove command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 