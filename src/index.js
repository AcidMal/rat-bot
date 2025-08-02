const { Client, GatewayIntentBits, Collection } = require('discord.js');
const { joinVoiceChannel } = require('@discordjs/voice');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

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
  const commandFiles = fs.readdirSync(dir);
  
  for (const file of commandFiles) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat.isDirectory()) {
      // Recursively load commands from subdirectories
      loadCommands(filePath);
    } else if (file.endsWith('.js')) {
      const command = require(filePath);
      
      // Set a new item in the Collection with the key as the command name and the value as the exported module
      if ('data' in command && 'execute' in command) {
        client.commands.set(command.data.name, command);
      } else {
        console.log(`[WARNING] The command at ${filePath} is missing a required "data" or "execute" property.`);
      }
    }
  }
}

const commandsPath = path.join(__dirname, 'commands');
loadCommands(commandsPath);

// Load events
const eventsPath = path.join(__dirname, 'events');
const eventFiles = fs.readdirSync(eventsPath).filter(file => file.endsWith('.js'));

for (const file of eventFiles) {
  const filePath = path.join(eventsPath, file);
  const event = require(filePath);
  
  if (event.once) {
    client.once(event.name, (...args) => event.execute(...args));
  } else {
    client.on(event.name, (...args) => event.execute(...args));
  }
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

// Login to Discord with your client's token
client.login(process.env.DISCORD_TOKEN); 