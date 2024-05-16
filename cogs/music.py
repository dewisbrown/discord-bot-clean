import asyncio, datetime, logging, random
import discord, yt_dlp
from discord.ext import commands


class MusicCog(commands.Cog):
    """
    Commands that handle music playing in voice channel.
    """
    def __init__(self, bot):
        yt_dl_options = {'format': 'bestaudio/best'}
        self.bot = bot
        self.queues = {}
        self.voice_clients = {}
        self.ytdl = yt_dlp.YoutubeDL(yt_dl_options)
        self.ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -filter:a "volume=0.25"'
        }

    @commands.Cog.listener()
    async def on_ready(self):
        '''Print statment to ensure loads properly.'''
        logging.info('Music Cog loaded.')

    @commands.command()
    async def queue(self, ctx):
        """
        Displays the music queue.
        """
        logging.info('Queue command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        if len(self.queues[ctx.guild.id]) == 0:
            await ctx.send('The queue is empty.')
        # else:
        #     note_emoji = '\U0001F3B5'
        #     embed = discord.Embed(title=f'{note_emoji}  **Current Queue | {len(self.queues[ctx.guild.id])} entries**', timestamp=datetime.datetime.now())
        #     message = ''
        #
        #     for index, item in enumerate(queue):
        #         message += f'`{index + 1}` | (`{item["song_duration"]}`) **{item["song_name"]} -** {item["request_author"]}\n'
        #
        #     embed.add_field(name='', value=message, inline=False)
        #     await ctx.send(embed=embed)

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

        note_emoji = '\U0001F3B5'
        try:
            # Check if voice client has been created for guild
            if ctx.guild.id in self.voice_clients:
                # Add to queue
                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = []
                self.queues[ctx.guild.id].append(url)
            else:
                voice_client = await ctx.author.voice.channel.connect()
                self.voice_clients[voice_client.guild.id] = voice_client

                if ctx.guild.id not in self.queues:
                    self.queues[ctx.guild.id] = []
                self.queues[ctx.guild.id].append(url)
                while len(self.queues[ctx.guild.id]) > 0:
                    loop = asyncio.get_event_loop()
                    data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(self.queues[ctx.guild.id].pop(0), download=False))

                    song = data['url']
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
        note_emoji = '\U0001F3B5'
        cowboy_emoji = '\U0001F920'

        if self.voice_clients[ctx.guild.id] and self.voice_clients[ctx.guild.id].is_playing():
            self.voice_clients[ctx.guild.id].stop()
            await ctx.reply(f'{cowboy_emoji} Skipped **skipped_song.name** - [`skipped_song.duration`]`')

            if len(self.queues[ctx.guild.id]) > 0:
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(self.queues[ctx.guild.id].pop(0), download=False))
                song = data['url']

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
            logging.error(msg=e)

    @commands.command()
    async def resume(self, ctx):
        """
        Resumes audio playback in voice channel.
        """
        logging.info('Resume command submitted by [%s:%s]', ctx.author.name, ctx.author.id)
        try:
            self.voice_clients[ctx.guild.id].resume()
        except Exception as e:
            logging.error(msg=e)

    @commands.command()
    async def stop(self, ctx):
        """
        Stops bot playback in voice channel.
        """
        try:
            self.voice_clients[ctx.guild.id].stop()
            await self.voice_clients[ctx.guild.id].disconnect()
            del self.voice_clients[ctx.guild.id]
        except Exception as e:
            logging.error('Failed to stop: %s', str(e))


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
