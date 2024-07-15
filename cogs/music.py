import asyncio
import os
import datetime
import urllib.parse, urllib.request
import re
import logging
import random
import discord
import spotipy
import yt_dlp
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials
from discord.ext import commands


class MusicCog(commands.Cog):
    """
    Commands that handle music playing in voice channel.
    """
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }
        self.yt_dl_options = {"format": "bestaudio/best"}
        self.ytdl = yt_dlp.YoutubeDL(self.yt_dl_options)
        self.youtube_base_url = 'https://www.youtube.com/'
        self.youtube_results_url = self.youtube_base_url + 'results?'
        self.youtube_watch_url = self.youtube_base_url + 'watch?v='
        load_dotenv()

    @commands.Cog.listener()
    async def on_ready(self):
        '''Print statment to ensure loads properly.'''
        logging.info('Music Cog loaded.')

    async def play_next(self, ctx):
        """
        Continues player if queue exists.
        """
        logging.info('play_next')
        if ctx.guild.id in self.queues and len(self.queue[ctx.guild.id]) > 0:
            url = self.queues[ctx.guild.id].pop(0)
            await self.play(ctx, url=url)
        else:
            await self.stop(ctx)

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

        if ctx.guild.id not in self.voice_clients:
            try:
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[ctx.guild.id] = voice_client
            except Exception as e:
                logging.error('%s', str(e))

        # note_emoji = '\U0001F3B5'
        try:
            if self.youtube_base_url not in url:
                query_string = urllib.parse.urlencode({
                    'search_query': url
                })

                content = urllib.request.urlopen(
                    self.youtube_results_url + query_string
                )

                search_results = re.findall(r'/watch\?v=(.{11})', content.read().decode())

                url = self.youtube_watch_url + search_results[0]
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(url, download=False))

            song = data['url']
            player = discord.FFmpegOpusAudio(song, **self.ffmpeg_options)

            self.voice_clients[ctx.guild.id].play(player, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop))
        except Exception as e:
            logging.error('%s', str(e))

    @commands.command()
    async def skip(self, ctx):
        """
        Stops current song playing and plays next song in queue.
        """
        logging.info('Skip command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.play_next(ctx)
            await ctx.send('Skipped current track.')
        except Exception as e:
            logging.error('%s', str(e))

    @commands.command()
    async def queue(self, ctx, *, url):
        """
        Add song to music queue.
        """
        if ctx.guild.id not in self.queues:
            self.queues[ctx.guild.id] = []
        self.queues[ctx.guild.id].append(url)
        await ctx.send('Song has been added to the queue.')

    @commands.command()
    async def clear_queue(self, ctx):
        """
        Clears music queue.
        """
        if ctx.guild.id in self.queues:
            self.queues[ctx.guild.id].clear()
        else:
            await ctx.send('There is no queue to clear.')

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
            if ctx.guild.id in self.queues:
                del self.queues[ctx.guild.id]
        except Exception as e:
            logging.error('Failed to stop playback: %s', str(e))

    # Helper functions
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
