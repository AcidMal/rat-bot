const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('info')
    .setDescription('Get information about a user or yourself')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to get information about')
        .setRequired(false)),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user') || interaction.user;
      const member = await interaction.guild.members.fetch(targetUser.id);
      
      const embed = new EmbedBuilder()
        .setColor(0x0099ff)
        .setTitle(`User Information - ${targetUser.username}`)
        .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
        .addFields(
          { name: 'Username', value: targetUser.username, inline: true },
          { name: 'Discriminator', value: targetUser.discriminator, inline: true },
          { name: 'ID', value: targetUser.id, inline: true },
          { name: 'Created At', value: `<t:${Math.floor(targetUser.createdTimestamp / 1000)}:F>`, inline: true },
          { name: 'Joined At', value: `<t:${Math.floor(member.joinedTimestamp / 1000)}:F>`, inline: true },
          { name: 'Nickname', value: member.nickname || 'None', inline: true }
        )
        .setFooter({ text: `Requested by ${interaction.user.tag}` })
        .setTimestamp();

      await interaction.reply({ embeds: [embed] });
    } catch (error) {
      console.error('Info command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 