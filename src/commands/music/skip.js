const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const musicManager = require('../../utils/musicManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('skip')
    .setDescription('Skip songs in the queue')
    .addIntegerOption(option =>
      option.setName('position')
        .setDescription('Position of the song to skip (1, 2, 3, etc.)')
        .setMinValue(1)
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('amount')
        .setDescription('Number of songs to skip from current position')
        .setMinValue(1)
        .setMaxValue(10)
        .setRequired(false)),
  async execute(interaction) {
    try {
      const guildId = interaction.guild.id;
      const position = interaction.options.getInteger('position');
      const amount = interaction.options.getInteger('amount');
      
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

      let skipMessage = '';
      
      if (position) {
        // Skip specific song at position
        if (position > queue.length) {
          return await interaction.reply({ 
            content: `❌ Invalid position! Queue only has ${queue.length} songs.`, 
            ephemeral: true 
          });
        }
        
        const songToSkip = queue[position - 1];
        queue.splice(position - 1, 1);
        
        skipMessage = `⏭️ Skipped **${songToSkip.title}** (position ${position})`;
        
        // If we skipped the current song, play the next one
        if (position === 1) {
          musicManager.skip(guildId);
        }
        
      } else if (amount) {
        // Skip multiple songs from current position
        const songsToSkip = queue.splice(0, amount);
        const songTitles = songsToSkip.map(song => song.title).join(', ');
        
        skipMessage = `⏭️ Skipped ${amount} song(s): **${songTitles}**`;
        
        // Play next song if we skipped the current one
        if (amount > 0) {
          musicManager.skip(guildId);
        }
        
      } else {
        // Skip current song only
        const currentSong = queue[0];
        musicManager.skip(guildId);
        skipMessage = `⏭️ Skipped **${currentSong.title}**`;
      }
      
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🎵 Skip Action')
        .setDescription(skipMessage)
        .addFields(
          { name: 'Songs remaining', value: queue.length.toString(), inline: true }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Skip command error:', error);
      await interaction.reply({ 
        content: `❌ Error: ${error.message}`, 
        ephemeral: true 
      });
    }
  },
}; 