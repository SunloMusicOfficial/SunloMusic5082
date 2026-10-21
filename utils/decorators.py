import traceback
from functools import wraps
from database.users import add_user
from utils.logger import get_logger
from config.settings import settings
from ftmgram import enums

logger = get_logger("Decorators")

def register_user(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user:
            await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            
            # ── LOG GROUP ERROR SENDING ──
            if settings.LOG_GROUP_ID != 0:
                tb = traceback.format_exc()
                error_msg = (
                    f"🚨 <b>𝐄𝐑𝐑𝐎𝐑 𝐀𝐋𝐄𝐑𝐓</b> 🚨\n\n"
                    f"📝 <b>Command:</b> <code>/{message.command[0] if message.command else 'Unknown'}</code>\n"
                    f"👤 <b>User:</b> {message.from_user.mention if message.from_user else 'Unknown'} (<code>{message.from_user.id if message.from_user else 0}</code>)\n"
                    f"💬 <b>Chat:</b> <code>{message.chat.id}</code>\n\n"
                    f"❌ <b>Error Details:</b>\n<pre>{tb[-3500:]}</pre>"
                )
                try:
                    await client.send_message(settings.LOG_GROUP_ID, error_msg, parse_mode=enums.ParseMode.HTML)
                except Exception as e:
                    logger.error(f"Failed to send error to log group: {e}")

            try:
                await message.reply_text("❌ Kuch gadbad ho gayi. Error log group mein report kar diya gaya hai.")
            except: pass
    return wrapper
