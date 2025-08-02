const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('voiceunmute')
    .setDescription('Unmute a user in voice channels')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to voice unmute')
        .setRequired(true))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for removing the voice mute')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.MuteMembers),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user');
      const reason = interaction.options.getString('reason') || 'No reason provided';
      const guild = interaction.guild;
      const member = await guild.members.fetch(targetUser.id);

      // Check permissions
      if (!interaction.member.permissions.has(PermissionFlagsBits.MuteMembers)) {
        return await interaction.reply({
          content: '❌ You need the "Mute Members" permission to use this command!',
          ephemeral: true
        });
      }

      // Check if user is in a voice channel
      if (!member.voice.channel) {
        return await interaction.reply({
          content: '❌ This user is not in a voice channel!',
          ephemeral: true
        });
      }

      // Check if user is voice muted
      if (!member.voice.serverMute) {
        return await interaction.reply({
          content: '❌ This user is not voice muted!',
          ephemeral: true
        });
      }

      // Unmute the user
      await member.voice.setMute(false, reason);

      // Log the action
      const caseId = await databaseManager.addModlogEntry({
        guildId: guild.id,
        userId: targetUser.id,
        moderatorId: interaction.user.id,
        action: 'voiceunmute',
        reason: reason
      });

      // Create embed
      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🔊 User Voice Unmuted')
        .setDescription(`**${targetUser.tag}** has been voice unmuted`)
        .addFields(
          { name: 'Reason', value: reason, inline: true },
          { name: 'Moderator', value: interaction.user.tag, inline: true },
          { name: 'Case ID', value: `#${caseId}`, inline: true },
          { name: 'Voice Channel', value: member.voice.channel.name, inline: true }
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
              .setTitle('🔊 Voice Unmute Log')
              .setDescription(`**${targetUser.tag}** (${targetUser.id}) was voice unmuted`)
              .addFields(
                { name: 'Reason', value: reason, inline: true },
                { name: 'Moderator', value: `${interaction.user.tag} (${interaction.user.id})`, inline: true },
                { name: 'Case ID', value: `#${caseId}`, inline: true },
                { name: 'Voice Channel', value: member.voice.channel.name, inline: true }
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
      console.error('Voiceunmute command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 