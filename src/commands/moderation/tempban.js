const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('tempban')
    .setDescription('Temporarily ban a user')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to temporarily ban')
        .setRequired(true))
    .addIntegerOption(option =>
      option.setName('days')
        .setDescription('Duration in days (1-7)')
        .setMinValue(1)
        .setMaxValue(7)
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for the temporary ban')
        .setRequired(false))
    .addIntegerOption(option =>
      option.setName('delete_messages')
        .setDescription('Number of days of messages to delete (0-7)')
        .setMinValue(0)
        .setMaxValue(7)
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.BanMembers),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user');
      const days = interaction.options.getInteger('days');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      const deleteMessages = interaction.options.getInteger('delete_messages') || 0;
      const guild = interaction.guild;

      // Check permissions
      if (!interaction.member.permissions.has(PermissionFlagsBits.BanMembers)) {
        return await interaction.reply({
          content: '❌ You need the "Ban Members" permission to use this command!',
          ephemeral: true
        });
      }

      // Check if user is already banned
      try {
        const ban = await guild.bans.fetch(targetUser.id);
        if (ban) {
          return await interaction.reply({
            content: '❌ This user is already banned!',
            ephemeral: true
          });
        }
      } catch (error) {
        // User is not banned, continue
      }

      // Calculate ban duration
      const banDuration = days * 24 * 60 * 60 * 1000; // Convert to milliseconds
      const banExpiry = new Date(Date.now() + banDuration);

      // Ban the user
      await guild.members.ban(targetUser, {
        reason: `${reason} (Temporary ban - expires ${banExpiry.toISOString()})`,
        deleteMessageDays: deleteMessages
      });

      // Log the action
      const caseId = await databaseManager.addModlogEntry({
        guildId: guild.id,
        userId: targetUser.id,
        moderatorId: interaction.user.id,
        action: 'tempban',
        reason: reason,
        duration: days,
        durationType: 'days'
      });

      // Create embed
      const embed = new EmbedBuilder()
        .setColor(0xff0000)
        .setTitle('🔨 User Temporarily Banned')
        .setDescription(`**${targetUser.tag}** has been temporarily banned`)
        .addFields(
          { name: 'Duration', value: `${days} days`, inline: true },
          { name: 'Reason', value: reason, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Case ID', value: `#${caseId}`, inline: true },
          { name: 'Expires', value: `<t:${Math.floor(banExpiry.getTime() / 1000)}:R>`, inline: true },
          { name: 'Messages Deleted', value: `${deleteMessages} days`, inline: true }
        )
        .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
        .setTimestamp();

      await interaction.reply({ embeds: [embed] });

      // Send to modlog channel if configured
      const settings = await databaseManager.getGuildSettings(guild.id);
      if (settings && settings.modlog_channel_id) {
        try {
          const modlogChannel = await guild.channels.fetch(settings.modlog_channel_id);
          if (modlogChannel) {
            const modlogEmbed = new EmbedBuilder()
              .setColor(0xff0000)
              .setTitle('🔨 Temporary Ban Log')
              .setDescription(`**${targetUser.tag}** (${targetUser.id}) was temporarily banned`)
              .addFields(
                { name: 'Duration', value: `${days} days`, inline: true },
                { name: 'Reason', value: reason, inline: true },
                { name: 'Moderator', value: `${interaction.user.tag} (${interaction.user.id})`, inline: true },
                { name: 'Case ID', value: `#${caseId}`, inline: true },
                { name: 'Expires', value: `<t:${Math.floor(banExpiry.getTime() / 1000)}:R>`, inline: true },
                { name: 'Messages Deleted', value: `${deleteMessages} days`, inline: true }
              )
              .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
              .setTimestamp();

            await modlogChannel.send({ embeds: [modlogEmbed] });
          }
        } catch (error) {
          console.error('Error sending to modlog channel:', error);
        }
      }

      // Schedule unban
      setTimeout(async () => {
        try {
          await guild.members.unban(targetUser.id, 'Temporary ban expired');
          
          // Log the automatic unban
          await databaseManager.addModlogEntry({
            guildId: guild.id,
            userId: targetUser.id,
            moderatorId: interaction.client.user.id,
            action: 'autounban',
            reason: 'Temporary ban expired'
          });

          // Send to modlog channel if configured
          if (settings && settings.modlog_channel_id) {
            try {
              const modlogChannel = await guild.channels.fetch(settings.modlog_channel_id);
              if (modlogChannel) {
                const autoUnbanEmbed = new EmbedBuilder()
                  .setColor(0x00ff00)
                  .setTitle('✅ Automatic Unban')
                  .setDescription(`**${targetUser.tag}** (${targetUser.id}) was automatically unbanned`)
                  .addFields(
                    { name: 'Reason', value: 'Temporary ban expired', inline: true },
                    { name: 'Case ID', value: `#${caseId}`, inline: true }
                  )
                  .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
                  .setTimestamp();

                await modlogChannel.send({ embeds: [autoUnbanEmbed] });
              }
            } catch (error) {
              console.error('Error sending auto-unban to modlog channel:', error);
            }
          }
        } catch (error) {
          console.error('Error auto-unbanning user:', error);
        }
      }, banDuration);

    } catch (error) {
      console.error('Tempban command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 