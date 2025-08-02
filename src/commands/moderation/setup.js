const { SlashCommandBuilder, PermissionFlagsBits, EmbedBuilder } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('setup')
    .setDescription('Configure bot settings for this server')
    .addChannelOption(option =>
      option.setName('modlog_channel')
        .setDescription('Channel for moderation logs')
        .setRequired(false))
    .addChannelOption(option =>
      option.setName('welcome_channel')
        .setDescription('Channel for welcome messages')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild),
  async execute(interaction) {
    const modlogChannel = interaction.options.getChannel('modlog_channel');
    const welcomeChannel = interaction.options.getChannel('welcome_channel');
    
    try {
      // Get current settings
      const currentSettings = databaseManager.getGuildSettings(interaction.guild.id) || {};
      
      // Update settings
      const newSettings = {
        modlog_channel_id: modlogChannel ? modlogChannel.id : currentSettings.modlog_channel_id,
        welcome_channel_id: welcomeChannel ? welcomeChannel.id : currentSettings.welcome_channel_id,
        prefix: currentSettings.prefix || '!'
      };
      
      databaseManager.setGuildSettings(interaction.guild.id, newSettings);
      
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('⚙️ Server Settings Updated')
        .addFields(
          { 
            name: 'Modlog Channel', 
            value: modlogChannel ? `<#${modlogChannel.id}>` : (currentSettings.modlog_channel_id ? `<#${currentSettings.modlog_channel_id}>` : 'Not set'), 
            inline: true 
          },
          { 
            name: 'Welcome Channel', 
            value: welcomeChannel ? `<#${welcomeChannel.id}>` : (currentSettings.welcome_channel_id ? `<#${currentSettings.welcome_channel_id}>` : 'Not set'), 
            inline: true 
          },
          { 
            name: 'Prefix', 
            value: newSettings.prefix, 
            inline: true 
          }
        )
        .setTimestamp();
      
      await interaction.reply({ embeds: [embed] });
      
    } catch (error) {
      console.error('Setup command error:', error);
      await interaction.reply({
        content: '❌ An error occurred while updating server settings.',
        ephemeral: true
      });
    }
  },
}; 