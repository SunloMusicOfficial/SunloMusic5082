import base64, requests, time
from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("calc") & filters.private)
async def calc(client, message):
    if len(message.command) < 2: return await message.reply_text("🧮 Usage: `/calc 2+2`")
    expr = " ".join(message.command[1:])
    try:
        result = eval(expr)
        await message.reply_text(f"🧮 **Result:** `{result}`")
    except: await message.reply_text("❌ Invalid expression.")

@app.on_message(filters.command("translate") & filters.private)
async def translate(client, message):
    if len(message.command) < 3: return await message.reply_text("🌐 Usage: `/translate <lang_code> <text>`\nExample: `/translate hi Hello`")
    lang = message.command[1]
    text = " ".join(message.command[2:])
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target=lang).translate(text)
        await message.reply_text(f"🌐 **Translated ({lang}):**\n{translated}")
    except Exception as e: await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("shorten") & filters.private)
async def shorten(client, message):
    if len(message.command) < 2: return await message.reply_text("🔗 Usage: `/shorten <long_url>`")
    url = message.command[1]
    try:
        import pyshorteners
        s = pyshorteners.Shortener()
        await message.reply_text(f"🔗 **Short URL:** {s.tinyurl.short(url)}")
    except: await message.reply_text("❌ Invalid URL.")

@app.on_message(filters.command("base64") & filters.private)
async def b64(client, message):
    if len(message.command) < 2: return await message.reply_text("🔐 Usage: `/base64 encode|decode <text>`")
    action, text = message.command[1], " ".join(message.command[2:])
    if action == "encode": res = base64.b64encode(text.encode()).decode()
    else: res = base64.b64decode(text.encode()).decode()
    await message.reply_text(f"🔐 **Result:** `{res}`")

@app.on_message(filters.command("whois") & filters.private)
async def whois(client, message):
    if not message.reply_to_message and len(message.command) < 2: return
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    text = f"👤 **Name:** {user.first_name}\n🆔 **ID:** `{user.id}`\n🌐 **Username:** @{user.username}\n🤖 **Bot:** {user.is_bot}"
    await message.reply_text(text)
