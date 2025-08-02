const { 
  joinVoiceChannel, 
  createAudioPlayer, 
  createAudioResource, 
  AudioPlayerStatus,
  VoiceConnectionStatus,
  entersState,
  getVoiceConnection
} = require('@discordjs/voice');
const play = require('play-dl');
const { EmbedBuilder } = require('discord.js');

class MusicManager {
  constructor() {
    this.queues = new Map();
    this.players = new Map();
  }

  // Get or create queue for a guild
  getQueue(guildId) {
    if (!this.queues.has(guildId)) {
      this.queues.set(guildId, []);
    }
    return this.queues.get(guildId);
  }

  // Get or create player for a guild
  getPlayer(guildId) {
    if (!this.players.has(guildId)) {
      const player = createAudioPlayer();
      this.players.set(guildId, player);
      
      // Handle player state changes
      player.on(AudioPlayerStatus.Idle, () => {
        this.playNext(guildId);
      });

      player.on('error', error => {
        console.error('Audio player error:', error);
      });
    }
    return this.players.get(guildId);
  }

  // Join voice channel
  async joinVoiceChannel(interaction) {
    const member = interaction.member;
    const voiceChannel = member.voice.channel;

    if (!voiceChannel) {
      throw new Error('You need to be in a voice channel to use this command!');
    }

    const connection = joinVoiceChannel({
      channelId: voiceChannel.id,
      guildId: voiceChannel.guild.id,
      adapterCreator: voiceChannel.guild.voiceAdapterCreator,
      selfDeaf: false,
    });

    // Wait for the connection to be ready
    await entersState(connection, VoiceConnectionStatus.Ready, 30_000);

    return connection;
  }

  // Search for a song
  async searchSong(query) {
    try {
      // Try to search on YouTube
      const ytInfo = await play.search(query, { limit: 1 });
      if (ytInfo && ytInfo.length > 0) {
        return {
          title: ytInfo[0].title,
          url: ytInfo[0].url,
          duration: ytInfo[0].durationInSec,
          thumbnail: ytInfo[0].thumbnails[0].url,
          type: 'youtube'
        };
      }
      throw new Error('No results found');
    } catch (error) {
      throw new Error(`Failed to search for song: ${error.message}`);
    }
  }

  // Add song to queue
  async addToQueue(guildId, song) {
    const queue = this.getQueue(guildId);
    queue.push(song);
    return queue.length;
  }

  // Play next song in queue
  async playNext(guildId) {
    const queue = this.getQueue(guildId);
    const player = this.getPlayer(guildId);
    const connection = getVoiceConnection(guildId);

    if (!connection) return;

    if (queue.length === 0) {
      // No more songs, disconnect after a delay
      setTimeout(() => {
        if (queue.length === 0) {
          connection.destroy();
        }
      }, 300000); // 5 minutes
      return;
    }

    const song = queue.shift();
    
    try {
      let stream;
      if (song.type === 'youtube') {
        stream = await play.stream(song.url);
      } else {
        stream = await play.stream(song.url);
      }

      const resource = createAudioResource(stream.stream, {
        inputType: stream.type,
        inlineVolume: true,
      });

      resource.volume.setVolume(0.5);
      player.play(resource);
    } catch (error) {
      console.error('Error playing song:', error);
      // Try to play next song
      this.playNext(guildId);
    }
  }

  // Start playing music
  async play(guildId, interaction) {
    const connection = await this.joinVoiceChannel(interaction);
    const player = this.getPlayer(guildId);
    
    connection.subscribe(player);
    
    // Start playing if there are songs in queue
    const queue = this.getQueue(guildId);
    if (queue.length > 0) {
      this.playNext(guildId);
    }
  }

  // Skip current song
  skip(guildId) {
    const player = this.getPlayer(guildId);
    player.stop();
  }

  // Stop playing and clear queue
  stop(guildId) {
    const player = this.getPlayer(guildId);
    const queue = this.getQueue(guildId);
    const connection = getVoiceConnection(guildId);

    player.stop();
    queue.length = 0;
    
    if (connection) {
      connection.destroy();
    }
  }

  // Get current queue
  getQueueInfo(guildId) {
    return this.getQueue(guildId);
  }

  // Format duration from seconds to MM:SS
  formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  // Create embed for song info
  createSongEmbed(song, action = 'Added to queue') {
    const embed = new EmbedBuilder()
      .setColor('#0099ff')
      .setTitle(action)
      .setDescription(`**${song.title}**`)
      .setThumbnail(song.thumbnail)
      .addFields(
        { name: 'Duration', value: this.formatDuration(song.duration), inline: true },
        { name: 'URL', value: `[Click here](${song.url})`, inline: true }
      )
      .setTimestamp();

    return embed;
  }
}

module.exports = new MusicManager(); 