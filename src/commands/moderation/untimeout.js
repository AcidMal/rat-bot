const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('untimeout')
    .setDescription('Remove timeout from a user')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to remove timeout from')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for removing the timeout')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      const guild = interaction.guild;
      const member = await guild.members.fetch(targetUser.id);

      // Check permissions
      if (!interaction.member.permissions.has(PermissionFlagsBits.ModerateMembers)) {
        return await interaction.reply({
          content: '❌ You need the "Moderate Members" permission to use this command!',
          ephemeral: true
        });
      }

      // Check if user is timed out
      if (!member.isCommunicationDisabled()) {
        return await interaction.reply({
          content: '❌ This user is not timed out!',
          ephemeral: true
        });
      }

      // Remove timeout
      await member.timeout(null, reason);

      // Log the action
      const caseId = await databaseManager.addModlogEntry({
        guildId: guild.id,
        userId: targetUser.id,
        moderatorId: interaction.user.id,
        action: 'untimeout',
        reason: reason
      });

      // Create embed
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('✅ Timeout Removed')
        .setDescription(`**${targetUser.tag}**'s timeout has been removed`)
        .addFields(
          { name: 'Reason', value: reason, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Case ID', value: `#${caseId}`, inline: true }
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
              .setColor(0x00ff00)
              .setTitle('✅ Untimeout Log')
              .setDescription(`**${targetUser.tag}** (${targetUser.id}) had their timeout removed`)
              .addFields(
                { name: 'Reason', value: reason, inline: true },
                { name: 'Moderator', value: `${interaction.user.tag} (${interaction.user.id})`, inline: true },
                { name: 'Case ID', value: `#${caseId}`, inline: true }
              )
              .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
              .setTimestamp();

            await modlogChannel.send({ embeds: [modlogEmbed] });
          }
        } catch (error) {
          console.error('Error sending to modlog channel:', error);
        }
      }

    } catch (error) {
      console.error('Untimeout command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 