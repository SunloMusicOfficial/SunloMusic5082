from ftmgram import filters
from core.bot import app
from utils.decorators import register_user
from plugins.queue import get_player_state, current_songs
import core.calls as calls_module
from pytgcalls.types import MediaStream

@app.on_message(filters.command(["bass", "8d", "nightcore", "slowed", "vaporwave", "normal", "karaoke"]) & filters.group)
@register_user
async def effects_handler(client, message):
    chat_id = message.chat.id
    state = get_player_state(chat_id)
    effect = message.command[0].lower()
    
    state["effect"] = None if effect == "normal" else effect
    await message.reply_text(f"🎛 Effect set to: **{effect.upper()}**\n_May take a second to apply._")
    
    if chat_id in current_songs:
        song = current_songs[chat_id]
        stream_url = song.get("stream_url") or song.get("file_path")
        
        ffmpeg_args = None
        if effect == "bass": ffmpeg_args = "-af bass=g=15"
        elif effect == "8d": ffmpeg_args = "-af apulsator=hz=0.08"
        elif effect == "nightcore": ffmpeg_args = "-af atempo=1.2,asetrate=48000*1.2"
        elif effect == "slowed": ffmpeg_args = "-af atempo=0.85,asetrate=44100*0.85"
        elif effect == "vaporwave": ffmpeg_args = "-af atempo=0.8,asetrate=44100*0.8"
        elif effect == "karaoke": ffmpeg_args = "-af pan=stereo|c0=c0|c1=-1*c1" # Vocal removal
        
        await calls_module.calls.play(chat_id, MediaStream(stream_url, ffmpeg_parameters=ffmpeg_args))

@app.on_message(filters.command("soundboard") & filters.group)
@register_user
async def soundboard_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🔊 **Available Sounds:**\n`airhorn`, `applause`, `drum`\n\n**Usage:** `/soundboard airhorn`")
    sound = message.command[1].lower()
    
    sounds = {
        "airhorn": "https://www.myinstants.com/media/sounds/airhorn.mp3",
        "applause": "https://www.myinstants.com/media/sounds/applause.mp3",
        "drum": "https://www.myinstants.com/media/sounds/rimshot.mp3"
    }
    if sound not in sounds: return await message.reply_text("❌ Sound not found.")
    
    await message.reply_text(f"🔊 **Playing {sound}...**")
    await calls_module.calls.play(message.chat.id, MediaStream(sounds[sound]))
