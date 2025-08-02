const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('nowplaying')
    .setDescription('Show the currently playing song'),
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
          content: '📭 No songs are currently playing!', 
          ephemeral: true 
        });
      }

      const currentSong = queue[0];
      
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🎵 Now Playing')
        .setDescription(`**${currentSong.title}**`)
        .setThumbnail(currentSong.thumbnail)
        .addFields(
          { name: 'Duration', value: musicManager.formatDuration(currentSong.duration), inline: true },
          { name: 'URL', value: `[Click here](${currentSong.url})`, inline: true },
          { name: 'Queue Position', value: `${queue.length} songs in queue`, inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Nowplaying command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 