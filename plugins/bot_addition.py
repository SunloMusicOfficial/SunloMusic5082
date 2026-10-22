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
                # 1. Check if bot is admin
                bot_member = await client.get_chat_member(message.chat.id, me.id)
                if bot_member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
                    userbot_me = await userbot.get_me()
                    
                    # 2. 🔥 FIX: Send a DM to Assistant first to make Peer ID valid
                    try:
                        await client.send_message(userbot_me.id, "/start")
                    except: pass
                    
                    # 3. Check if Assistant is already in group
                    try:
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                        logger.info("Assistant already in group.")
                    except:
                        # 4. Invite Assistant
                        await client.add_chat_members(message.chat.id, userbot_me.id)
                        logger.info(f"✅ Assistant added to {message.chat.id}")
                        await message.reply_text("🤖 **Assistant account added successfully!**")
            except Exception as e:
                logger.warning(f"⚠️ Could not auto-invite Assistant: {e}")
