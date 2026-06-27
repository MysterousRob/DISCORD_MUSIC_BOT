import discord
from discord.ext import commands

control_message = None

async def create_dj_booth(guild):
    category = discord.utils.get(guild.categories, name="MUSIC BOTSsss")
    if not category:
        category = await guild.create_category("MUSIC BOTS")
        
    channel = discord.utils.get(guild.text_channels, name="creampie-control")
    if not channel:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=True, read_messages=True),
            guild.me: discord.PermissionOverwrite(send_messages=True, manage_messages=True)
        }
        channel = await guild.create_text_channel("creampie-controlll", category=category, overwrites=overwrites)
    return channel

async def update_control_panel(ctx, view, control_channel, get_help_embed):
    global control_message
    if control_message:
        try:
            await control_message.delete()
        except discord.NotFound:
            pass 
        except Exception as e:
            print(f"Cleanup error: {e}")
    control_message = await ctx.send(embed=view.get_embed(), view=view)

async def setup_booth(ctx, get_help_embed):
    channel = await create_dj_booth(ctx.guild)
    if channel:
        await channel.send(embed=get_help_embed())
        await ctx.send("✅ DJ Booth created!")
    else:
        await ctx.send("❌ Channel already exists.")