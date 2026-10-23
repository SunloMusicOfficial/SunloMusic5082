import time
from ftmgram import filters, enums
from core.bot import app
import core.calls as calls_module
from utils.decorators import register_user
from utils.player_state import playback_start_times, get_player_state
from utils.logger import get_logger
from pytgcalls.types import MediaStream

logger = get_logger("MusicControls")

# ── SEEK COMMAND ──
@app.on_message(filters.command("seek") & filters.group)
@register_user
async def seek_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⏩ <b>Usage:</b> <code>/seek 1:30</code> ya <code>/seek 30</code>", parse_mode=enums.ParseMode.HTML)
    
    chat_id = message.chat.id
    try:
        time_str = message.command[1]
        if ":" in time_str:
            m, s = map(int, time_str.split(":"))
            seconds = m * 60 + s
        else:
            seconds = int(time_str)

        await calls_module.calls.seek(chat_id, seconds)
        playback_start_times[chat_id] = time.time() - seconds
        await message.reply_text(f"⏩ <b>Seeked to</b> <code>{seconds}s</code>", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ <b>Error:</b> <code>{e}</code>", parse_mode=enums.ParseMode.HTML)

# ── SPEED COMMAND ──
@app.on_message(filters.command("speed") & filters.group)
@register_user
async def speed_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚡ <b>Usage:</b> <code>/speed 1.5</code> (0.5 to 2.0)", parse_mode=enums.ParseMode.HTML)
    
    chat_id = message.chat.id
    try:
        speed = float(message.command[1])
        if not 0.5 <= speed <= 2.0:
            raise ValueError
        await calls_module.calls.change_playback_speed(chat_id, speed)
        await message.reply_text(f"⚡ <b>Speed set to</b> <code>{speed}x</code>", parse_mode=enums.ParseMode.HTML)
    except:
        await message.reply_text("❌ <b>Invalid speed.</b> Use 0.5 to 2.0", parse_mode=enums.ParseMode.HTML)

# ── VOLUME COMMAND ──
@app.on_message(filters.command("volume") & filters.group)
@register_user
async def volume_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🔊 <b>Usage:</b> <code>/volume 100</code> (1-200)", parse_mode=enums.ParseMode.HTML)
    
    chat_id = message.chat.id
    try:
        vol = int(message.command[1])
        if not 1 <= vol <= 200:
            raise ValueError
        await calls_module.calls.change_volume_call(chat_id, vol)
        get_player_state(chat_id)["volume"] = vol
        await message.reply_text(f"🔊 <b>Volume set to</b> <code>{vol}%</code>", parse_mode=enums.ParseMode.HTML)
    except:
        await message.reply_text("❌ <b>Invalid volume.</b> Use 1 to 200", parse_mode=enums.ParseMode.HTML)

# ── PITCH COMMAND ──
@app.on_message(filters.command("pitch") & filters.group)
@register_user
async def pitch_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🎵 <b>Usage:</b> <code>/pitch 1.5</code> (0.5 to 2.0)", parse_mode=enums.ParseMode.HTML)
    
    chat_id = message.chat.id
    try:
        pitch = float(message.command[1])
        if not 0.5 <= pitch <= 2.0:
            raise ValueError
        
        from plugins.queue import current_songs
        if chat_id not in current_songs:
            return await message.reply_text("❌ No active stream.")
            
        song = current_songs[chat_id]
        stream_url = song.get('stream_url') or song.get('file_path')
        ffmpeg_args = f"-af atempo={pitch},asetrate=48000*{pitch}"
        await calls_module.calls.play(chat_id, MediaStream(stream_url, ffmpeg_parameters=ffmpeg_args))
        
        await message.reply_text(f"🎵 <b>Pitch set to</b> <code>{pitch}x</code>", parse_mode=enums.ParseMode.HTML)
    except:
        await message.reply_text("❌ <b>Invalid pitch.</b> Use 0.5 to 2.0", parse_mode=enums.ParseMode.HTML)
