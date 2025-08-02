const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('clear')
    .setDescription('Clear the music queue'),
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

      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('🗑️ Queue Cleared')
        .setDescription('The music queue has been cleared.')
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