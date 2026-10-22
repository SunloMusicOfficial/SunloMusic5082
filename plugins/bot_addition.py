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
                # Check if bot is admin
                bot_member = await client.get_chat_member(message.chat.id, me.id)
                if bot_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    userbot_me = await userbot.get_me()
                    
                    # 🔥 FIX: Check if Assistant is already there
                    try:
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                        logger.info("Assistant already in group.")
                    except Exception as e:
                        if "USER_NOT_PARTICIPANT" in str(e) or "NOT_FOUND" in str(e):
                            # Assistant is not in group, try to add
                            try:
                                await client.add_chat_members(message.chat.id, userbot_me.id)
                                logger.info(f"✅ Assistant added to {message.chat.id}")
                                await message.reply_text("🤖 **Assistant account added successfully!**")
                            except Exception as add_err:
                                logger.warning(f"⚠️ Could not auto-invite Assistant: {add_err}")
                                await message.reply_text(
                                    f"⚠️ **Could not auto-invite Assistant.**\n"
                                    f"Please add `@{userbot_me.username}` manually to the group.\n\n"
                                    f"<b>Reason:</b> <code>{add_err}</code>",
                                    parse_mode=enums.ParseMode.HTML
                                )
            except Exception as e:
                logger.warning(f"⚠️ BotAddition error: {e}")
