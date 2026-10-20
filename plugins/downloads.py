from ftmgram import filters
from core.bot import app
from utils.decorators import register_user
from utils.downloader import downloader
from utils.formatters import get_readable_time
import os

@app.on_message(filters.command("song") & filters.private)
@register_user
async def song_downloader(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🎵 **Usage:** `/song <song name>`")
    
    query = " ".join(message.command[1:])
    m = await message.reply_text("🔍 **Searching & Downloading...**")
    
    song = await downloader.search_and_extract(query)
    if not song:
        return await m.edit_text("❌ Song not found!")
    
    await m.edit_text("📥 **Downloading audio, please wait...**")
    file_path = await downloader.download_audio(song['id'])
    
    if file_path and os.path.exists(file_path):
        await message.reply_audio(
            audio=file_path,
            title=song['title'],
            performer=song['uploader'],
            caption=f"🎵 **{song['title']}**\n⏱ Duration: {get_readable_time(song['duration'])}"
        )
        await m.delete()
    else:
        await m.edit_text("❌ Download failed.")

@app.on_message(filters.command("video") & filters.private)
@register_user
async def video_downloader(client, message):
    # Video download logic can be added here later
    await message.reply_text("🎬 Video downloader feature is coming soon in premium update!")
