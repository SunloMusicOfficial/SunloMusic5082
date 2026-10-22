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
                    
                    try:
                        # Check if Assistant is already there
                        await client.get_chat_member(message.chat.id, userbot_me.id)
                        logger.info("Assistant already in group.")
                        continue
                    except:
                        pass # Assistant is not in group, proceed to add
                    
                    # 2. 🔥 FIX: Try Direct Add first
                    added = False
                    try:
                        await client.add_chat_members(message.chat.id, userbot_me.id)
                        added = True
                        logger.info(f"✅ Assistant added directly to {message.chat.id}")
                        await message.reply_text("🤖 **Assistant account added successfully!**")
                    except Exception as direct_err:
                        logger.warning(f"⚠️ Direct add failed: {direct_err}. Trying invite link method...")
                        
                        # 3. 🔥 FIX: If direct add fails, use Invite Link method
                        try:
                            # Generate invite link
                            invite_link = await client.export_chat_invite_link(message.chat.id)
                            
                            # Assistant joins via link
                            await userbot.join_chat(invite_link)
                            
                            added = True
                            logger.info(f"✅ Assistant joined via invite link in {message.chat.id}")
                            await message.reply_text("🤖 **Assistant account joined successfully via invite link!**")
                            
                        except Exception as link_err:
                            logger.error(f"❌ Invite link method also failed: {link_err}")
                            
                            # 4. Last Resort: Give manual link to user
                            await message.reply_text(
                                f"⚠️ **Auto-join failed.**\n\n"
                                f"Please add `@{userbot_me.username}` manually to the group.\n\n"
                                f"<b>Reason:</b> <code>{link_err}</code>",
                                parse_mode=enums.ParseMode.HTML
                            )
                    
            except Exception as e:
                logger.warning(f"⚠️ BotAddition error: {e}")
