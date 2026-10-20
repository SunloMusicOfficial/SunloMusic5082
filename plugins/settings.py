from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user
from database.chats import set_chat_setting
from config.settings import settings

@app.on_message(filters.command("setwelcome") & filters.group)
@register_user
async def setwelcome_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("👋 **Usage:** `/setwelcome <text>`")
    await set_chat_setting(message.chat.id, "welcome", message.text.split(None, 1)[1])
    await message.reply_text("✅ Welcome message set!")

@app.on_message(filters.command("setgoodbye") & filters.group)
@register_user
async def setgoodbye_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("👋 **Usage:** `/setgoodbye <text>`")
    await set_chat_setting(message.chat.id, "goodbye", message.text.split(None, 1)[1])
    await message.reply_text("✅ Goodbye message set!")

@app.on_message(filters.command("setlog") & filters.user(settings.OWNER_ID))
async def setlog_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("⚙️ **Usage:** `/setlog <channel_id>`")
    try:
        log_id = int(message.command[1])
        await set_chat_setting(message.chat.id, "log_channel", log_id)
        await message.reply_text("✅ Log channel set!")
    except: await message.reply_text("❌ Invalid ID.")
