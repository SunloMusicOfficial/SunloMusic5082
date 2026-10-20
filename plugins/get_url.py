import aiohttp
import os
from ftmgram import filters
from ftmgram.types import Message
from core.bot import app
from utils.logger import get_logger

logger = get_logger("ImageURL")

@app.on_message(filters.command("geturl"))
async def geturl_handler(client, message: Message):
    # Check karo ki user ne reply kiya hai ya direct photo bheji hai
    if not (message.reply_to_message and message.reply_to_message.photo) and not message.photo:
        return await message.reply_text(
            "📸 **Usage:**\n"
            "1. Koi photo bhejo caption mein `/geturl` likh kar.\n"
            "2. Ya kisi photo par reply karke `/geturl` likho."
        )
    
    photo = message.reply_to_message.photo if message.reply_to_message else message.photo
    m = await message.reply_text("📥 **Downloading image...**")
    
    try:
        # Photo download karo temporary
        file_path = await client.download_media(photo.file_id)
        
        await m.edit_text("☁️ **Uploading to cloud...**")
        
        # Upload to catbox.moe
        async with aiohttp.ClientSession() as session:
            with open(file_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('reqtype', 'fileupload')
                data.add_field('fileToUpload', f, filename=os.path.basename(file_path))
                
                async with session.post('https://catbox.moe/user/api.php', data=data) as resp:
                    if resp.status == 200:
                        url = await resp.text()
                        if url.startswith("https://"):
                            # Success
                            await m.edit_text(
                                f"✅ **Image Uploaded Successfully!**\n\n"
                                f"🔗 **Direct URL:**\n`{url}`\n\n"
                                f"🆔 **Telegram File ID (Recommended):**\n`{photo.file_id}`\n\n"
                                f"💡 **Tip:** `file_id` use karna URL se zyada fast hota hai, kyunki image Telegram ke apne server se load hoti hai aur kabhi block nahi hoti. Aap dono mein se koi bhi use kar sakte hain `.env` mein!"
                            )
                        else:
                            await m.edit_text(f"❌ Upload failed: {url}")
                    else:
                        await m.edit_text(f"❌ Server error: {resp.status}")
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        
    except Exception as e:
        logger.error(f"Error in geturl: {e}")
        await m.edit_text(f"❌ Error: {e}")
