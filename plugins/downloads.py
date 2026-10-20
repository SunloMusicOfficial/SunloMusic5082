import os
from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user
from utils.downloader import downloader
from utils.logger import get_logger

logger = get_logger("Downloaders")

@app.on_message(filters.command(["ig", "insta"]) & filters.private)
@register_user
async def insta_dl(client, message):
    if len(message.command) < 2: return await message.reply_text("📸 **Usage:** `/ig <reels link>`")
    url = message.command[1]
    m = await message.reply_text("📥 <b>𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐑𝐞𝐞𝐥𝐬...</b>", parse_mode=enums.ParseMode.HTML)
    
    try:
        opts = {"format": "best", "outtmpl": f"cache/%(id)s.%(ext)s", "quiet": True}
        import yt_dlp
        ydl = yt_dlp.YoutubeDL(opts)
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        
        await message.reply_video(video=file_path, caption=f"✅ <b>Downloaded</b>", parse_mode=enums.ParseMode.HTML)
        await m.delete()
        os.remove(file_path)
    except Exception as e:
        await m.edit_text(f"❌ <b>Error:</b> {e}")

@app.on_message(filters.command("song") & filters.private)
@register_user
async def song_dl(client, message):
    if len(message.command) < 2: return await message.reply_text("🎵 **ᴜꜱᴀɢᴇ:** `/song <name>`")
    m = await message.reply_text("🔍 <b>𝐅𝐢𝐧𝐝𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐬𝐨𝐧𝐠...</b>", parse_mode=enums.ParseMode.HTML)
    
    song = await downloader.search_multiple(" ".join(message.command[1:]), limit=1)
    if not song: return await m.edit_text("❌ ɴᴏᴛ ꜰᴏᴜɴᴅ!")
    
    await m.edit_text("📥 <b>𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐚𝐮𝐝𝐢𝐨...</b>", parse_mode=enums.ParseMode.HTML)
    file_path = await downloader.download_media(song[0]['id'], is_video=False)
    
    if file_path and os.path.exists(file_path):
        await message.reply_audio(audio=file_path, title=song[0]['title'], performer=song[0]['uploader'])
        await m.delete()
    else: await m.edit_text("❌ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ.")
