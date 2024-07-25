import os
import datetime
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
        self.url_queue = []
        self.FFMPEG_OPTIONS = {'options': '-vn'}
        self.YDL_OPTIONS = {
            'format': 'bestaudio', 
            'noplaylist' : True,
            'default_search': 'ytsearch',
        }
        self.ytdl = yt_dlp.YoutubeDL(self.YDL_OPTIONS)
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
        if self.url_queue:
            # Retrieve queue info and play
            song = self.url_queue.pop(0)
            source = await discord.FFmpegOpusAudio.from_probe(song['url'], **self.FFMPEG_OPTIONS)
            
            # Format duration seconds to MM:SS
            td = datetime.timedelta(seconds=song['duration'])
            minutes, seconds = divmod(td.seconds, 60)
            duration = f'{minutes}:{seconds:02d}'

            # Create and send embed
            embed = discord.Embed(title='Now Playing', timestamp=datetime.datetime.now())
            embed.set_thumbnail(url=song['thumbnail'])
            embed.add_field(name=f'**{song["title"]}** `({duration})`', value=f'*requested by {song["requester"]}*', inline=False)
            embed.set_footer(text=f'Queue: {len(self.url_queue)}', icon_url=ctx.guild.icon.url)
            await ctx.send(embed=embed)

            # Play url
            ctx.voice_client.play(source, after=lambda _:self.bot.loop.create_task(self.play_next(ctx)))
        elif not ctx.voice_client.is_playing():
            await ctx.send('Queue is empty.')

    @commands.command()
    async def play(self, ctx, *, url):
        """
        Plays the user submitted search terms in audio chat.
        """
        logging.info('Play command submitted by [%s:%s]', ctx.author.name, ctx.author.id)

        voice_channel = ctx.author.voice.channel if ctx.author.voice else None
        if not voice_channel:
            return await ctx.send('Join a voice channel to use this command.')
        if not ctx.voice_client:
            await voice_channel.connect()
        
        async with ctx.typing():
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                if self.is_spotify_url(url):
                    url = self.get_search_terms(url)
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    info = info['entries'][0]

                # Extract song info from video: [url, title, thumbnail, duration, requester]
                song = {
                    'url': info['url'],
                    'title': info['title'],
                    'thumbnail': None,
                    'duration': info['duration'],
                    'requester': ctx.author.name,
                }

                # Extract thumbnail url in .jpg format
                for thumbnail in info['thumbnails']:
                    if thumbnail['url'].endswith('.jpg'):
                        song['thumbnail'] = thumbnail['url']

                self.url_queue.append(song)
                await ctx.send(f'Added to queue: **{song["title"]}**')
        if not ctx.voice_client.is_playing():
            await self.play_next(ctx)

    @commands.command()
    async def skip(self, ctx):
        """
        Stops current song playing and plays next song in queue.
        """
        logging.info('Skip command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send(f'Song skipped by *{ctx.author.name}*.')

    @commands.command()
    async def queue(self, ctx):
        """
        Add song to music queue.
        """
        logging.info('Queue command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        if self.url_queue:
            embed = discord.Embed(title=f'{ctx.guild} - Queue: {len(self.url_queue)}', timestamp=datetime.datetime.now())
            for i, tup in enumerate(self.url_queue):
                embed.add_field(name=f'{i + 1}. **{tup[1]}** - requested by *{tup[2]}*', value='', inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send('The queue is empty.')

    @commands.command()
    async def clear_queue(self, ctx):
        """
        Clears music queue.
        """
        if self.url_queue:
            self.url_queue.clear()
        else:
            await ctx.send('There is no queue to clear.')

    @commands.command()
    async def shuffle(self, ctx):
        """
        Randomize order of urls in queue.
        """
        logging.info('Shuffle command submitted by [%s:%s]', ctx.author.name, ctx.author.id)

        if len(self.url_queue) > 1:
            random.shuffle(self.url_queue)
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
            ctx.voice_client.pause()
        except Exception as e:
            logging.error('Failed to pause: %s', str(e))

    @commands.command()
    async def resume(self, ctx):
        """
        Resumes audio playback in voice channel.
        """
        logging.info('Resume command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        try:
            ctx.voice_client.resume()
        except Exception as e:
            logging.error('Failed to resume playback: %s', str(e))

    @commands.command()
    async def stop(self, ctx):
        """
        Stops bot playback in voice channel and cleans up guild dict entries.
        """
        try:
            ctx.voice_client.stop()
            await ctx.voice_client.disconnect()
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
