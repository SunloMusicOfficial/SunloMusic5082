import os
import aiohttp
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from utils.decorators import register_user
from utils.downloader import downloader

@app.on_message(filters.command("song") & filters.private)
@register_user
async def song_dl(client, message):
    if len(message.command) < 2: return await message.reply_text("🎵 **ᴜꜱᴀɢᴇ:** `/song <name>`")
    
    m = await message.reply_text("🔍 **Searching & Downloading...**")
    
    # Get Video ID via yt-dlp search
    video_url = " ".join(message.command[1:])
    song_info = await downloader.search_and_extract(video_url)
    if not song_info:
        return await m.edit_text("❌ **Song not found!**")
        
    video_id = song_info['id']
    title = song_info['title']
    
    api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
    api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")
    
    try:
        os.makedirs("cache", exist_ok=True)
        file_path = f"cache/song_{video_id}.mp3"
        
        async with aiohttp.ClientSession() as session:
            payload = {"url": f"https://youtube.com/watch?v={video_id}", "api_key": api_key, "type": "audio"}
            async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=120) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get("Content-Type", "")
                    if "application/json" in content_type:
                        data = await resp.json()
                        stream_url = data.get("url") or data.get("link")
                        if stream_url:
                            async with session.get(stream_url) as file_resp:
                                with open(file_path, "wb") as f:
                                    async for chunk in file_resp.content.iter_chunked(65536):
                                        f.write(chunk)
                    else:
                        with open(file_path, "wb") as f:
                            async for chunk in resp.content.iter_chunked(65536):
                                f.write(chunk)
                                
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        await message.reply_audio(audio=file_path, title=title, performer="Sunlo Music")
                        await m.delete()
                        os.remove(file_path)
                    else:
                        await m.edit_text("❌ Download failed. File is empty.")
                else:
                    await m.edit_text(f"❌ API Error: {resp.status}")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("video") & filters.private)
@register_user
async def video_dl(client, message):
    if len(message.command) < 2: return await message.reply_text("🎬 **ᴜꜱᴀɢᴇ:** `/video <name>`")
    # Same logic as above, just change "type": "audio" to "type": "video" and reply_video
    m = await message.reply_text("🔍 **Searching & Downloading Video...**")
    
    video_url = " ".join(message.command[1:])
    song_info = await downloader.search_and_extract(video_url)
    if not song_info:
        return await m.edit_text("❌ **Video not found!**")
        
    video_id = song_info['id']
    title = song_info['title']
    
    api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
    api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")
    
    try:
        os.makedirs("cache", exist_ok=True)
        file_path = f"cache/video_{video_id}.mp4"
        
        async with aiohttp.ClientSession() as session:
            payload = {"url": f"https://youtube.com/watch?v={video_id}", "api_key": api_key, "type": "video"}
            async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=180) as resp:
                if resp.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(65536):
                            f.write(chunk)
                                
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        await message.reply_video(video=file_path, caption=f"🎬 {title}")
                        await m.delete()
                        os.remove(file_path)
                    else:
                        await m.edit_text("❌ Download failed. File is empty.")
                else:
                    await m.edit_text(f"❌ API Error: {resp.status}")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
