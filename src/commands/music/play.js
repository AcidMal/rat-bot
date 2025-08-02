const { SlashCommandBuilder, EmbedBuilder } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, AudioPlayerStatus } = require('@discordjs/voice');
const play = require('play-dl');

module.exports = {
  data: new SlashCommandBuilder()
    .setName('play')
    .setDescription('Play a song from YouTube')
    .addStringOption(option =>
      option.setName('query')
        .setDescription('The song to search for or YouTube URL')
        .setRequired(true)),
  async execute(interaction) {
    try {
      const query = interaction.options.getString('query');
      const member = interaction.member;

      // Check if user is in a voice channel
      if (!member.voice.channel) {
        return await interaction.reply({
          content: '❌ You need to be in a voice channel to use this command!',
          ephemeral: true
        });
      }

      await interaction.deferReply();

      // Join the voice channel
      const connection = joinVoiceChannel({
        channelId: member.voice.channel.id,
        guildId: interaction.guild.id,
        adapterCreator: interaction.guild.voiceAdapterCreator,
      });

      // Search for the song
      let songInfo;
      if (play.yt_validate(query) === 'video') {
        songInfo = await play.video_info(query);
      } else {
        const searchResults = await play.search(query, { limit: 1 });
        if (searchResults.length === 0) {
          return await interaction.editReply({
            content: '❌ No songs found for that query!',
            ephemeral: true
          });
        }
        songInfo = await play.video_info(searchResults[0].url);
      }

      const stream = await play.stream(songInfo.video_details.url);
      const resource = createAudioResource(stream.stream, {
        inputType: stream.type
      });

      const player = createAudioPlayer();
      connection.subscribe(player);
      player.play(resource);

      const embed = new EmbedBuilder()
        .setColor(0x00ff00)
        .setTitle('🎵 Now Playing')
        .setDescription(`**${songInfo.video_details.title}**`)
        .setThumbnail(songInfo.video_details.thumbnails[0].url)
        .addFields(
          { name: 'Duration', value: formatDuration(songInfo.video_details.durationInSec), inline: true },
          { name: 'Channel', value: songInfo.video_details.channel.name, inline: true },
          { name: 'URL', value: `[Click here](${songInfo.video_details.url})`, inline: true }
        )
        .setTimestamp();

      await interaction.editReply({ embeds: [embed] });

      // Handle when the song ends
      player.on(AudioPlayerStatus.Idle, () => {
        connection.destroy();
      });

    } catch (error) {
      console.error('Play command error:', error);
      await interaction.editReply({
        content: `❌ Error: ${error.message}`,
        ephemeral: true
      });
    }
  },
};

function formatDuration(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
} 