from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from database.sudo import add_sudo, remove_sudo, get_sudo_users

@app.on_message(filters.command("addsudo") & filters.user(settings.OWNER_ID))
async def addsudo_handler(client, message):
    target_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try: target_id = int(message.command[1])
        except: pass
        
    if not target_id:
        return await message.reply_text("↩️ Kisi user ko reply karo ya ID do.\nExample: `/addsudo 12345678`")
        
    await add_sudo(target_id)
    await message.reply_text(f"✅ User `{target_id}` added to Sudo list in Database!")

@app.on_message(filters.command("delsudo") & filters.user(settings.OWNER_ID))
async def delsudo_handler(client, message):
    target_id = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target_id = message.reply_to_message.from_user.id
    elif len(message.command) > 1:
        try: target_id = int(message.command[1])
        except: pass
        
    if not target_id:
        return await message.reply_text("↩️ Kisi user ko reply karo ya ID do.")
        
    await remove_sudo(target_id)
    await message.reply_text(f"❌ User `{target_id}` removed from Sudo list!")

@app.on_message(filters.command("sudolist"))
async def sudolist_handler(client, message):
    users = await get_sudo_users()
    if not users:
        return await message.reply_text("📭 Sudo list is empty.")
        
    text = "👑 **Sudo Users List:**\n\n"
    for uid in users:
        text += f"▸ `{uid}`\n"
    await message.reply_text(text)
