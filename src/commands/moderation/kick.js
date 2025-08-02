const { SlashCommandBuilder, PermissionFlagsBits, EmbedBuilder } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('kick')
    .setDescription('Kick a user from the server')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to kick')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for kicking the user')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.KickMembers),
  async execute(interaction) {
    const targetUser = interaction.options.getUser('user');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    
    try {
      const member = await interaction.guild.members.fetch(targetUser.id);
      
      if (!member.kickable) {
        return await interaction.reply({
          content: '❌ I cannot kick this user. They may have higher permissions than me.',
          ephemeral: true
        });
      }
      
      await member.kick(reason);
      
      // Log to database
      const result = databaseManager.addModlogEntry(
        interaction.guild.id,
        targetUser.id,
        interaction.user.id,
        'kick',
        reason
      );
      
      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('👢 User Kicked')
        .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
        .addFields(
          { name: 'User', value: `${targetUser.tag} (${targetUser.id})`, inline: true },
          { name: 'Kicked by', value: `${interaction.user.tag}`, inline: true },
          { name: 'Case ID', value: `#${result.lastInsertRowid}`, inline: true },
          { name: 'Reason', value: reason, inline: false }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
      // Send to modlog channel if configured
      const settings = databaseManager.getGuildSettings(interaction.guild.id);
      if (settings && settings.modlog_channel_id) {
        const modlogChannel = interaction.guild.channels.cache.get(settings.modlog_channel_id);
        if (modlogChannel) {
          const modlogEmbed = new EmbedBuilder()
            .setColor(0xff0000)
            .setTitle('👢 User Kicked')
            .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
            .addFields(
              { name: 'User', value: `${targetUser.tag} (${targetUser.id})`, inline: true },
              { name: 'Kicked by', value: `${interaction.user.tag}`, inline: true },
              { name: 'Case ID', value: `#${result.lastInsertRowid}`, inline: true },
              { name: 'Reason', value: reason, inline: false }
            )
            .setTimestamp();
          
          await modlogChannel.send({ embeds: [modlogEmbed] });
        }
      }
      
    } catch (error) {
      console.error('Kick command error:', error);
      await interaction.reply({
        content: '❌ Failed to kick the user. Make sure I have the necessary permissions.',
        ephemeral: true
      });
    }
  },
}; 