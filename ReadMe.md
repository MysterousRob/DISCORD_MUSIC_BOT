# 🎶 Cream Pie Discord Music Bot

A Discord music bot built with Python and `discord.py`. The bot can join voice channels, play YouTube audio, manage a queue, and provide interactive playback controls and audio enhancements.

---

## 📋 Requirements

Before installing the bot, make sure you have:

- Windows 10/11
- Python 3.12+ recommended
- FFmpeg
- A Discord Bot Application
- Git
- Internet connection

---

# 🚀 Installation

## 1. Clone the Repository

Clone the project using Git:

```bash
git clone https://github.com/MysterousRob/CUM_STAINZ_DISCORD_MUSIC_BOT.git
```

Enter the project directory:

```bash
cd CUM_STAINZ_DISCORD_MUSIC_BOT
```

---

## 2. Create a Python Virtual Environment

Create a virtual environment inside the project:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see:

```text
(.venv)
```

at the beginning of your terminal.

Example:

```text
(.venv) PS C:\Users\YourName\Desktop\CUM_STAINZ_DISCORD_MUSIC_BOT>
```

---

## 3. Install Dependencies

Make sure the virtual environment is activated.

Install the required Python packages:

```powershell
pip install -r requirements.txt
```

The project uses packages including:

- `discord.py`
- `yt-dlp`
- `python-dotenv`
- `PyNaCl`
- `Flask`
- `lyricsgenius`
- `youtube-search-python`
- `httpx`

---

# 🔐 Discord Bot Setup

## 4. Create a Discord Application

Go to the Discord Developer Portal:

[https://discord.com/developers/applications](https://discord.com/developers/applications)

Create a new application.

Then:

1. Open the application.
2. Go to **Bot**.
3. Create/add the bot.
4. Copy the bot token.

⚠️ **NEVER share your bot token or commit it to GitHub.**

If a token is exposed, reset it immediately in the Discord Developer Portal.

---

## 5. Enable Required Intents

In the Discord Developer Portal, open:

**Bot → Privileged Gateway Intents**

Enable:

- **Message Content Intent**

The bot uses message content and Discord guild functionality.

---

# 🔑 Environment Variables

## 6. Create the `.env` File

Create a file named:

```text
.env
```

Place it in the **root of the project**, next to `main.py`.

Your project should look similar to:

```text
CUM_STAINZ_DISCORD_MUSIC_BOT/
│
├── .env
├── .gitignore
├── main.py
├── bot_ui.py
├── Enhancements_slider.py
├── requirements.txt
├── Dockerfile
└── .venv/
```

Inside `.env`, add:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

Replace:

```text
YOUR_DISCORD_BOT_TOKEN
```

with the actual Discord bot token.

### Example

```env
DISCORD_TOKEN=your_actual_token_here
```

Do **not** add unnecessary quotes or spaces.

---

# 🛡️ Protect Your Secrets

Make sure `.env` is included in `.gitignore`.

Your `.gitignore` should contain:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

Never commit `.env` to Git.

---

# 🎬 FFmpeg Setup

FFmpeg is required for the bot to play audio in Discord voice channels.

## 7. Install FFmpeg

The bot requires a working `ffmpeg.exe`.

A recommended Windows installation is:

```text
C:\ffmpeg\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe
```

You can verify FFmpeg by running:

```powershell
ffmpeg -version
```

You should see the FFmpeg version information.

---

## ⚠️ Windows Application Control Error

If you receive:

```text
WinError 4551
An Application Control policy has blocked this file
```

Windows may be blocking a different FFmpeg installation.

Check which FFmpeg installations Windows can find:

```powershell
where.exe ffmpeg
```

For example:

```text
C:\ProgramData\chocolatey\bin\ffmpeg.exe
C:\ffmpeg\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe
C:\Users\YourName\AppData\Local\Microsoft\WinGet\Links\ffmpeg.exe
```

Test the known working FFmpeg directly:

```powershell
& "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe" -version
```

If that works but:

```powershell
ffmpeg -version
```

does not, Windows is likely finding another FFmpeg installation first.

### Temporary Fix

For the current PowerShell session, put the working FFmpeg directory first in `PATH`:

```powershell
$env:PATH = "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin;" + $env:PATH
```

Then verify:

```powershell
ffmpeg -version
```

If FFmpeg displays its version successfully, the bot can use it.

> If your FFmpeg is installed somewhere else, replace the path with your actual FFmpeg `bin` directory.

---

# ▶️ Running the Bot

## 8. Activate the Virtual Environment

Every time you open a new terminal, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If FFmpeg requires the temporary PATH fix, run:

```powershell
$env:PATH = "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin;" + $env:PATH
```

---

## 9. Start the Bot

Run:

```powershell
python main.py
```

A successful startup should look similar to:

```text
INFO discord.client logging in using static token
INFO discord.gateway Shard ID None has connected to Gateway
Bot is online as Cream Pie#9032
```

The bot should now appear **Online** in Discord.

---

# 🎵 Using the Bot

Once the bot is online, join a Discord voice channel.

The main music command is:

```text
.play <song name>
```

Example:

```text
.play Never Gonna Give You Up
```

You can also use:

```text
.pl <song name>
```

---

## Available Commands

### Play

```text
.play <song>
```

or:

```text
.pl <song>
```

Searches YouTube and starts playing the selected song.

---

### Skip

```text
.skip
```

or:

```text
.s
```

Skips the current song.

---

### Queue

```text
.queue
```

or:

```text
.q
```

Displays the current music queue.

---

### Leave

```text
.leave
```

or:

```text
.l
```

or:

```text
.dc
```

Disconnects the bot from the voice channel.

---

### Bass Boost

```text
.bassboost
```

You can also specify a level:

```text
.bassboost 20
```

---

### Previous

```text
.previous
```

Returns to a previously played song when available.

---

### Setup

```text
.setup
```

Creates the bot's music control/DJ booth.

The setup command requires administrator permissions.

---

# 🎛️ Interactive Music Controls

When a song starts playing, the bot provides an interactive control panel.

The controls include:

- ▶️ / ⏸️ Play / Pause
- ⏭️ Skip
- ⏹️ Stop
- 📜 Queue
- 🔁 Loop
- Bass adjustment
- Playback speed
- Muffle filter
- 8D Audio
- Reverb
- Mixer reset

---

# 🌐 Flask Health Check

The bot also starts a small Flask web server.

By default it runs on:

```text
http://127.0.0.1:8000
```

The server also listens on the machine's network address.

Opening the root page should return:

```text
Bot is online and healthy!
```

---

# 🧪 Troubleshooting

## Bot says `Improper token has been passed`

Example:

```text
discord.errors.LoginFailure: Improper token has been passed.
```

Check your `.env` file:

```env
DISCORD_TOKEN=YOUR_BOT_TOKEN
```

Make sure you copied the **Bot Token**, not:

- Application ID
- Client ID
- Client Secret
- Public Key

You can test whether Python is loading the token without printing the token itself:

```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); t=os.getenv('DISCORD_TOKEN'); print('Token found:', t is not None); print('Token length:', len(t) if t else 0); print('Starts with:', t[:5] if t else 'NONE')"
```

Never paste the complete token into a public location.

---

## FFmpeg Cannot Run

If you receive:

```text
WinError 4551
An Application Control policy has blocked this file
```

run:

```powershell
where.exe ffmpeg
```

Then test the actual executable directly:

```powershell
& "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe" -version
```

If the direct command works, put that FFmpeg directory first in the current terminal's PATH:

```powershell
$env:PATH = "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin;" + $env:PATH
```

Then test:

```powershell
ffmpeg -version
```

---

## Bot Does Not Join Voice

Make sure:

1. You are inside a voice channel.
2. The bot has permission to:
   - Connect
   - Speak
3. PyNaCl is installed:

```powershell
pip install pynacl
```

---

## YouTube Warnings

You may see warnings similar to:

```text
Some ios client https formats have been skipped
```

or:

```text
YouTube may have enabled the SABR-only streaming experiment
```

These are `yt-dlp` warnings and do not necessarily mean the bot failed.

If the bot successfully joins the voice channel and plays audio, the warnings can generally be ignored.

---

# 🛑 Stopping the Bot

To stop the bot:

```text
CTRL + C
```

in the terminal running `main.py`.

---

# 🔄 Starting the Bot Again

After closing VS Code or opening a new terminal:

```powershell
cd C:\path\to\CUM_STAINZ_DISCORD_MUSIC_BOT
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If needed, set the FFmpeg PATH:

```powershell
$env:PATH = "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin;" + $env:PATH
```

Then start the bot:

```powershell
python main.py
```

---

# 🔒 Security Checklist

Before pushing the project to GitHub, verify:

- [ ] `.env` is in `.gitignore`
- [ ] `.venv/` is in `.gitignore`
- [ ] The Discord token is not inside Python files
- [ ] The Discord token is not inside the README
- [ ] The Discord token is not committed to Git
- [ ] If the token was exposed, it has been reset

---

# 📁 Project Structure

```text
CUM_STAINZ_DISCORD_MUSIC_BOT/
│
├── .env                      # 🔒 Secrets - DO NOT COMMIT
├── .gitignore
├── .venv/                    # Python virtual environment
│
├── main.py                   # Main bot
├── bot_ui.py                 # DJ booth / control UI
├── Enhancements_slider.py    # Audio enhancement controls
│
├── requirements.txt          # Python dependencies
├── Dockerfile
└── README.md
```

---

# ✅ Quick Start

For someone who already has Python and FFmpeg installed:

```powershell
git clone <REPOSITORY_URL>
cd CUM_STAINZ_DISCORD_MUSIC_BOT

python -m venv .venv

.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create `.env`:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
```

If necessary, configure FFmpeg:

```powershell
$env:PATH = "C:\ffmpeg\ffmpeg-8.0.1-full_build\bin;" + $env:PATH
```

Start the bot:

```powershell
python main.py
```

Once you see:

```text
Bot is online as Cream Pie#9032
```

the bot is ready to use.
