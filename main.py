import os
import discord
import yt_dlp
import asyncio
from discord.ext import commands
from flask import Flask
from threading import Thread
from youtubesearchpython import VideosSearch

app = Flask('')
@app.route('/')
def home():
    return "Bot is online and healthy!"

def run():
    # Koyeb uses port 8000 by default for free tier
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()


TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# -- Config --
song_queue = []
song_history = []

ytdl_format_options = {
    'format': 'bestaudio/best/worst',
    'cookiefile': 'cookies.txt',  # Ensure this matches your filename on GitHub
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_params = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 192k',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

# -- UI Components (The Menu) -- 
class MasterControlView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.select(
        placeholder="PC/Web: Audio Effects & EQ",
        row=0,
        options=[
            discord.SelectOption(label="Normal (Reset)", emoji="🎵", value="0"),
            discord.SelectOption(label="Bass Boost (Light)", emoji="🔊", value="10"),
            discord.SelectOption(label="Bass Boost (HEAVY)", emoji="🔥", value="25"),
        ]
    )
    async def select_callback(self, interaction, select):
        global ffmpeg_params
        level = int(select.values[0])
        if level == 0:
            ffmpeg_params['options'] = '-vn -b:a 192k'
            await interaction.response.send_message("🔊 EQ Reset to Normal", ephemeral=True)
        else:
            ffmpeg_params['options'] = f'-vn -b:a 192k -af "equalizer=f=40:width_type=h:width=50:g={level}"'
            await interaction.response.send_message(f"🔊 Bass set to {level}dB (Applied to next song)", ephemeral=True)

    @discord.ui.button(label="Pause/Resume", style=discord.ButtonStyle.success, emoji="⏯️", row=1)
    async def toggle_play(self, interaction, button):
        if self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        else:
            self.ctx.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused", ephemeral=True)

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", row=1)
    async def skip_button(self, interaction, button):
        self.ctx.voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)

    @discord.ui.button(label="Stop & Leave", style=discord.ButtonStyle.danger, emoji="⏹️", row=1)
    async def stop_button(self, interaction, button):
        await self.ctx.voice_client.disconnect()
        song_queue.clear()
        await interaction.response.send_message("👋 Cleared and Left", ephemeral=True)

# -- Helpers -- 
def play_next(ctx, error=None): 
    if error:
        print(f"Player error: {error}")
    if len(song_queue) > 0:
        next_song = song_queue.pop(0)
        song_history.append(next_song)
        
        bot.loop.create_task(bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.listening, name=next_song['title']
        )))
        
        source = discord.FFmpegOpusAudio.from_probe(next_song['url'], **ffmpeg_params)
        ctx.voice_client.play(source, after=lambda e: play_next(ctx))
        
        view = MasterControlView(ctx)
        bot.loop.create_task(ctx.send(f"🎶 Now playing: **{next_song['title']}**", view=view))
    else:
        bot.loop.create_task(bot.change_presence(activity=None))

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

# -- Bot Commands --

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Join a voice channel first!")

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    async with ctx.typing():
        if "youtube.com" not in search and "youtu.be" not in search:
            query = VideosSearch(search, limit=1)
            results = query.result()
            if not results['result']:
                return await ctx.send("❌ No results found.")
            url = results['result'][0]['link']
        else:
            url = search

        try:
            info = ytdl.extract_info(url, download=False)
            source_url = info['url']
            title = info.get('title', 'Unknown Song')
            
            # Use ffmpeg_params here to match your variable at the top
            source = await discord.FFmpegOpusAudio.from_probe(source_url, **ffmpeg_params)
            ctx.voice_client.play(source, after=lambda e: play_next(ctx, e))
            
            await ctx.send(f"🎶 Now playing: **{title}**")
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
        await ctx.send(f"🔊 Bass boost set to **{level}dB**! (Applies to the next song)")

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
    
    msg = "**Upcoming Songs:**\n"
    for i, song in enumerate(song_queue, 1):
        msg += f"{i}. {song['title']}\n"
    await ctx.send(msg)

@bot.command(name='leave')
async def leave(ctx):
    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        song_queue.clear()
        song_history.clear()
        await bot.change_presence(activity=None)
        await ctx.send("Bye!")

keep_alive()
bot.run(TOKEN)