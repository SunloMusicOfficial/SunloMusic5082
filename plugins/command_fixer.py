from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("CommandFixer")

@app.on_message(filters.group & filters.text & filters.regex(r"^/[a-zA-Z0-9_]+@" + settings.BOT_USERNAME.replace("@", "") + r"(?:\s|$)"))
async def fix_tagged_commands(client, message):
    """Handles /command@BotName and converts it to a normal /command."""
    try:
        bot_username = settings.BOT_USERNAME.replace("@", "")
        new_text = message.text.replace(f"@{bot_username}", "").strip()
        
        # Modify the message object
        message.text = new_text
        message.command = new_text.split()
        
        # Reprint the message so other handlers can catch it
        await message.copy(chat_id=message.chat.id)
        
        # Delete the original message to avoid double processing
        try:
            await message.delete()
        except:
            pass
    except Exception as e:
        logger.error(f"Command fixer error: {e}")
