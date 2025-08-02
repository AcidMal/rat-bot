const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('timeout')
    .setDescription('Timeout a user temporarily')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to timeout')
        .setRequired(true))
    .addIntegerOption(option =>
      option.setName('duration')
        .setDescription('Duration in minutes (1-40320)')
        .setMinValue(1)
        .setMaxValue(40320)
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for the timeout')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.ModerateMembers),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user');
      const duration = interaction.options.getInteger('duration');
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

      // Check if target is timeoutable
      if (!member.moderatable) {
        return await interaction.reply({
          content: '❌ I cannot timeout this user! They may have higher permissions than me.',
          ephemeral: true
        });
      }

      // Check if user is already timed out
      if (member.isCommunicationDisabled()) {
        return await interaction.reply({
          content: '❌ This user is already timed out!',
          ephemeral: true
        });
      }

      // Calculate timeout duration
      const timeoutDuration = duration * 60 * 1000; // Convert to milliseconds
      const timeoutDate = new Date(Date.now() + timeoutDuration);

      // Apply timeout
      await member.timeout(timeoutDuration, reason);

      // Log the action
      const caseId = await databaseManager.addModlogEntry({
        guildId: guild.id,
        userId: targetUser.id,
        moderatorId: interaction.user.id,
        action: 'timeout',
        reason: reason,
        duration: duration,
        durationType: 'minutes'
      });

      // Create embed
      const embed = new EmbedBuilder()
        .setColor(0xff8800)
        .setTitle('⏰ User Timed Out')
        .setDescription(`**${targetUser.tag}** has been timed out`)
        .addFields(
          { name: 'Duration', value: `${duration} minutes`, inline: true },
          { name: 'Reason', value: reason, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Case ID', value: `#${caseId}`, inline: true },
          { name: 'Expires', value: `<t:${Math.floor(timeoutDate.getTime() / 1000)}:R>`, inline: true }
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
              .setColor(0xff8800)
              .setTitle('⏰ Timeout Log')
              .setDescription(`**${targetUser.tag}** (${targetUser.id}) was timed out`)
              .addFields(
                { name: 'Duration', value: `${duration} minutes`, inline: true },
                { name: 'Reason', value: reason, inline: true },
                { name: 'Moderator', value: `${interaction.user.tag} (${interaction.user.id})`, inline: true },
                { name: 'Case ID', value: `#${caseId}`, inline: true },
                { name: 'Expires', value: `<t:${Math.floor(timeoutDate.getTime() / 1000)}:R>`, inline: true }
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
      console.error('Timeout command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 