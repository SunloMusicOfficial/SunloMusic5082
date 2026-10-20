from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user
from database.chats import get_chat_setting, set_chat_setting

warns_db = {}
locked_chats = set()

@app.on_message(filters.command("lock") & filters.group)
async def lock_handler(client, message):
    if not message.from_user: return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return
    locked_chats.add(message.chat.id)
    await message.reply_text("🔒 Group locked. Only admins can message.")

@app.on_message(filters.command("unlock") & filters.group)
async def unlock_handler(client, message):
    if not message.from_user: return
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]: return
    locked_chats.discard(message.chat.id)
    await message.reply_text("🔓 Group unlocked.")

@app.on_message(filters.group & ~filters.service, group=3)
async def lock_watcher(client, message):
    if message.chat.id in locked_chats and message.from_user:
        member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if member.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            await message.delete()

@app.on_message(filters.command("warn") & filters.group)
@register_user
async def warn_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user to warn.")
    user_id = message.reply_to_message.from_user.id
    if user_id not in warns_db: warns_db[user_id] = 0
    warns_db[user_id] += 1
    if warns_db[user_id] >= 3:
        await client.ban_chat_member(message.chat.id, user_id)
        await message.reply_text("🚫 User banned after 3 warnings.")
        warns_db[user_id] = 0
    else:
        await message.reply_text(f"⚠️ Warning {warns_db[user_id]}/3 for {message.reply_to_message.from_user.mention}")

@app.on_message(filters.command("resetwarn") & filters.group)
@register_user
async def resetwarn(client, message):
    if not message.reply_to_message: return
    warns_db[message.reply_to_message.from_user.id] = 0
    await message.reply_text("✅ Warnings reset.")
