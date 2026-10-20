from ftmgram import filters
from pytgcalls.types import MediaStream
from core.bot import app
from core.calls import calls
from utils.decorators import register_user
from utils.downloader import downloader
from utils.formatters import get_readable_time
from plugins.queue import add_to_queue
from utils.logger import get_logger

logger = get_logger("PlayPlugin")

@app.on_message(filters.command("play") & filters.group)
@register_user
async def play_handler(client, message):
    # 1. Check if user gave a query
    if len(message.command) < 2:
        return await message.reply_text("🎵 **Usage:** `/play <song name or YouTube link>`")

    query = " ".join(message.command[1:])
    m = await message.reply_text("🔍 **Searching...**")

    # 2. Extract stream URL using our fast downloader
    song = await downloader.search_and_extract(query)
    if not song:
        return await m.edit_text("❌ **Song not found!** Please try another query.")

    chat_id = message.chat.id
    
    # 3. Check if bot is already playing in this chat
    active_calls = await calls.calls
    if chat_id in active_calls:
        # Add to queue
        await add_to_queue(chat_id, song)
        await m.edit_text(f"📥 **Added to queue:**\n🎵 {song['title']}\n⏱ Duration: {get_readable_time(song['duration'])}")
    else:
        # Play immediately
        await m.edit_text("⚡ **Connecting to Voice Chat...**")
        try:
            stream_url = song.get("stream_url") or song.get("file_path")
            await calls.play(
                chat_id,
                MediaStream(stream_url)
            )
            await m.edit_text(
                f"▶️ **Now Playing:**\n\n"
                f"🎵 **Title:** {song['title']}\n"
                f"⏱ **Duration:** {get_readable_time(song['duration'])}\n"
                f"👤 **Requested by:** {message.from_user.mention}"
            )
        except Exception as e:
            logger.error(f"Play error: {e}")
            await m.edit_text(f"❌ **Error:** Voice chat join nahi kar paya. Make sure I am admin and VC is active.")
