import asyncio
import os
import datetime
import logging
import random
import discord
import spotipy
from pytube import YouTube
from pytube import Search
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands


class MusicCog(commands.Cog):
    """
    Commands that handle music playing in voice channel.
    """
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        # self.queue_info = {}
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }
        load_dotenv()

    @commands.Cog.listener()
    async def on_ready(self):
        '''Print statment to ensure loads properly.'''
        logging.info('Music Cog loaded.')

    # @commands.command()
    # async def queue(self, ctx):
    #     """
    #     Displays the music queue.
    #     """
    #     logging.info('Queue command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
    #     if ctx.guild.id in self.queues:
    #         if len(self.queues[ctx.guild.id]) == 0:
    #             await ctx.send('The queue is empty.')
    #         else:
    #             note_emoji = '\U0001F3B5'
    #             embed = discord.Embed(title=f'{note_emoji}  **Current Queue | {len(self.queues[ctx.guild.id])} entries**', timestamp=datetime.datetime.now())
    #             message = ''

    #             for index, title in enumerate(self.queue_info[ctx.guild.id]):
    #                 message += f'`{index + 1}` | **{title}**\n'

    #             embed.add_field(name='', value=message, inline=False)
    #             await ctx.send(embed=embed)
    #     else:
    #         await ctx.send('There is no queue.')

    @commands.command()
    async def play(self, ctx, *, url):
        """
        Plays the user submitted search terms in audio chat.
        """
        logging.info('Play command submitted by [%s:%s]', ctx.author.name, ctx.author.id)

        if ctx.author.voice is None:
            await ctx.send('You must be in a voice channel to run this command.')
            logging.info('Play command failed: [%s] is not in voice channel.', ctx.author.name)
            return

        # note_emoji = '\U0001F3B5'
        try:
            # Check if voice client exists for guild
            if ctx.guild.id in self.voice_clients:
                # Initialize queue list if doesn't exist for the guild
                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = []
                self.queues[ctx.guild.id].append(url)

                # Initialize queue_info list if doesn't exist for the guild
                # if ctx.guild.id not in self.queue_info:
                #     self.queue_info[ctx.guild.id] = []
                # self.queue_info[ctx.guild.id].append(self.get_queue_info(url))
            else:
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[voice_client.guild.id] = voice_client

                # Initialize queue list if doesn't exist for the guild
                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = []
                self.queues[ctx.guild.id].append(url)

                # Initialize queue_info list if doesn't exist for the guild
                # if ctx.guild.id not in self.queue_info:
                #     self.queue_info[ctx.guild.id] = []
                # self.queue_info[ctx.guild.id].append(self.get_queue_info(url))

                while len(self.queues[ctx.guild.id]) > 0:
                    url = self.queues[ctx.guild.id].pop(0)
                    song = self.get_stream_url(url=url)
                    player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)
                    self.voice_clients[ctx.guild.id].play(player)

                    while self.voice_clients[ctx.guild.id].is_playing():
                        await asyncio.sleep(1)
        except Exception as e:
            logging.error('Failed to play song: %s',str(e))

    @commands.command()
    async def skip(self, ctx):
        """
        Stops current song playing and plays next song in queue.
        """
        logging.info('Skip command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        # note_emoji = '\U0001F3B5'
        cowboy_emoji = '\U0001F920'

        if self.voice_clients[ctx.guild.id] and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].stop()
            # skipped_song = self.queue_info[ctx.guild.id].pop(0)
            # await ctx.reply(f'{cowboy_emoji} Skipped **{skipped_song}**')

            if len(self.queues[ctx.guild.id]) > 0:
                url = self.queues[ctx.guild.id].pop(0)
                song = self.get_stream_url(url)
                player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)
                self.voice_clients[ctx.guild.id].play(player)
            else:
                await self.stop(ctx)
        else:
            await ctx.send('There is no song currently playing.')

    @commands.command()
    async def shuffle(self, ctx):
        """
        Randomize order of urls in queue.
        """
        logging.info('Shuffle command submitted by [%s:%s]', ctx.author.name, ctx.author.id)

        if len(self.queues[ctx.guild.id]) > 1:
            random.shuffle(self.queues[ctx.guild.id])
        else:
            await ctx.send('There must be at least two songs in queue to shuffle.')

    @commands.command()
    async def move(self, ctx, index1, index2):
        """
        Modifies queue order by moving a song to a target index in the queue.
        """
        logging.info('Move command submitted by [%s:%s]', ctx.author.name, ctx.author.id)

        index1 -= 1
        index2 -= 1

        # TODO: implement reordering of queue

    @commands.command()
    async def pause(self, ctx):
        """
        Stops audio playback in voice channel. Can be resumed.
        """
        logging.info('Pause command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        try:
            self.voice_clients[ctx.guild.id].pause()
        except Exception as e:
            logging.error('Failed to pause: %s', str(e))

    @commands.command()
    async def resume(self, ctx):
        """
        Resumes audio playback in voice channel.
        """
        logging.info('Resume command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        try:
            self.voice_clients[ctx.guild.id].resume()
        except Exception as e:
            logging.error('Failed to resume playback: %s', str(e))

    @commands.command()
    async def stop(self, ctx):
        """
        Stops bot playback in voice channel and cleans up guild dict entries.
        """
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
            del self.queues[ctx.guild.id]
            # del self.queue_info[ctx.guild.id]
        except Exception as e:
            logging.error('Failed to stop playback: %s', str(e))

    # Helper functions
    def get_queue_info(self, url: str) -> str:
        """
        Extracts song duration and title from url.
        """
        if self.is_yt_url(user_input=url):
            return YouTube(url).streams.filter(only_audio=True).first().title
        elif self.is_spotify_url(user_input=url):
            search_terms = self.get_search_terms(url)
            return Search(search_terms).results[0].streams.filter(only_audio=True).first().title
        else:
            return Search(url).results[0].streams.filter(only_audio=True).first().title

    def get_stream_url(self, url: str) -> str:
        """
        Extracts stream url from YouTube link, search terms, or Spotify link.
        """
        if self.is_yt_url(user_input=url):
            return YouTube(url).streams.filter(only_audio=True).first().url
        elif self.is_spotify_url(user_input=url):
            search_terms = self.get_search_terms(url)
            return Search(search_terms).results[0].streams.filter(only_audio=True).first().url
        else:
            return Search(url).results[0].streams.filter(only_audio=True).first().url

    def is_yt_url(self, user_input: str) -> bool:
        """
        Checks if input string is a YouTube url.
        """
        if 'https://www.youtube.com/' in user_input:
            return True
        return False

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
    await bot.add_cog(MusicCog(bot))
