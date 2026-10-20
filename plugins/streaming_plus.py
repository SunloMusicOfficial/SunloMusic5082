import asyncio, random
from ftmgram import filters, enums
from core.bot import app
import core.calls as calls_module
from utils.decorators import register_user
from pytgcalls.types import MediaStream
from plugins.queue import add_to_queue, get_player_state
from utils.downloader import downloader

RADIOS = {
    "lofi": "https://stream.zeno.fm/0r0xa792kwzuv",
    "bollywood": "https://stream.zeno.fm/1c4vt2b8tv8uv",
    "english": "https://stream.zeno.fm/5x8b6q1y9v8uv"
}

@app.on_message(filters.command("radio") & filters.group)
@register_user
async def radio_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("📻 **Available:** `lofi`, `bollywood`, `english`")
    station = message.command[1].lower()
    if station not in RADIOS: return await message.reply_text("❌ Station not found!")
    
    m = await message.reply_text(f"📻 **Connecting to {station.upper()}...**")
    try:
        await calls_module.calls.play(message.chat.id, MediaStream(RADIOS[station]))
        await m.edit_text(f"📻 **Live:** {station.upper()} Radio")
    except Exception as e: await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("sleep") & filters.group)
@register_user
async def sleep_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("⏱ **Usage:** `/sleep 10` (minutes)")
    try:
        mins = int(message.command[1])
        await message.reply_text(f"😴 **Sleep timer set for {mins} minutes.**")
        await asyncio.sleep(mins * 60)
        await calls_module.calls.leave_call(message.chat.id)
        await message.reply_text("😴 **Sleep timer ended. Bot left VC.**")
    except: pass

@app.on_message(filters.command("ai_dj") & filters.group)
@register_user
async def ai_dj(client, message):
    moods = ["lofi chill beats", "party dance mix", "sad emotional songs", "rock metal", "romantic hindi songs"]
    mood = random.choice(moods)
    m = await message.reply_text(f"🤖 **AI DJ:** *Mood detected: {mood}*\n🔍 Finding song...")
    
    song = await downloader.search_and_extract(mood)
    if not song: return await m.edit_text("❌ AI DJ failed to find a song.")
    
    chat_id = message.chat.id
    active_calls = await calls_module.calls.calls
    if chat_id in active_calls:
        await add_to_queue(chat_id, song)
        await m.edit_text(f"📥 **AI DJ Added:** {song['title']}")
    else:
        from plugins.play import play_song_by_id
        await play_song_by_id(client, message, m, song['id'])
