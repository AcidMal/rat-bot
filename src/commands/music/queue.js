const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('queue')
    .setDescription('Show the current music queue'),
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

      // This is a basic implementation - in a full music bot you'd have a queue system
      const embed = new EmbedBuilder()
        .setColor(0x0099ff)
        .setTitle('📋 Music Queue')
        .setDescription('No songs in queue.\n\n*This is a basic implementation. A full music bot would show the actual queue.*')
        .setTimestamp();

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