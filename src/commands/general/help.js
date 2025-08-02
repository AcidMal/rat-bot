const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('help')
    .setDescription('Display all available commands'),
  async execute(interaction) {
    const commands = interaction.client.commands;
    
    // Categorize commands
    const categories = {
      'General': ['ping', 'help', 'shardinfo'],
      'Info': ['info'],
      'Music': ['play', 'skip', 'stop', 'queue', 'clear', 'remove', 'shuffle', 'nowplaying'],
      'Moderation': ['kick', 'ban', 'timeout', 'untimeout', 'tempban', 'voicemute', 'voiceunmute', 'modlog', 'setup', 'automod']
    };
    
    const embed = new EmbedBuilder()
      .setColor(0x0099ff)
      .setTitle('🤖 Bot Commands')
      .setDescription('Here are all the available commands:')
      .setTimestamp();
    
    // Add fields for each category
    for (const [category, commandNames] of Object.entries(categories)) {
      const categoryCommands = commandNames
        .map(name => commands.get(name))
        .filter(cmd => cmd) // Only include commands that exist
        .map(cmd => `\`/${cmd.data.name}\` - ${cmd.data.description}`);
      
      if (categoryCommands.length > 0) {
        embed.addFields({
          name: `${category} Commands`,
          value: categoryCommands.join('\n'),
          inline: false
        });
      }
    }
    
    embed.setFooter({ text: 'Use /help <command> for detailed information about a specific command' });
    
    await interaction.reply({ embeds: [embed] });
  },
}; 