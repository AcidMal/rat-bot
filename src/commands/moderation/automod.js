const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('automod')
    .setDescription('Configure auto-moderation settings')
    .addSubcommand(subcommand =>
      subcommand
        .setName('view')
        .setDescription('View current auto-mod settings'))
    .addSubcommand(subcommand =>
      subcommand
        .setName('enable')
        .setDescription('Enable auto-moderation')
        .addStringOption(option =>
          option.setName('feature')
            .setDescription('Auto-mod feature to enable')
            .setRequired(true)
            .addChoices(
              { name: 'Anti Spam', value: 'antispam' },
              { name: 'Anti Caps', value: 'anticaps' },
              { name: 'Anti Links', value: 'antilinks' },
              { name: 'Anti Invite', value: 'antiinvite' },
              { name: 'Word Filter', value: 'wordfilter' },
              { name: 'Mass Mention', value: 'massmention' }
            )))
    .addSubcommand(subcommand =>
      subcommand
        .setName('disable')
        .setDescription('Disable auto-moderation')
        .addStringOption(option =>
          option.setName('feature')
            .setDescription('Auto-mod feature to disable')
            .setRequired(true)
            .addChoices(
              { name: 'Anti Spam', value: 'antispam' },
              { name: 'Anti Caps', value: 'anticaps' },
              { name: 'Anti Links', value: 'antilinks' },
              { name: 'Anti Invite', value: 'antiinvite' },
              { name: 'Word Filter', value: 'wordfilter' },
              { name: 'Mass Mention', value: 'massmention' }
            )))
    .addSubcommand(subcommand =>
      subcommand
        .setName('threshold')
        .setDescription('Set auto-mod thresholds')
        .addStringOption(option =>
          option.setName('feature')
            .setDescription('Feature to configure')
            .setRequired(true)
            .addChoices(
              { name: 'Anti Spam', value: 'antispam' },
              { name: 'Anti Caps', value: 'anticaps' },
              { name: 'Mass Mention', value: 'massmention' }
            ))
        .addIntegerOption(option =>
          option.setName('threshold')
            .setDescription('Threshold value (1-10)')
            .setMinValue(1)
            .setMaxValue(10)
            .setRequired(true)))
    .addSubcommand(subcommand =>
      subcommand
        .setName('action')
        .setDescription('Set auto-mod actions')
        .addStringOption(option =>
          option.setName('feature')
            .setDescription('Feature to configure')
            .setRequired(true)
            .addChoices(
              { name: 'Anti Spam', value: 'antispam' },
              { name: 'Anti Caps', value: 'anticaps' },
              { name: 'Anti Links', value: 'antilinks' },
              { name: 'Anti Invite', value: 'antiinvite' },
              { name: 'Word Filter', value: 'wordfilter' },
              { name: 'Mass Mention', value: 'massmention' }
            ))
        .addStringOption(option =>
          option.setName('action')
            .setDescription('Action to take')
            .setRequired(true)
            .addChoices(
              { name: 'Delete Message', value: 'delete' },
              { name: 'Warn User', value: 'warn' },
              { name: 'Timeout User', value: 'timeout' },
              { name: 'Kick User', value: 'kick' }
            )))
    .setDefaultMemberPermissions(PermissionFlagsBits.ManageGuild),
  async execute(interaction) {
    try {
      const subcommand = interaction.options.getSubcommand();
      const guild = interaction.guild;

      // Check permissions
      if (!interaction.member.permissions.has(PermissionFlagsBits.ManageGuild)) {
        return await interaction.reply({
          content: '❌ You need the "Manage Guild" permission to use this command!',
          ephemeral: true
        });
      }

      // Get current settings
      let settings = await databaseManager.getGuildSettings(guild.id);
      if (!settings) {
        settings = {
          guild_id: guild.id,
          automod_enabled: false,
          antispam_enabled: false,
          anticaps_enabled: false,
          antilinks_enabled: false,
          antiinvite_enabled: false,
          wordfilter_enabled: false,
          massmention_enabled: false,
          antispam_threshold: 5,
          anticaps_threshold: 70,
          massmention_threshold: 5,
          antispam_action: 'delete',
          anticaps_action: 'delete',
          antilinks_action: 'delete',
          antiinvite_action: 'delete',
          wordfilter_action: 'delete',
          massmention_action: 'delete'
        };
        await databaseManager.setGuildSettings(guild.id, settings);
      }

      if (subcommand === 'view') {
        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle('🛡️ Auto-Mod Settings')
          .setDescription(`Current auto-moderation settings for **${guild.name}**`)
          .addFields(
            { 
              name: '📊 Features Status', 
              value: `**Anti Spam:** ${settings.antispam_enabled ? '✅' : '❌'}\n` +
                     `**Anti Caps:** ${settings.anticaps_enabled ? '✅' : '❌'}\n` +
                     `**Anti Links:** ${settings.antilinks_enabled ? '✅' : '❌'}\n` +
                     `**Anti Invite:** ${settings.antiinvite_enabled ? '✅' : '❌'}\n` +
                     `**Word Filter:** ${settings.wordfilter_enabled ? '✅' : '❌'}\n` +
                     `**Mass Mention:** ${settings.massmention_enabled ? '✅' : '❌'}`, 
              inline: false 
            },
            { 
              name: '⚙️ Thresholds', 
              value: `**Anti Spam:** ${settings.antispam_threshold}/10\n` +
                     `**Anti Caps:** ${settings.anticaps_threshold}%\n` +
                     `**Mass Mention:** ${settings.massmention_threshold} mentions`, 
              inline: true 
            },
            { 
              name: '🔨 Actions', 
              value: `**Anti Spam:** ${settings.antispam_action}\n` +
                     `**Anti Caps:** ${settings.anticaps_action}\n` +
                     `**Anti Links:** ${settings.antilinks_action}\n` +
                     `**Anti Invite:** ${settings.antiinvite_action}\n` +
                     `**Word Filter:** ${settings.wordfilter_action}\n` +
                     `**Mass Mention:** ${settings.massmention_action}`, 
              inline: true 
            }
          )
          .setTimestamp();

        await interaction.reply({ embeds: [embed] });

      } else if (subcommand === 'enable') {
        const feature = interaction.options.getString('feature');
        const featureKey = `${feature}_enabled`;
        
        if (settings[featureKey]) {
          return await interaction.reply({
            content: `❌ **${feature}** is already enabled!`,
            ephemeral: true
          });
        }

        settings[featureKey] = true;
        await databaseManager.setGuildSettings(guild.id, settings);

        const embed = new EmbedBuilder()
          .setColor(0x00ff00)
          .setTitle('✅ Auto-Mod Enabled')
          .setDescription(`**${feature}** has been enabled`)
          .setTimestamp();

        await interaction.reply({ embeds: [embed] });

      } else if (subcommand === 'disable') {
        const feature = interaction.options.getString('feature');
        const featureKey = `${feature}_enabled`;
        
        if (!settings[featureKey]) {
          return await interaction.reply({
            content: `❌ **${feature}** is already disabled!`,
            ephemeral: true
          });
        }

        settings[featureKey] = false;
        await databaseManager.setGuildSettings(guild.id, settings);

        const embed = new EmbedBuilder()
          .setColor(0xff0000)
          .setTitle('❌ Auto-Mod Disabled')
          .setDescription(`**${feature}** has been disabled`)
          .setTimestamp();

        await interaction.reply({ embeds: [embed] });

      } else if (subcommand === 'threshold') {
        const feature = interaction.options.getString('feature');
        const threshold = interaction.options.getInteger('threshold');
        const thresholdKey = `${feature}_threshold`;
        
        settings[thresholdKey] = threshold;
        await databaseManager.setGuildSettings(guild.id, settings);

        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle('⚙️ Threshold Updated')
          .setDescription(`**${feature}** threshold set to **${threshold}**`)
          .setTimestamp();

        await interaction.reply({ embeds: [embed] });

      } else if (subcommand === 'action') {
        const feature = interaction.options.getString('feature');
        const action = interaction.options.getString('action');
        const actionKey = `${feature}_action`;
        
        settings[actionKey] = action;
        await databaseManager.setGuildSettings(guild.id, settings);

        const embed = new EmbedBuilder()
          .setColor(0x0099ff)
          .setTitle('🔨 Action Updated')
          .setDescription(`**${feature}** action set to **${action}**`)
          .setTimestamp();

        await interaction.reply({ embeds: [embed] });
      }

    } catch (error) {
      console.error('Automod command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 