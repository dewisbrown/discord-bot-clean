import os
import logging
import asyncio

import discord
import spotipy
import yt_dlp
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from collections import deque
from discord.ext import commands


class MusicCog(commands.Cog):
    """
    Commands that handle music playing in voice channel.
    """
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.SONG_QUEUES = {}
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -c:a libopus -b:a 96k',
            }
        self.YDL_OPTIONS = {
            'format': 'bestaudio[abr<=96]/bestaudio', 
            'noplaylist' : True,
            'youtube_include_dash_manifest': False,
            'youtube_include_hls_manifest': False,
            'default_search': 'ytsearch1',
        }
        load_dotenv()

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Print statment to ensure loads properly.
        """
        logging.info('Music Cog loaded.')

    async def search_ytdlp_async(self, query, ydl_opts):
        """
        Routine to search for YouTube stream.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: self._extract(query, ydl_opts))

    def _extract(self, query, ydl_opts):
        """
        Extracts YouTube info from search query.
        """
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(query, download=False)

    @commands.command(name='play')
    async def play(self, ctx: commands.Context, *, query: str):
        """
        Uses user input to query YouTube for audio stream, then plays
        audio stream in a discord voice channel.
        """
        try:
            voice_channel: discord.VoiceChannel = ctx.author.voice.channel

            if voice_channel is None:
                await ctx.send('You must be in a voice channel to use this command.')
                return

            voice_client: discord.VoiceClient = ctx.guild.voice_client

            # Join current voice channel if bot is not connected
            if voice_client is None:
                voice_client = await voice_channel.connect()
            # Move bot to user's voice channel if in another channel
            elif voice_channel != voice_client.channel:
                await voice_client.move_to(voice_channel)

            if self.is_spotify_url(query):
                query = self.get_search_terms(query)

            results = await self.search_ytdlp_async(query, self.YDL_OPTIONS)
            tracks = results.get('entries', [])

            # Check if tracks is empty
            if not tracks:
                await ctx.send('No results found for your query.')
                return

            first_track = tracks[0]
            audio_url = first_track['url']
            title = first_track.get('title', 'untitled')

            guild_id = str(ctx.guild.id)
            if self.SONG_QUEUES.get(guild_id) is None:
                self.SONG_QUEUES[guild_id] = deque()

            # Add the song to the queue with the requester's name
            self.SONG_QUEUES[guild_id].append((audio_url, title, ctx.author.display_name))

            if voice_client.is_playing() or voice_client.is_paused():
                await ctx.send(f'Added to queue: **{title}** - *Requested by* {ctx.author.display_name}')
            else:
                await self.play_next_song(voice_client, guild_id, ctx)
        except Exception as e:
            logging.error(f"Error in play command: {e}")
            await ctx.send('An error occurred while trying to play the song.')

    @commands.command(name='skip')
    async def skip(self, ctx: commands.Context):
        """
        Skips the currently playing song.
        """
        voice_client: discord.VoiceClient = ctx.guild.voice_client

        if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
            voice_client.stop()
            await ctx.send('Skipped the current song.')
        else:
            await ctx.send('Not playing anything to skip.')

    @commands.command(name='pause')
    async def pause(self, ctx: commands.Context):
        """
        Pauses the currently playing song.
        """
        voice_client: discord.VoiceClient = ctx.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            await ctx.send('Not in a voice channel.')
            return

        # Check if something is playing
        if not voice_client.is_playing():
            await ctx.send('Nothing is playing.')
            return

        voice_client.pause()
        await ctx.send('Playback has been paused.')

    @commands.command(name='resume')
    async def resume(self, ctx: commands.Context):
        """
        Resumes playback if paused.
        """
        voice_client: discord.VoiceClient = ctx.guild.voice_client

        # Check if the bot is in a voice channel
        if voice_client is None:
            await ctx.send('Bot is not in a voice channel.')
            return

        # Check if it's actually paused
        if not voice_client.is_paused():
            await ctx.send('There is nothing paused at this moment.')
            return

        # Resume playback
        voice_client.resume()
        await ctx.send('Playback resumed.')

    @commands.command(name='stop')
    async def stop(self, ctx: commands.Context):
        """
        Stops playback and clears the queue.
        """
        voice_client: discord.VoiceClient = ctx.guild.voice_client

        # Check if the bot is in a voice channel
        if not voice_client or not voice_client.is_connected():
            await ctx.send('Bot is not connected to a voice channel.')
            return

        # Clear the guild's queue
        guild_id_str = str(ctx.guild.id)
        if guild_id_str in self.SONG_QUEUES:
            self.SONG_QUEUES[guild_id_str].clear()

        # If something is playing or paused, stop it
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()

        # (Optional) Disconnect from the channel
        await voice_client.disconnect()

        await ctx.send('Playback has been stopped. Bye!')

    @commands.command(name='play_next_song')
    async def play_next_song(self, voice_client: discord.VoiceClient, guild_id, ctx: commands.Context, send_message: bool = True):
        """
        Plays the next song in the queue. Optionally sends a message when a song starts playing.
        """
        if self.SONG_QUEUES[guild_id]:
            # Unpack all three elements from the deque
            audio_url, title, requester = self.SONG_QUEUES[guild_id].popleft()

            source = discord.FFmpegOpusAudio(audio_url, **self.FFMPEG_OPTIONS)

            def after_play(error):
                if error:
                    print(f"Error playing {title}: {error}")
                asyncio.run_coroutine_threadsafe(
                    self.play_next_song(voice_client, guild_id, ctx, send_message=True), self.bot.loop
                )

            voice_client.play(source, after=after_play)

            # Only send the "Now playing" message if send_message is True
            if send_message:
                await ctx.send(f'Now playing: **{title}** - *Requested by* {requester}')
        else:
            await voice_client.disconnect()
            self.SONG_QUEUES[guild_id] = deque()

    @commands.command(name='queue')
    async def queue(self, ctx: commands.Context):
        """
        Displays the list of songs in the queue with their titles and requesters.
        """
        guild_id = str(ctx.guild.id)

        # Check if the queue exists and is not empty
        if guild_id not in self.SONG_QUEUES or not self.SONG_QUEUES[guild_id]:
            await ctx.send('The queue is currently empty.')
            return

        # Build the queue message
        queue_list = self.SONG_QUEUES[guild_id]
        queue_message = "**Current Queue:**\n"
        for index, (audio_url, title, requester) in enumerate(queue_list, start=1):
            queue_message += f"{index}. {title} - *Requested by* {requester}\n"

        await ctx.send(queue_message)

    def is_spotify_url(self, user_input: str) -> bool:
        """
        Checks if input string is a spotify url.
        """
        if 'open.spotify.com/track/' in user_input:
            return True
        return False

    def get_search_terms(self, url: str) -> str:
        """
        Extracts artist and song name from spotify url.
        """
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(auth_manager=auth_manager)

        track = sp.track(url)
        logging.info('Converting spotify url %s to [%s %s]', url, track['name'], track['artists'][0]['name'])
        return f"{track['name']} {track['artists'][0]['name']}"

async def setup(bot):
    """
    Adds music cog to bot.
    """
    await bot.add_cog(MusicCog(bot))
