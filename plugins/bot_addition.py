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
                    
                    # Check if Assistant is already in group
                    try:
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                        logger.info("Assistant already in group.")
                    except:
                        # Invite Assistant
                        await client.add_chat_members(message.chat.id, userbot_me.id)
                        logger.info(f"✅ Assistant added to {message.chat.id}")
                        await message.reply_text("🤖 **Assistant account added successfully!**")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-invite Assistant: {e}")
