from ftmgram import filters
from core.bot import app
from core.calls import calls
from utils.decorators import register_user
from plugins.queue import play_next_in_queue
from utils.logger import get_logger

logger = get_logger("Controls")

@app.on_message(filters.command("pause") & filters.group)
@register_user
async def pause_handler(client, message):
    try:
        await calls.pause(message.chat.id)
        await message.reply_text("⏸ **Paused** the current stream.")
    except Exception:
        await message.reply_text("❌ No active stream to pause.")

@app.on_message(filters.command("resume") & filters.group)
@register_user
async def resume_handler(client, message):
    try:
        await calls.resume(message.chat.id)
        await message.reply_text("▶️ **Resumed** the stream.")
    except Exception:
        await message.reply_text("❌ No paused stream found.")

@app.on_message(filters.command(["skip", "next"]) & filters.group)
@register_user
async def skip_handler(client, message):
    await message.reply_text("⏭ **Skipping to next song...**")
    await play_next_in_queue(message.chat.id)

@app.on_message(filters.command(["stop", "end"]) & filters.group)
@register_user
async def stop_handler(client, message):
    try:
        await calls.leave_call(message.chat.id)
        await message.reply_text("⏹ **Stopped** and left the voice chat.")
    except Exception:
        await message.reply_text("❌ I am not in a voice chat.")
