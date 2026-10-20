import asyncio, requests, qrcode
from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("wiki") & filters.private)
@register_user
async def wiki_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("📖 **Usage:** `/wiki <query>`")
    query = " ".join(message.command[1:])
    m = await message.reply_text("🔍 Searching Wikipedia...")
    try:
        import wikipedia
        summary = await asyncio.to_thread(wikipedia.summary, query, sentences=3)
        await m.edit_text(f"📖 **{query}**\n\n{summary}")
    except: await m.edit_text("❌ Article not found.")

@app.on_message(filters.command("google") & filters.private)
@register_user
async def google_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("🔍 **Usage:** `/google <query>`")
    query = " ".join(message.command[1:])
    m = await message.reply_text("🔍 Searching Google...")
    try:
        from googlesearch import search
        results = await asyncio.to_thread(lambda: list(search(query, num_results=5)))
        text = f"🔍 **Google Results for:** `{query}`\n\n"
        for i, link in enumerate(results, 1): text += f"{i}. {link}\n"
        await m.edit_text(text)
    except: await m.edit_text("❌ Search failed.")

@app.on_message(filters.command("qr") & filters.private)
@register_user
async def qr_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("🔲 **Usage:** `/qr <text>`")
    text = " ".join(message.command[1:])
    m = await message.reply_text("⚙️ Generating QR...")
    img = qrcode.make(text)
    path = f"cache/qr_{message.from_user.id}.jpg"
    img.save(path)
    await message.reply_photo(photo=path)
    await m.delete()

@app.on_message(filters.command("weather") & filters.private)
@register_user
async def weather_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("☁️ **Usage:** `/weather <city>`")
    city = " ".join(message.command[1:])
    m = await message.reply_text("☁️ Fetching weather...")
    try:
        res = await asyncio.to_thread(requests.get, f"https://wttr.in/{city}?format=3")
        await m.edit_text(f"☁️ **Weather:** `{res.text}`")
    except: await m.edit_text("❌ City not found.")
