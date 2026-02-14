import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import yt_dlp
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# -- Config --
song_queue = []
song_history = []

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'default_search': 'ytsearch', # Changed to prioritize search
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

ffmpeg_params = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 192k', # Forces high-quality bitrate for music
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
def play_next(ctx):
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
        try:
            # Re-routing search to find 'Music' versions specifically
            if "youtube.com" not in search and "youtu.be" not in search and "soundcloud.com" not in search:
                # This string helps the bot find songs, not vlogs
                search_query = f"{search} official audio"
                info = ytdl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
            else:
                info = ytdl.extract_info(search, download=False)

            # Strict Music Filter: Skip if video is too long (over 12 mins)
            if info.get('duration', 0) > 720:
                return await ctx.send("🛑 That file is too long for a music bot. Please request a song under 12 minutes.")

            data = {'url': info['url'], 'title': info['title']}

            if ctx.voice_client.is_playing():
                song_queue.append(data)
                await ctx.send(f"✅ Added to queue: **{data['title']}**")
            else:
                song_history.append(data)
                await bot.change_presence(activity=discord.Activity(
                    type=discord.ActivityType.listening, name=data['title']
                ))
                
                source = await discord.FFmpegOpusAudio.from_probe(data['url'], **ffmpeg_params)
                ctx.voice_client.play(source, after=lambda e: play_next(ctx))
                
                view = MasterControlView(ctx)
                await ctx.send(f"🎶 Now playing: **{data['title']}**", view=view)
        
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

# ... (Include your skip, previous, queue, and leave commands)

bot.run(TOKEN)

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

bot.run(TOKEN)