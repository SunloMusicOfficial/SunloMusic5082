import os
from ftmgram import filters, enums
from core.bot import app
import core.calls as calls_module
from pytgcalls.types import MediaStream
from utils.decorators import register_user
from plugins.queue import current_songs

history_db = {}

@app.on_message(filters.command("current") & filters.group)
async def current(client, message):
    chat_id = message.chat.id
    if chat_id not in current_songs: return await message.reply_text("❌ Nothing is playing.")
    song = current_songs[chat_id]
    await message.reply_text(f"🎵 **Currently Playing:**\n\n{song['title']}\n⏱ Duration: {song['duration']}s")

@app.on_message(filters.command("playfile") & filters.group)
async def playfile(client, message):
    if not message.reply_to_message or not message.reply_to_message.audio:
        return await message.reply_text("↩️ Reply to an audio file to play it.")
    m = await message.reply_text("📥 Downloading file...")
    file_path = await client.download_media(message.reply_to_message.audio.file_id, file_name="cache/temp_play.mp3")
    
    try:
        await calls_module.calls.play(message.chat.id, MediaStream(file_path))
        await m.edit_text("▶️ **Playing your file!**")
    except Exception as e: await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("vcjoin") & filters.group)
async def vcjoin(client, message):
    try:
        await calls_module.calls.play(message.chat.id, MediaStream("https://stream.zeno.fm/0r0xa792kwzuv"))
        await message.reply_text("🎙 **Joined VC & playing lofi radio.**")
    except Exception as e: await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("vcleave") & filters.group)
async def vcleave(client, message):
    try:
        await calls_module.calls.leave_call(message.chat.id)
        await message.reply_text("🚪 **Left VC.**")
    except: await message.reply_text("❌ Not in VC.")

@app.on_message(filters.command("history") & filters.group)
async def history(client, message):
    chat_id = message.chat.id
    if chat_id not in history_db or not history_db[chat_id]:
        return await message.reply_text("📭 No history for this chat.")
    text = "🕒 **Recently Played:**\n\n"
    for i, s in enumerate(history_db[chat_id][-5:], 1):
        text += f"{i}. {s}\n"
    await message.reply_text(text)
