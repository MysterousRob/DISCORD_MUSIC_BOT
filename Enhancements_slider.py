import discord
import time

class EnhancementSliderView(discord.ui.View):
    def __init__(self, ctx, ffmpeg_params, song_queue, apply_filter_func, current_data, start_time):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.ffmpeg_params = ffmpeg_params
        self.song_queue = song_queue
        self.apply_filter_func = apply_filter_func
        self.current_data = current_data
        self.start_time = start_time
        
        # Mixer & Toggle States
        self.bass_level = 0
        self.speed_level = 1.0
        self.muffle_level = 5000
        self.is_8d = False
        self.is_reverb = False
        self.loop_mode = "None"# Options: None, Song,

    def create_progress_bar(self):
        """Calculates 01:45 / 03:20 style progress."""
        if not self.current_data: return "00:00 / 00:00"
        elapsed = int(time.time() - self.start_time)
        total = self.current_data.get('duration', 0)
        
        def format_time(seconds):
            return time.strftime('%M:%S', time.gmtime(seconds))
            
        progress = int((elapsed / total) * 10) if total > 0 else 0
        bar = "".join(["🟦" if i < progress else "⬜" for i in range(10)])
        return f"{bar} `{format_time(elapsed)} / {format_time(total)}`"
    
    def create_bar(self, current, min_val, max_val):
        """Creates a visual [▬▬🔘▬▬] bar."""
        size = 10
        progress = int(((current - min_val) / (max_val - min_val)) * size)
        bar = "".join(["▬" if i != progress else "🔘" for i in range(size + 1)])
        return f"`{bar}`"

    def get_embed(self):
        """Generates the unified Studio Mixer UI."""
        embed_color = discord.Color.from_rgb(255, 182, 193)
        if self.muffle_level < 2500: embed_color = discord.Color.blue()
        if self.bass_level > 20: embed_color = discord.Color.red()

        embed = discord.Embed(
            title=f"🎶 {self.current_data.get('title', 'Unknown')}",
            description=f"**Status:** {self.loop_mode} Loop | 8D: {'ON' if self.is_8d else 'OFF'} | Reverb: {'ON' if self.is_reverb else 'OFF'}",
            color=embed_color
        )
        
        embed.add_field(name="Progress", value=self.create_progress_bar(), inline=False)
        embed.add_field(name=f"🔊 Bass: {self.bass_level}dB", value=self.create_bar(self.bass_level, 0, 40), inline=True)
        embed.add_field(name=f"⚡ Speed: {self.speed_level:.2f}x", value=self.create_bar(self.speed_level, 0.5, 2.0), inline=True)
        embed.add_field(name=f"📻 Muffle: {self.muffle_level}Hz", value=self.create_bar(self.muffle_level, 500, 5000), inline=True)
        
        return embed

    async def update_and_apply(self, interaction):
        """Builds the complex filter string."""
        filters = [
            f"equalizer=f=40:width_type=h:width=50:g={self.bass_level}",
            f"asetrate=44100*{self.speed_level},atempo={self.speed_level}",
            f"lowpass=f={self.muffle_level}"
        ]
        if self.is_8d: filters.append("apulsator=hz=0.125")
        if self.is_reverb: filters.append("aecho=0.8:0.88:60:0.4")
        
        self.ffmpeg_params['options'] = f"-vn -b:a 192k -af \"{','.join(filters)}\""
        await interaction.response.edit_message(embed=self.get_embed(), view=self)
        await self.apply_filter_func(self.ctx)

    # --- Controls ---
    # --- ROW 0: Playback & Utility ---
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.success, row=0)
    async def toggle_play(self, interaction, button):
        if self.ctx.voice_client and self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            await interaction.response.send_message("▶️ Resumed", ephemeral=True)
        elif self.ctx.voice_client:
            self.ctx.voice_client.pause()
            await interaction.response.send_message("⏸️ Paused", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary, row=0)
    async def skip_button(self, interaction, button):
        if self.ctx.voice_client:
            self.ctx.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped!", ephemeral=True)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction, button):
        if self.ctx.voice_client:
            await self.ctx.voice_client.disconnect()
            await interaction.response.send_message("⏹️ Left.", ephemeral=True)
    
    @discord.ui.button(label="Queue", emoji="📜", style=discord.ButtonStyle.secondary, row=0)
    async def queue_button(self, interaction, button):
        if not self.song_queue:
            return await interaction.response.send_message("The queue is empty.", ephemeral=True)
        msg = "**Upcoming:**\n" + "\n".join([f"{i+1}. {s['title']}" for i, s in enumerate(self.song_queue[:10])])
        await interaction.response.send_message(msg, ephemeral=True)

    @discord.ui.button(label="Loop", emoji="🔁", style=discord.ButtonStyle.secondary, row=0)
    async def toggle_loop(self, interaction, button):
        modes = ["None", "Song", "Queue"]
        self.loop_mode = modes[(modes.index(self.loop_mode) + 1) % 3]
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    # --- ROW 1: Bass ---
    @discord.ui.button(label="- Bass", style=discord.ButtonStyle.secondary, row=1)
    async def bass_down(self, interaction, button):
        self.bass_level = max(0, self.bass_level - 5)
        await self.update_and_apply(interaction)

    @discord.ui.button(label="+ Bass", style=discord.ButtonStyle.secondary, row=1)
    async def bass_up(self, interaction, button):
        self.bass_level = min(40, self.bass_level + 5)
        await self.update_and_apply(interaction)

    # --- ROW 2: Speed & Reset ---
    @discord.ui.button(label="Slower", style=discord.ButtonStyle.secondary, row=2)
    async def speed_down(self, interaction, button):
        self.speed_level = round(max(0.5, self.speed_level - 0.1), 2)
        await self.update_and_apply(interaction)

    @discord.ui.button(label="Faster", style=discord.ButtonStyle.secondary, row=2)
    async def speed_up(self, interaction, button):
        self.speed_level = round(min(2.0, self.speed_level + 0.1), 2)
        await self.update_and_apply(interaction)

    @discord.ui.button(label="Reset Mixer", style=discord.ButtonStyle.danger, row=2)
    async def reset(self, interaction, button):
        self.bass_level, self.speed_level, self.muffle_level = 0, 1.0, 5000
        self.is_8d = self.is_reverb = False
        await self.update_and_apply(interaction)

    # --- ROW 3: Muffle ---
    @discord.ui.button(label="+ Muffle", style=discord.ButtonStyle.secondary, row=3)
    async def muffle_down(self, interaction, button):
        self.muffle_level = max(500, self.muffle_level - 500)
        await self.update_and_apply(interaction)

    @discord.ui.button(label="- Muffle", style=discord.ButtonStyle.secondary, row=3)
    async def muffle_up(self, interaction, button):
        self.muffle_level = min(5000, self.muffle_level + 500)
        await self.update_and_apply(interaction)

    # --- ROW 4: Effects ---
    @discord.ui.button(label="8D Audio", style=discord.ButtonStyle.secondary, row=4)
    async def toggle_8d(self, interaction, button):
        self.is_8d = not self.is_8d
        button.style = discord.ButtonStyle.primary if self.is_8d else discord.ButtonStyle.secondary
        await self.update_and_apply(interaction)
    
    @discord.ui.button(label="Reverb", style=discord.ButtonStyle.secondary, row=4)
    async def toggle_reverb(self, interaction, button):
        self.is_reverb = not self.is_reverb
        button.style = discord.ButtonStyle.primary if self.is_reverb else discord.ButtonStyle.secondary
        await self.update_and_apply(interaction)