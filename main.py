import os
import discord
import yt_dlp
import asyncio
import time
from discord.ext import commands
from flask import Flask
from threading import Thread
from youtubesearchpython import VideosSearch
from dotenv import load_dotenv

from Enhancements_slider import EnhancementSliderView
from bot_ui import setup_booth, update_control_panel

load_dotenv()

app = Flask('')
@app.route('/')

def home():
    return "Bot is online and healthy!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()


TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix=".", intents=intents)

# -- Config --
song_queue = []
song_history = []
current_song_data = None      
current_song_start_time = 0   
is_swapping = False
disconnect_timer = None
control_message = None

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'source_address': '0.0.0.0',
    'extract_flat': False,
    'extractor_args': {'youtube': {'player_client': ['web', 'ios', 'android']}},
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

ffmpeg_params = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 192k',
}

# -- Helpers -- 
async def silent_disconnect(ctx):
    await asyncio.sleep(120) # 2 minutes
    if ctx.voice_client and not ctx.voice_client.is_playing():
        await ctx.voice_client.disconnect()

async def start_playing_task(ctx, next_song):
    try:
        info = ytdl.extract_info(next_song['url'], download=False)
        stream_url = info['url']
        
        source = await discord.FFmpegOpusAudio.from_probe(stream_url, **ffmpeg_params)
        ctx.voice_client.play(source, after=lambda e: play_next(ctx, e))
        
        view = EnhancementSliderView(
            ctx, ffmpeg_params, song_queue, apply_live_filter, 
            next_song, time.time()
        )
        control_message = await ctx.send(embed=view.get_embed(), view=view)
        
    except Exception as e:
        print(f"Playback error: {e}")
        await ctx.send("❌ Error starting stream. Skipping...")
        play_next(ctx)
        
async def update_dashboard(self, interaction):
    await self.control_message.edit(embed=self.get_embed(), view=self)

async def apply_live_filter(ctx):
    global current_song_start_time, current_song_data, is_swapping
    if not ctx.voice_client or not current_song_data: 
        return
    elapsed = time.time() - current_song_start_time
    is_swapping = True
    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        ctx.voice_client.stop()
        await asyncio.sleep(0.2)
    live_params = ffmpeg_params.copy()
    live_params['before_options'] = f"-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -ss {elapsed}"
    source = await discord.FFmpegOpusAudio.from_probe(current_song_data['url'], **live_params)
    ctx.voice_client.play(source, after=lambda e: play_next(ctx, e))
    current_song_start_time = time.time() - elapsed

def play_next(ctx, error=None): 
    global current_song_data, current_song_start_time, is_swapping, disconnect_timer
    if error: 
        print(f"Player error: {error}")
        
    if is_swapping:
        is_swapping = False
        return
    
    if disconnect_timer:
        disconnect_timer.cancel()
        disconnect_timer = None

    next_song = None
    if len(song_queue) > 0:
        next_song = song_queue.pop(0)
    elif current_song_data:
        try:
            search = VideosSearch(f"related to {current_song_data['title']}", limit=1)
            result = search.result()['result']
            
            for res in results:
                if res['link'] != current_song_data['url']:
                    next_song = {'url': result['link'], 'title': result['title'], 'duration': 300}
                    break
        except: 
            next_song = None
    
    if next_song:
        current_song_data = next_song
        bot.loop.create_task(start_playing_task(ctx, next_song))
    else:
        current_song_data = None
        disconnect_timer = bot.loop.create_task(silent_disconnect(ctx))

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Bot is online as {bot.user}')

# -- Bot Commands --
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await setup_booth(ctx, get_help_embed)


@bot.hybrid_command(name='play', aliases=['pl'], description="Play music or search YouTube")
async def play(ctx, *, search: str):
    global current_song_data, current_song_start_time, disconnect_timer
    
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first!")
    
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()
        
    if disconnect_timer:
        disconnect_timer.cancel()
        disconnect_timer = None
        
    async with ctx.typing():
        search_query = search.strip()
        is_link = search_query.startswith("http")

        if not is_link:
            results = VideosSearch(search_query, limit=1).result()
            if not results['result']:
                return await ctx.send("❌ No results found.")
            
            video_data = results['result'][0]
            duration_str = video_data.get('duration')
            
            if duration_str:
                time_parts = duration_str.split(':')
                if len(time_parts) > 2 or (len(time_parts) == 2 and int(time_parts[0]) >= 10):
                    return await ctx.send("🛑 Search results are limited to 10 minutes. Use a direct link!")
            
            url = video_data['link']
        else:
            url = search_query

        try:
            info = ytdl.extract_info(url, download=False)
            data = {
                'url': info['url'], 
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0)
            }
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                song_queue.append(data)
                await ctx.send(f"📂 Added to queue: **{data['title']}**")
            else:
                song_history.append(data)
                current_song_data = data
                current_song_start_time = time.time()
                
                source = await discord.FFmpegOpusAudio.from_probe(data['url'], **ffmpeg_params)
                ctx.voice_client.play(source, after=lambda e: play_next(ctx, e))
                
                view = EnhancementSliderView(
                    ctx, 
                    ffmpeg_params, 
                    song_queue, 
                    apply_live_filter, 
                    current_song_data, 
                    current_song_start_time
                )
                await ctx.send(embed=view.get_embed(), view=view)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")

@bot.command(name='bassboost')
async def bassboost(ctx, level: int = 15): 
    global ffmpeg_params
    if level <= 0:
        ffmpeg_params['options'] = '-vn'
        await ctx.send("🔊 Bass boost **OFF**.")
    else:
        ffmpeg_params['options'] = f'-vn -af "equalizer=f=40:width_type=h:width=50:g={level}"'
        await ctx.send(f"🔊 Bass boost set to **{level}dB**!")

@bot.hybrid_command(name='skip', aliases=['s'], description="Skip the current song")
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop() 
        await ctx.send("⏭️ Skipped!")
    else:
        await ctx.send("❌ Nothing is playing.")

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

@bot.hybrid_command(name='queue', aliases=['q'], description="Show the music queue")
async def show_queue(ctx):
    if not song_queue:
        return await ctx.send("The queue is currently empty.")
    
    msg = "**Upcoming Songs:**\n"
    for i, song in enumerate(song_queue[:10], 1):
        msg += f"{i}. {song['title']}\n"
    await ctx.send(msg)

@bot.hybrid_command(name='leave', aliases=['l', 'dc'], description="Disconnect from voice")
async def leave(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        song_queue.clear()
        song_history.clear()
        await bot.change_presence(activity=None)
        await ctx.send("Bye!")

keep_alive()
bot.run(TOKEN)