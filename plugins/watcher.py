from ftmgram import filters, enums
from core.bot import app
from database.chats import get_chat_setting
from database.users import get_afk, remove_afk, set_afk

@app.on_message(filters.new_chat_members)
async def welcome_new(client, message):
    welcome_text = await get_chat_setting(message.chat.id, "welcome")
    if welcome_text:
        await message.reply_text(welcome_text)

@app.on_message(filters.left_chat_member)
async def goodbye_member(client, message):
    goodbye_text = await get_chat_setting(message.chat.id, "goodbye")
    if goodbye_text:
        await message.reply_text(goodbye_text)

@app.on_message(filters.text & filters.group & ~filters.bot, group=2)
async def afk_watcher(client, message):
    if not message.from_user: return
    # Check if user who sent msg is AFK
    afk_reason = await get_afk(message.from_user.id)
    if afk_reason:
        await remove_afk(message.from_user.id)
        await message.reply_text(f"👋 Welcome back {message.from_user.mention}!\n_Aapka AFK hata diya gaya hai._")

    # Check if replied user is AFK
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_afk = await get_afk(message.reply_to_message.from_user.id)
        if replied_afk:
            await message.reply_text(f"💤 **{message.reply_to_message.from_user.first_name}** is AFK.\n📝 **Reason:** {replied_afk}")

@app.on_message(filters.command("afk") & filters.group)
async def afk_handler(client, message):
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason provided."
    await set_afk(message.from_user.id, reason)
    await message.reply_text(f"💤 **{message.from_user.first_name}** is now AFK.\n📝 **Reason:** {reason}")
