from ftmgram import filters, enums
from core.bot import app
from core.userbot import userbot
from utils.logger import get_logger

logger = get_logger("BotAddition")

@app.on_message(filters.new_chat_members)
async def welcome_and_invite(client, message):
    me = await client.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            try:
                bot_member = await client.get_chat_member(message.chat.id, me.id)
                if bot_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    userbot_me = await userbot.get_me()
                    
                    try:
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                    except:
                        # 🔥 FIX: Force DM to assistant
                        try:
                            await client.send_message(userbot_me.id, "/start")
                        except: pass
                        
                        try:
                            await client.add_chat_members(message.chat.id, userbot_me.id)
                            await message.reply_text("🤖 **Assistant account added successfully!**")
                        except Exception as e:
                            await message.reply_text(
                                f"⚠️ **Auto-invite failed.**\n"
                                f"Please add `@{userbot_me.username}` manually.\n\n"
                                f"<b>Reason:</b> <code>{e}</code>",
                                parse_mode=enums.ParseMode.HTML
                            )
            except Exception as e:
                logger.warning(f"BotAddition error: {e}")
