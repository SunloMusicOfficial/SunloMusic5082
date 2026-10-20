from functools import wraps
from database.users import add_user
from utils.logger import get_logger

logger = get_logger("Decorators")

def register_user(func):
    """Har command se pehle user ko DB mein save karta hai."""
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        if message.from_user:
            await add_user(
                user_id=message.from_user.id,
                first_name=message.from_user.first_name,
                username=message.from_user.username
            )
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            await message.reply_text("❌ Kuch gadbad ho gayi. Dobara try karein.")
    return wrapper
