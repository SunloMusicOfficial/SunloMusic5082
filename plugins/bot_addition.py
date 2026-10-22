from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from core.userbot import userbot
from config.settings import settings
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
                    
                    try:
                        # Check if Assistant is already there
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                    except:
                        # 🔥 FIX: Bade bots wala tarika (Force DM to make Peer valid)
                        try:
                            # Assistant ko DM bhejo taaki woh "Active" ho jaye
                            await client.send_message(userbot_me.id, "System Check")
                        except: pass
                        
                        try:
                            # Ab add karo
                            await client.add_chat_members(message.chat.id, userbot_me.id)
                            await message.reply_text("🤖 **Assistant account added successfully!**")
                        except Exception as e:
                            # Agar Telegram ne block kiya, toh direct button de do
                            add_link = f"https://t.me/{userbot_me.username}?startgroup=true"
                            buttons = InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Assistant Manually", url=add_link)]])
                            
                            await message.reply_text(
                                f"⚠️ **Auto-invite blocked by Telegram.**\n\n"
                                f"Please tap the button below to add `@{userbot_me.username}` to the group.",
                                reply_markup=buttons
                            )
            except Exception as e:
                logger.warning(f"BotAddition error: {e}")
