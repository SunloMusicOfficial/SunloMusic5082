import os
import asyncio
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from utils.decorators import sudo_only
from database.users import get_total_users, get_all_users
from core.calls import calls

@app.on_message(filters.command("stats"))
@sudo_only
async def stats_handler(client, message):
    users = await get_total_users()
    try: active_vcs = len(await calls.calls)
    except: active_vcs = 0
    await message.reply_text(f"📊 **𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐬**\n\n👥 ᴜꜱᴇʀꜱ: `{users}`\n🎙 ᴀᴄᴛɪᴠᴇ ᴠᴄꜱ: `{active_vcs}`")

@app.on_message(filters.command("broadcast"))
@sudo_only
async def broadcast_handler(client, message):
    if not message.reply_to_message:
        return await message.reply_text("↩️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ.")
    
    m = await message.reply_text("📣 ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...")
    users = await get_all_users()
    success = 0
    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.1)
        except: pass
    await m.edit_text(f"✅ Broadcast sent to `{success}` users.")

@app.on_message(filters.command("clean"))
@sudo_only
async def clean_handler(client, message):
    m = await message.reply_text("🧹 **Cleaning cache...**")
    try:
        for f in os.listdir("cache"):
            if f.endswith((".mp3", ".mp4", ".m4a", ".webp", ".jpg")):
                os.remove(os.path.join("cache", f))
        await m.edit_text("✅ **Cache cleaned successfully!**")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
