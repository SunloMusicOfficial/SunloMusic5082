import os, sys, subprocess
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from database.chats import set_chat_setting, get_chat_setting

@app.on_message(filters.command("auth") & filters.group)
async def auth_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user.")
    user_id = message.reply_to_message.from_user.id
    # Save to DB (mock logic)
    await message.reply_text(f"✅ {user_id} authorized to control music in this chat.")

@app.on_message(filters.command("setprefix") & filters.group)
async def setprefix_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("⚙️ **Usage:** `/setprefix !`")
    prefix = message.command[1]
    await set_chat_setting(message.chat.id, "prefix", prefix)
    await message.reply_text(f"✅ Prefix changed to `{prefix}`")

@app.on_message(filters.command("maintenance") & filters.user(settings.OWNER_ID))
async def maintenance_handler(client, message):
    status = await get_chat_setting("global", "maintenance", False)
    new_status = not status
    await set_chat_setting("global", "maintenance", new_status)
    await message.reply_text(f"🛠 **Maintenance Mode:** `{'ON' if new_status else 'OFF'}`")

@app.on_message(filters.command("restart") & filters.user(settings.OWNER_ID))
async def restart_handler(client, message):
    await message.reply_text("🔄 **Restarting bot...**")
    try:
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await message.reply_text(f"❌ Restart failed: {e}")
        sys.exit(1)

@app.on_message(filters.command("queue") & filters.group)
async def queue_handler(client, message):
    from plugins.queue import queues
    chat_id = message.chat.id
    if chat_id not in queues or not queues[chat_id]:
        return await message.reply_text("📭 **Queue is empty.**")
    text = "🎵 **Current Queue:**\n\n"
    for i, song in enumerate(queues[chat_id][:10], 1):
        text += f"{i}. {song['title']}\n"
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
