const { Client, GatewayIntentBits, Collection } = require('discord.js');
const { joinVoiceChannel } = require('@discordjs/voice');
const fs = require('fs');
const path = require('path');
const envPath = path.join(__dirname, '../.env');
console.log('🔍 Loading .env from:', envPath);
require('dotenv').config({ path: envPath });
console.log('🔍 Environment variables loaded. Token exists:', !!process.env.DISCORD_TOKEN);

console.log('🚀 Starting Discord Bot...');
console.log('📁 Current directory:', process.cwd());
console.log('🔧 Node version:', process.version);

// Check if .env file exists
console.log('🔍 Looking for .env file at:', envPath);
if (!fs.existsSync(envPath)) {
  console.error('❌ .env file not found! Please create one based on env.example');
  process.exit(1);
}
console.log('✅ .env file found');

// Check if DISCORD_TOKEN exists
if (!process.env.DISCORD_TOKEN) {
  console.error('❌ DISCORD_TOKEN not found in .env file!');
  process.exit(1);
}

console.log('✅ Environment variables loaded');

// Create a new client instance
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.GuildVoiceStates,
  ],
  shards: process.env.SHARD_ID ? [parseInt(process.env.SHARD_ID)] : undefined,
});

// Add shard and cluster information to client
client.shardId = process.env.SHARD_ID ? parseInt(process.env.SHARD_ID) : 0;
client.clusterId = process.env.CLUSTER_ID ? parseInt(process.env.CLUSTER_ID) : 0;

// Create a collection for commands
client.commands = new Collection();

// Load commands recursively
function loadCommands(dir) {
  try {
    console.log(`📂 Loading commands from: ${dir}`);
    const commandFiles = fs.readdirSync(dir);
    console.log(`📄 Found ${commandFiles.length} files in commands directory`);
    
    for (const file of commandFiles) {
      const filePath = path.join(dir, file);
      const stat = fs.statSync(filePath);
      
      if (stat.isDirectory()) {
        // Recursively load commands from subdirectories
        console.log(`📁 Loading subdirectory: ${file}`);
        loadCommands(filePath);
      } else if (file.endsWith('.js')) {
        try {
          console.log(`📄 Loading command: ${file}`);
          const command = require(filePath);
          
          // Set a new item in the Collection with the key as the command name and the value as the exported module
          if ('data' in command && 'execute' in command) {
            client.commands.set(command.data.name, command);
            console.log(`✅ Loaded command: ${command.data.name}`);
          } else {
            console.log(`⚠️  The command at ${filePath} is missing a required "data" or "execute" property.`);
          }
        } catch (error) {
          console.error(`❌ Error loading command ${file}:`, error.message);
        }
      }
    }
  } catch (error) {
    console.error(`❌ Error loading commands from ${dir}:`, error.message);
  }
}

const commandsPath = path.join(__dirname, 'commands');
if (fs.existsSync(commandsPath)) {
  loadCommands(commandsPath);
  console.log(`✅ Loaded ${client.commands.size} commands total`);
} else {
  console.error('❌ Commands directory not found!');
  process.exit(1);
}

// Load events
const eventsPath = path.join(__dirname, 'events');
if (fs.existsSync(eventsPath)) {
  const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));
  console.log(`📄 Found ${eventFiles.length} event files`);
  
  for (const file of eventFiles) {
    try {
      const filePath = path.join(eventsPath, file);
      console.log(`📄 Loading event: ${file}`);
      const event = require(filePath);
      
      if (event.once) {
        client.once(event.name, (...args) => event.execute(...args));
      } else {
        client.on(event.name, (...args) => event.execute(...args));
      }
      console.log(`✅ Loaded event: ${event.name}`);
    } catch (error) {
      console.error(`❌ Error loading event ${file}:`, error.message);
    }
  }
} else {
  console.error('❌ Events directory not found!');
  process.exit(1);
}

// Handle interaction events
client.on('interactionCreate', async interaction => {
  if (!interaction.isChatInputCommand()) return;

  const command = interaction.client.commands.get(interaction.commandName);

  if (!command) {
    console.error(`No command matching ${interaction.commandName} was found.`);
    return;
  }

  try {
    await command.execute(interaction);
  } catch (error) {
    console.error(error);
    if (interaction.replied || interaction.deferred) {
      await interaction.followUp({ content: 'There was an error while executing this command!', ephemeral: true });
    } else {
      await interaction.reply({ content: 'There was an error while executing this command!', ephemeral: true });
    }
  }
});

// Add error handlers
process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
});

process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

// Login to Discord with your client's token
console.log('🔐 Attempting to login to Discord...');
client.login(process.env.DISCORD_TOKEN).catch(error => {
  console.error('❌ Failed to login:', error.message);
  process.exit(1);
}); 