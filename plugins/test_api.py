import aiohttp
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings

@app.on_message(filters.command("testapi") & filters.user(settings.OWNER_ID))
async def test_api_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/testapi <song_name>`")
    
    query = " ".join(message.command[1:])
    api_url = settings.SUNLO_DOWNLOAD_API_URL
    api_key = settings.SUNLO_DOWNLOAD_API_KEY
    
    if not api_url or not api_key:
        return await message.reply_text("❌ **API URL ya Key Render me missing hai!**")

    m = await message.reply_text(f"🚀 Hitting API: `{api_url}`\nQuery: `{query}`...")

    try:
        async with aiohttp.ClientSession() as session:
            payload = {"url": query, "q": query, "api_key": api_key}
            async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=15) as resp:
                status = resp.status
                text = await resp.text()
                
                # Message limit se bachne ke liye sirf pehle 3000 characters
                safe_text = text[:3000] if text else "Empty Response"
                
                await m.edit_text(
                    f"📡 **API Response Status:** `{status}`\n\n"
                    f"📥 **Raw Response:**\n<pre>{safe_text}</pre>",
                    parse_mode=enums.ParseMode.HTML
                )
    except Exception as e:
        await m.edit_text(f"❌ **Connection Failed:**\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)
