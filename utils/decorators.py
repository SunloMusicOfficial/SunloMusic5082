import traceback
from functools import wraps
from ftmgram import enums
from database.users import add_user
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Decorators")

def register_user(func):
    """Har command se pehle user ko DB mein save karta hai aur errors ko Log Group me bhejta hai."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        # 1. Register User in Database
        if message.from_user:
            try:
                await add_user(
                    message.from_user.id, 
                    message.from_user.first_name, 
                    message.from_user.username
                )
            except Exception as e:
                logger.error(f"Failed to add user to DB: {e}")

        # 2. Execute Command
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            
            # 3. Send Error to Log Group (Premium Alert)
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
                except Exception as log_e:
                    logger.error(f"Failed to send error to log group: {log_e}")

            # 4. Reply to user safely
            try:
                await message.reply_text("❌ Kuch gadbad ho gayi. Error log group mein report kar diya gaya hai.")
            except:
                pass
    return wrapper

def sudo_only(func):
    """Sirf Owner aur Sudo Users ke liye commands allow karta hai."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if not message.from_user:
            return
            
        user_id = message.from_user.id
        if user_id != settings.OWNER_ID and user_id not in settings.SUDO_USERS:
            return await message.reply_text("🚫 **Access Denied!** Yeh command sirf Owner aur Sudo users ke liye hai.")
            
        return await func(client, message, *args, **kwargs)
    return wrapper

def owner_only(func):
    """Sirf Bot Owner ke liye commands allow karta hai."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if not message.from_user:
            return
            
        if message.from_user.id != settings.OWNER_ID:
            return await message.reply_text("🚫 **Access Denied!** Yeh command sirf Bot Owner ke liye hai.")
            
        return await func(client, message, *args, **kwargs)
    return wrapper
