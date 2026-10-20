import os, importlib, asyncio, psutil, time, platform
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from database.users import get_total_users, add_gban, remove_gban, get_all_users

START_TIME = time.time()

@app.on_message(filters.command("ping"))
async def ping_handler(client, message):
    start = time.time()
    m = await message.reply_text("🏓 **Pinging...**")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await m.edit_text(f"🚀 **Pong!**\n⚡ **Latency:** `{latency} ms`")

@app.on_message(filters.command("uptime"))
async def uptime_handler(client, message):
    uptime_sec = int(time.time() - START_TIME)
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_sec))
    await message.reply_text(f"⏱ **Bot Uptime:** `{uptime_str}`")

@app.on_message(filters.command("id"))
async def id_handler(client, message):
    text = f"👤 **User ID:** `{message.from_user.id}`\n💬 **Chat ID:** `{message.chat.id}`"
    if message.reply_to_message:
        text += f"\n↩️ **Replied User ID:** `{message.reply_to_message.from_user.id}`"
    await message.reply_text(text)

@app.on_message(filters.command("stats") & filters.user(settings.OWNER_ID))
async def stats_handler(client, message):
    users = await get_total_users()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    await message.reply_text(f"📊 **Bot Stats**\n\n👥 **Users:** `{users}`\n💻 **CPU:** `{cpu}%`\n🧠 **RAM:** `{ram}%`")

@app.on_message(filters.command("clean") & filters.user(settings.OWNER_ID))
async def clean_handler(client, message):
    m = await message.reply_text("🧹 **Cleaning cache...**")
    try:
        for f in os.listdir("cache"):
            if f.endswith(".mp3") or f.endswith(".mp4") or f.endswith(".webp") or f.endswith(".jpg"):
                os.remove(os.path.join("cache", f))
        await m.edit_text("✅ **Cache cleaned successfully!**")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("gban") & filters.user(settings.OWNER_ID))
async def gban_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user.")
    await add_gban(message.reply_to_message.from_user.id)
    await message.reply_text("🚫 User globally banned.")

@app.on_message(filters.command("ungban") & filters.user(settings.OWNER_ID))
async def ungban_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user.")
    await remove_gban(message.reply_to_message.from_user.id)
    await message.reply_text("✅ User unbanned.")

@app.on_message(filters.command("broadcast") & filters.user(settings.OWNER_ID))
async def broadcast_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a message.")
    users = await get_all_users()
    m = await message.reply_text("📣 Broadcasting...")
    success = 0
    for user in users:
        try:
            await message.reply_to_message.copy(user["user_id"])
            success += 1
            await asyncio.sleep(0.1)
        except: pass
    await m.edit_text(f"✅ Broadcast sent to `{success}` users.")

@app.on_message(filters.command("reload") & filters.user(settings.OWNER_ID))
async def reload_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("⚙️ **Usage:** `/reload <plugin>`")
    plugin = message.command[1].replace(".py", "")
    try:
        module = importlib.import_module(f"plugins.{plugin}")
        importlib.reload(module)
        await message.reply_text(f"✅ Plugin `{plugin}` reloaded!")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@app.on_message(filters.command("tagall") & filters.group)
async def tagall_handler(client, message):
    if not message.from_user: return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else "Hello everyone!"
    tags = []
    async for m in client.get_chat_members(message.chat.id):
        if not m.user.is_bot: tags.append(m.user.mention)
    await message.reply_text(f"{text}\n\n" + " ".join(tags))

@app.on_message(filters.command("kick") & filters.group)
async def kick_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user.")
    try:
        await client.ban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await client.unban_chat_member(message.chat.id, message.reply_to_message.from_user.id)
        await message.reply_text("👢 User kicked!")
    except: await message.reply_text("❌ Failed. Make sure I am admin.")

@app.on_message(filters.command("purge") & filters.group)
async def purge_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to start purge.")
    await message.delete()
    msg_ids = list(range(message.reply_to_message.id, message.id))
    await client.delete_messages(message.chat.id, msg_ids)
