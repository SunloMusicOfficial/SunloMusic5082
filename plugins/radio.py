from ftmgram import filters
from core.bot import app
from utils.decorators import register_user
import core.calls as calls_module
from pytgcalls.types import MediaStream
from plugins.play import get_player_buttons
import time

RADIO_STATIONS = {
    "lofi": "https://stream.zeno.fm/0r0xa792kwzuv",
    "bollywood": "https://stream.zeno.fm/1c4vt2b8tv8uv",
    "english": "https://stream.zeno.fm/5x8b6q1y9v8uv"
}

@app.on_message(filters.command("radio") & filters.group)
@register_user
async def radio_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("📻 **Available Radio:**\n`lofi`, `bollywood`, `english`\n\n**Usage:** `/radio lofi`")
    
    station = message.command[1].lower()
    if station not in RADIO_STATIONS:
        return await message.reply_text("❌ Station not found!")
        
    chat_id = message.chat.id
    url = RADIO_STATIONS[station]
    
    m = await message.reply_text(f"📻 **Connecting to {station.upper()} Radio...**")
    
    try:
        await calls_module.calls.play(chat_id, MediaStream(url))
        
        caption = (
            f"<blockquote>📻 <b>𝐋𝐈𝐕𝐄 𝐑𝐀𝐃𝐈𝐎</b>\n\n"
            f"🎙 <b>Station:</b> {station.upper()}\n"
            f"📡 <b>Status:</b> Live & Non-stop</blockquote>"
        )
        await m.edit_text(caption, reply_markup=get_player_buttons(chat_id))
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
