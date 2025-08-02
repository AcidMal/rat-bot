const { SlashCommandBuilder, PermissionFlagsBits, EmbedBuilder } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('ban')
    .setDescription('Ban a user from the server')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to ban')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for banning the user')
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('days')
        .setDescription('Number of days of messages to delete (0-7)')
        .setMinValue(0)
        .setMaxValue(7)
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
  async execute(interaction) {
    const targetUser = interaction.options.getUser('user');
    const reason = interaction.options.getString('reason') || 'No reason provided';
    const deleteMessageDays = interaction.options.getInteger('days') || 0;
    
    try {
      const member = await interaction.guild.members.fetch(targetUser.id);
      
      if (!member.bannable) {
        return await interaction.reply({
          content: '❌ I cannot ban this user. They may have higher permissions than me.',
          ephemeral: true
        });
      }
      
      await member.ban({ deleteMessageDays, reason });
      
      // Log to database
      const result = databaseManager.addModlogEntry(
        interaction.guild.id,
        targetUser.id,
        interaction.user.id,
        'ban',
        reason
      );
      
      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('🔨 User Banned')
        .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
        .addFields(
          { name: 'User', value: `${targetUser.tag} (${targetUser.id})`, inline: true },
          { name: 'Banned by', value: `${interaction.user.tag}`, inline: true },
          { name: 'Case ID', value: `#${result.lastInsertRowid}`, inline: true },
          { name: 'Reason', value: reason, inline: false },
          { name: 'Messages Deleted', value: `${deleteMessageDays} days`, inline: true }
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
            .setTitle('🔨 User Banned')
            .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
            .addFields(
              { name: 'User', value: `${targetUser.tag} (${targetUser.id})`, inline: true },
              { name: 'Banned by', value: `${interaction.user.tag}`, inline: true },
              { name: 'Case ID', value: `#${result.lastInsertRowid}`, inline: true },
              { name: 'Reason', value: reason, inline: false },
              { name: 'Messages Deleted', value: `${deleteMessageDays} days`, inline: true }
            )
            .setTimestamp();
          
          await modlogChannel.send({ embeds: [modlogEmbed] });
        }
      }
      
    } catch (error) {
      console.error('Ban command error:', error);
      await interaction.reply({
        content: '❌ Failed to ban the user. Make sure I have the necessary permissions.',
        ephemeral: true
      });
    }
  },
}; 