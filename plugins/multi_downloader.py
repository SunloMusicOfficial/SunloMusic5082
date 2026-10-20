import os, asyncio
from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user
from utils.downloader import downloader

@app.on_message(filters.command(["spotify", "soundcloud", "jiosaavn"]) & filters.private)
@register_user
async def multi_dl(client, message):
    cmd = message.command[0]
    if len(message.command) < 2: return await message.reply_text(f"🎵 **Usage:** `/{cmd} <song name>`")
    m = await message.reply_text(f"🔍 **Searching on {cmd.capitalize()}...**")
    
    # yt-dlp supports scsearch for soundcloud, for others we just use ytsearch
    platform = "sc" if cmd == "soundcloud" else "yt"
    song = await downloader.search_and_extract(" ".join(message.command[1:]), platform)
    if not song: return await m.edit_text("❌ Not found!")
    
    await m.edit_text("📥 **Downloading...**")
    file_path = await downloader.download_media(song['id'], is_video=False)
    if file_path and os.path.exists(file_path):
        await message.reply_audio(audio=file_path, title=song['title'])
        await m.delete()
    else: await m.edit_text("❌ Download failed.")

@app.on_message(filters.command(["pinterest", "fb", "twitter"]) & filters.private)
@register_user
async def social_dl(client, message):
    if len(message.command) < 2: return await message.reply_text("🔗 **Provide a valid link.**")
    url = message.command[1]
    m = await message.reply_text("📥 **Downloading media...**")
    try:
        import yt_dlp
        ydl = yt_dlp.YoutubeDL({"outtmpl": f"cache/%(id)s.%(ext)s", "quiet": True})
        info = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info)
        if file_path.endswith(('.mp4', '.mkv', '.webm')):
            await message.reply_video(video=file_path)
        else:
            await message.reply_photo(photo=file_path)
        await m.delete()
        os.remove(file_path)
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("tts") & filters.private)
@register_user
async def tts_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("🗣 **Usage:** `/tts <text>`")
    text = " ".join(message.command[1:])
    m = await message.reply_text("🎙 **Generating voice...**")
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en')
        file_path = f"cache/tts_{message.from_user.id}.mp3"
        tts.save(file_path)
        await message.reply_voice(voice=file_path)
        await m.delete()
        os.remove(file_path)
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
