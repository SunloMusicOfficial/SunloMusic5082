import os, aiohttp
from ftmgram import filters
from core.bot import app
from config.settings import settings
from utils.logger import get_logger
from plugins.play import play_handler

logger = get_logger("Shazam")

@app.on_message(filters.command("shazam") & filters.group)
async def shazam_handler(client, message):
    if not message.reply_to_message or not message.reply_to_message.voice:
        return await message.reply_text("↩️ Reply to a voice message with `/shazam` to identify the song.")
    
    api_key = os.getenv("AUDD_API_KEY")
    if not api_key:
        return await message.reply_text("⚠️ **AUDD_API_KEY set nahi hai .env mein!** Get it from audd.io")
        
    m = await message.reply_text("🎧 **Identifying song...**")
    file_path = await client.download_media(message.reply_to_message.voice.file_id)
    
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('api_token', api_key)
            data.add_field('file', open(file_path, 'rb'))
            data.add_field('return', 'spotify')
            
            async with session.post('https://api.audd.io/', data=data) as resp:
                res = await resp.json()
                
                if res.get('status') == 'success' and res.get('result'):
                    song = res['result']
                    title = song['title']
                    artist = song['artist']
                    
                    await m.edit_text(f"🎵 **Song Found:**\n\n**Title:** {title}\n**Artist:** {artist}\n\n_Playing now..._")
                    
                    message.command = ["/play", f"{title} {artist}"]
                    message.text = f"/play {title} {artist}"
                    await play_handler(client, message)
                else:
                    await m.edit_text("❌ **Song recognize nahi ho paya.** Try a longer voice note.")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
