import traceback
from functools import wraps
from ftmgram import enums
from database.users import add_user
from database.sudo import is_sudo, get_sudo_users
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Decorators")

def register_user(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user:
            try: await add_user(message.from_user.id, message.from_user.first_name, message.from_user.username)
            except: pass
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            if settings.LOG_GROUP_ID != 0:
                tb = traceback.format_exc()
                try: await client.send_message(settings.LOG_GROUP_ID, f"🚨 Error in {func.__name__}:\n<pre>{tb[-3000:]}</pre>", parse_mode=enums.ParseMode.HTML)
                except: pass
            try: await message.reply_text("❌ Error aagya bhai, log group check karein.")
            except: pass
    return wrapper

def sudo_only(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if not message.from_user: return
        user_id = message.from_user.id
        
        # Check if Owner
        if user_id == settings.OWNER_ID:
            return await func(client, message, *args, **kwargs)
            
        # Check Cloud Sudo Database
        db_sudo = await is_sudo(user_id)
        
        # Check Env Sudo (Backward compatibility)
        env_sudo = user_id in settings.SUDO_USERS
        
        if not (db_sudo or env_sudo):
            return await message.reply_text("🚫 **Access Denied!** Yeh command sirf Owner aur Sudo users ke liye hai.")
            
        return await func(client, message, *args, **kwargs)
    return wrapper
