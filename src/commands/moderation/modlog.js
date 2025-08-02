const { SlashCommandBuilder, PermissionFlagsBits, EmbedBuilder } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('modlog')
    .setDescription('View moderation logs')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('User to view logs for')
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('case')
        .setDescription('Specific case ID to view')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageMessages),
  async execute(interaction) {
    const targetUser = interaction.options.getUser('user');
    const caseId = interaction.options.getInteger('case');
    
    try {
      if (caseId) {
        // View specific case
        const caseData = databaseManager.getModlogCase(interaction.guild.id, caseId);
        
        if (!caseData) {
          return await interaction.reply({
            content: `❌ Case #${caseId} not found.`,
            ephemeral: true
          });
        }
        
        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle(`📋 Case #${caseId}`)
          .addFields(
            { name: 'Action', value: caseData.action.toUpperCase(), inline: true },
            { name: 'User', value: `<@${caseData.user_id}>`, inline: true },
            { name: 'Moderator', value: `<@${caseData.moderator_id}>`, inline: true },
            { name: 'Reason', value: caseData.reason || 'No reason provided', inline: false },
            { name: 'Date', value: new Date(caseData.timestamp).toLocaleString(), inline: true }
          )
          .setTimestamp();
        
        await interaction.reply({ embeds: [embed] });
        
      } else if (targetUser) {
        // View user's modlog
        const userLogs = databaseManager.getUserModlog(interaction.guild.id, targetUser.id, 10);
        
        if (userLogs.length === 0) {
          return await interaction.reply({
            content: `📭 No moderation history found for ${targetUser.tag}.`,
            ephemeral: true
          });
        }
        
        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle(`📋 Moderation History - ${targetUser.tag}`)
          .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }));
        
        let logText = '';
        userLogs.forEach(log => {
          const date = new Date(log.timestamp).toLocaleDateString();
          logText += `**Case #${log.case_id}** - ${log.action.toUpperCase()} by <@${log.moderator_id}>\n`;
          logText += `└ Reason: ${log.reason || 'No reason provided'}\n`;
          logText += `└ Date: ${date}\n\n`;
        });
        
        embed.setDescription(logText);
        embed.setFooter({ text: `Showing last ${userLogs.length} entries` });
        
        await interaction.reply({ embeds: [embed] });
        
      } else {
        // View recent guild modlog
        const guildLogs = databaseManager.getGuildModlog(interaction.guild.id, 10);
        
        if (guildLogs.length === 0) {
          return await interaction.reply({
            content: '📭 No moderation history found for this server.',
            ephemeral: true
          });
        }
        
        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle('📋 Recent Moderation Actions');
        
        let logText = '';
        guildLogs.forEach(log => {
          const date = new Date(log.timestamp).toLocaleDateString();
          logText += `**Case #${log.case_id}** - ${log.action.toUpperCase()}\n`;
          logText += `└ User: <@${log.user_id}>\n`;
          logText += `└ Moderator: <@${log.moderator_id}>\n`;
          logText += `└ Reason: ${log.reason || 'No reason provided'}\n`;
          logText += `└ Date: ${date}\n\n`;
        });
        
        embed.setDescription(logText);
        embed.setFooter({ text: `Showing last ${guildLogs.length} entries` });
        
        await interaction.reply({ embeds: [embed] });
      }
      
    } catch (error) {
      console.error('Modlog command error:', error);
      await interaction.reply({
        content: '❌ An error occurred while fetching the modlog.',
        ephemeral: true
      });
    }
  },
}; 