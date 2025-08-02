const { Client, GatewayIntentBits } = require('discord.js');
require('dotenv').config();

const client = new Client({
  intents: [GatewayIntentBits.Guilds]
});

client.once('ready', () => {
  console.log('🤖 Bot is ready!');
  console.log('📋 Available guilds (servers):');
  
  client.guilds.cache.forEach(guild => {
    console.log(`   ${guild.name} (ID: ${guild.id})`);
  });
  
  console.log('\n📝 Copy one of the Guild IDs above and update your .env file');
  console.log('💡 Replace "your_guild_id_here" with the actual Guild ID');
  
  process.exit(0);
});

client.login(process.env.DISCORD_TOKEN).catch(error => {
  console.error('❌ Failed to login:', error.message);
  process.exit(1);
}); 