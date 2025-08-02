const { SlashCommandBuilder, EmbedBuilder, PermissionFlagsBits } = require('discord.js');
const databaseManager = require('../../utils/databaseManager');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('voicemute')
    .setDescription('Mute a user in voice channels')
    .addUserOption(option =>
      option.setName('user')
        .setDescription('The user to voice mute')
        .setRequired(true))
    .addIntegerOption(option =>
      option.setName('duration')
        .setDescription('Duration in minutes (1-40320)')
        .setMinValue(1)
        .setMaxValue(40320)
        .setRequired(false))
    .addStringOption(option =>
      option.setName('reason')
        .setDescription('Reason for the voice mute')
        .setRequired(false))
    .setDefaultMemberPermissions(PermissionFlagsBits.MuteMembers),
  async execute(interaction) {
    try {
      const targetUser = interaction.options.getUser('user');
      const duration = interaction.options.getInteger('duration');
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

      // Check if target is manageable
      if (!member.manageable) {
        return await interaction.reply({
          content: '❌ I cannot mute this user! They may have higher permissions than me.',
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

      // Check if user is already voice muted
      if (member.voice.serverMute) {
        return await interaction.reply({
          content: '❌ This user is already voice muted!',
          ephemeral: true
        });
      }

      // Mute the user
      await member.voice.setMute(true, reason);

      // Log the action
      const caseId = await databaseManager.addModlogEntry({
        guildId: guild.id,
        userId: targetUser.id,
        moderatorId: interaction.user.id,
        action: 'voicemute',
        reason: reason,
        duration: duration,
        durationType: 'minutes'
      });

      // Create embed
      const embed = new EmbedBuilder()
        .setColor(0xff8800)
        .setTitle('🔇 User Voice Muted')
        .setDescription(`**${targetUser.tag}** has been voice muted`)
        .addFields(
          { name: 'Duration', value: duration ? `${duration} minutes` : 'Indefinite', inline: true },
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
              .setColor(0xff8800)
              .setTitle('🔇 Voice Mute Log')
              .setDescription(`**${targetUser.tag}** (${targetUser.id}) was voice muted`)
              .addFields(
                { name: 'Duration', value: duration ? `${duration} minutes` : 'Indefinite', inline: true },
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

      // Auto-unmute after duration if specified
      if (duration) {
        setTimeout(async () => {
          try {
            if (member.voice.serverMute) {
              await member.voice.setMute(false, 'Voice mute duration expired');
              
              // Log the automatic unmute
              await databaseManager.addModlogEntry({
                guildId: guild.id,
                userId: targetUser.id,
                moderatorId: interaction.client.user.id,
                action: 'autovoiceunmute',
                reason: 'Voice mute duration expired'
              });

              // Send to modlog channel if configured
              if (settings && settings.modlog_channel_id) {
                try {
                  const modlogChannel = await guild.channels.fetch(settings.modlog_channel_id);
                  if (modlogChannel) {
                    const autoUnmuteEmbed = new EmbedBuilder()
                      .setColor(0x00ff00)
                      .setTitle('🔊 Automatic Voice Unmute')
                      .setDescription(`**${targetUser.tag}** (${targetUser.id}) was automatically voice unmuted`)
                      .addFields(
                        { name: 'Reason', value: 'Voice mute duration expired', inline: true },
                        { name: 'Case ID', value: `#${caseId}`, inline: true }
                      )
                      .setThumbnail(targetUser.displayAvatarURL({ dynamic: true }))
                      .setTimestamp();

                    await modlogChannel.send({ embeds: [autoUnmuteEmbed] });
                  }
                } catch (error) {
                  console.error('Error sending auto-unmute to modlog channel:', error);
                }
              }
            }
          } catch (error) {
            console.error('Error auto-unmuting user:', error);
          }
        }, duration * 60 * 1000);
      }

    } catch (error) {
      console.error('Voicemute command error:', error);
      await interaction.reply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
}; 