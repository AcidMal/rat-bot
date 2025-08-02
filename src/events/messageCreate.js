const { Events, EmbedBuilder } = require('discord.js');
const databaseManager = require('../utils/databaseManager');

module.exports = {
  name: Events.MessageCreate,
  async execute(message) {
    // Ignore bot messages and DMs
    if (message.author.bot || !message.guild) return;

    try {
      // Get guild settings
      const settings = await databaseManager.getGuildSettings(message.guild.id);
      if (!settings) return;

      const member = message.member;
      const content = message.content.toLowerCase();
      const channel = message.channel;

      // Anti Spam Check
      if (settings.antispam_enabled) {
        const userKey = `${message.author.id}_spam`;
        const now = Date.now();
        
        if (!global.spamTracker) global.spamTracker = new Map();
        
        const userData = global.spamTracker.get(userKey) || { messages: [], lastReset: now };
        
        // Reset if more than 10 seconds have passed
        if (now - userData.lastReset > 10000) {
          userData.messages = [];
          userData.lastReset = now;
        }
        
        userData.messages.push(now);
        global.spamTracker.set(userKey, userData);
        
        // Check if user is spamming (more than threshold messages in 10 seconds)
        const recentMessages = userData.messages.filter(time => now - time <= 10000);
        if (recentMessages.length > settings.antispam_threshold) {
          await handleAutoModAction(message, settings.antispam_action, 'Anti Spam', settings);
          return;
        }
      }

      // Anti Caps Check
      if (settings.anticaps_enabled && content.length > 10) {
        const capsCount = (content.match(/[A-Z]/g) || []).length;
        const capsPercentage = (capsCount / content.length) * 100;
        
        if (capsPercentage > settings.anticaps_threshold) {
          await handleAutoModAction(message, settings.anticaps_action, 'Anti Caps', settings);
          return;
        }
      }

      // Anti Links Check
      if (settings.antilinks_enabled) {
        const linkPatterns = [
          /https?:\/\/[^\s]+/g,
          /discord\.gg\/[^\s]+/g,
          /discord\.com\/invite\/[^\s]+/g
        ];
        
        for (const pattern of linkPatterns) {
          if (pattern.test(content)) {
            await handleAutoModAction(message, settings.antilinks_action, 'Anti Links', settings);
            return;
          }
        }
      }

      // Anti Invite Check
      if (settings.antiinvite_enabled) {
        const invitePattern = /discord\.gg\/[^\s]+|discord\.com\/invite\/[^\s]+/g;
        if (invitePattern.test(content)) {
          await handleAutoModAction(message, settings.antiinvite_action, 'Anti Invite', settings);
          return;
        }
      }

      // Mass Mention Check
      if (settings.massmention_enabled) {
        const mentionCount = (content.match(/@/g) || []).length;
        if (mentionCount > settings.massmention_threshold) {
          await handleAutoModAction(message, settings.massmention_action, 'Mass Mention', settings);
          return;
        }
      }

      // Word Filter Check (basic implementation)
      if (settings.wordfilter_enabled) {
        const badWords = ['spam', 'badword']; // This would be configurable in a real implementation
        for (const word of badWords) {
          if (content.includes(word)) {
            await handleAutoModAction(message, settings.wordfilter_action, 'Word Filter', settings);
            return;
          }
        }
      }

    } catch (error) {
      console.error('Auto-mod error:', error);
    }
  },
};

async function handleAutoModAction(message, action, reason, settings) {
  try {
    const member = message.member;
    const guild = message.guild;

    // Log the auto-mod action
    const caseId = await databaseManager.addModlogEntry({
      guildId: guild.id,
      userId: message.author.id,
      moderatorId: message.client.user.id,
      action: `auto_${action}`,
      reason: `Auto-mod: ${reason}`
    });

    // Create embed for logging
    const embed = new EmbedBuilder()
      .setColor(0xff8800)
      .setTitle('🛡️ Auto-Mod Action')
      .setDescription(`**${message.author.tag}** triggered auto-moderation`)
      .addFields(
        { name: 'Reason', value: reason, inline: true },
        { name: 'Action', value: action, inline: true },
        { name: 'Channel', value: message.channel.name, inline: true },
        { name: 'Case ID', value: `#${caseId}`, inline: true }
      )
      .setThumbnail(message.author.displayAvatarURL({ dynamic: true }))
      .setTimestamp();

    // Send to modlog channel if configured
    if (settings.modlog_channel_id) {
      try {
        const modlogChannel = await guild.channels.fetch(settings.modlog_channel_id);
        if (modlogChannel) {
          await modlogChannel.send({ embeds: [embed] });
        }
      } catch (error) {
        console.error('Error sending auto-mod to modlog channel:', error);
      }
    }

    // Execute the action
    switch (action) {
      case 'delete':
        try {
          await message.delete();
        } catch (error) {
          console.error('Error deleting message:', error);
        }
        break;

      case 'warn':
        try {
          await message.reply({
            content: `⚠️ **${message.author}**, your message was flagged by auto-moderation for: **${reason}**`,
            ephemeral: false
          });
        } catch (error) {
          console.error('Error warning user:', error);
        }
        break;

      case 'timeout':
        try {
          if (member.moderatable) {
            await member.timeout(5 * 60 * 1000, `Auto-mod: ${reason}`);
          }
        } catch (error) {
          console.error('Error timing out user:', error);
        }
        break;

      case 'kick':
        try {
          if (member.kickable) {
            await member.kick(`Auto-mod: ${reason}`);
          }
        } catch (error) {
          console.error('Error kicking user:', error);
        }
        break;
    }

  } catch (error) {
    console.error('Error handling auto-mod action:', error);
  }
} 