from ftmgram import filters
from core.bot import app
import core.calls as calls_module
from utils.logger import get_logger

logger = get_logger("KickedWatcher")

@app.on_message(filters.left_chat_member)
async def bot_kicked_handler(client, message):
    if message.left_chat_member.id == (await client.get_me()).id:
        chat_id = message.chat.id
        logger.warning(f"⚠️ Bot was kicked from {chat_id}. Clearing VC state.")
        try:
            await calls_module.calls.leave_call(chat_id)
        except: pass
        from plugins.queue import current_songs, chat_states
        current_songs.pop(chat_id, None)
        chat_states.pop(chat_id, None)
