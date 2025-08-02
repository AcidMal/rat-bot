const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('stop')
    .setDescription('Stop playing and leave the voice channel'),
  async execute(interaction) {
    try {
      const member = interaction.member;

      // Check if user is in a voice channel
      if (!member.voice.channel) {
        return await interaction.reply({
          content: '❌ You need to be in a voice channel to use this command!',
          ephemeral: true
        });
      }

      // Check if bot is in a voice channel
      const botMember = interaction.guild.members.cache.get(interaction.client.user.id);
      if (!botMember.voice.channel) {
        return await interaction.reply({
          content: '❌ I am not currently playing any music!',
          ephemeral: true
        });
      }

      // Leave the voice channel
      botMember.voice.disconnect();

      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('⏹️ Music Stopped')
        .setDescription('Stopped playing and left the voice channel.')
        .setTimestamp();

      await interaction.reply({ embeds: [embed] });

    } catch (error) {
      console.error('Stop command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 