import discord
from discord.ext import commands
import yt_dlp
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

song_queue = []
song_history = []

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

def play_next(ctx):
    if len(song_queue) > 0:
        next_song = song_queue.pop(0)
        song_history.append(next_song)
        
        source = discord.FFmpegOpusAudio.from_probe(next_song['url'], **ffmpeg_options)
        ctx.voice_client.pley(source, after=lambda e: play_next(ctx))
        
        bot.loop.create_task(ctx.send(f" Now playing: **{next_song['title']}**"))
    else:
        bot.loop.create_task(ctx.send("Que empty!! Add more with /play"))
        

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}  (ID: {bot.user.id})')
    print('----------')

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first!")

    voice_client = ctx.guild.voice_client
    if not voice_client:
        await ctx.author.voice.channel.connect()
        voice_client = ctx.guild.voice_client

    async with ctx.typing():
        info = ytdl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        data = {'url': info['url'], 'title': info['title']}
        
        if voice_client.is_playing():
            song_queue.append(data)
            await ctx.send(f"Added to queue: **{info['title']}**")
        else: 
            song_history.append(data)
            source = await discord.FFmpegOpusAudio.from_probe(data['url'],**ffmpeg_options)
            voice_client.play(source, after=lambda e: play_next(ctx))
            await ctx.send(f"Now playing: **{info['title']}**")
            

@bot.command(name='skip')
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped!!!!!")
        
        
@bot.command(name='previous')
async def previous(ctx):
    if len(song_history) < 2:
        return await ctx.send("No previous songs to play!")
    
    current = song_history.pop()
    prev = song_history.pop()
    
    song_queue.insert(0, current)
    song_queue.insert(0, prev)
    
    ctx.voice_client.stop()
    await ctx.send(f"Going back to: **{prev['title']}**")
    

@bot.command(name='queue')
async def show_queue(ctx):
    if not song_queue:
        return await ctx.send("The queue is currently empty.")
    
    msg = "**upcoming Songs:**\n"
    for i, song in enumerate(song_queue, 1):
        msg += f"{i}. {song['title']}\n"
    await ctx.send(msg)

@bot.command(name='leave')
async def leave(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        song_queue.clear()
        song_history.clear()
        await ctx.send("Bye!")

bot.run(TOKEN)