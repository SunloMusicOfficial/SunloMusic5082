from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from core.userbot import userbot
from utils.logger import get_logger

logger = get_logger("CallsEngine")

# PyTgCalls Instance (v2.x)
calls = PyTgCalls(userbot)

@calls.on_update()
async def stream_handler(client, update: Update):
    """Auto-play next song when current ends (Gapless playback)"""
    try:
        if update.status == "stream_ended":
            # Queue logic will be added in plugins/play.py
            from plugins.queue import play_next_in_queue
            await play_next_in_queue(update.chat_id)
    except Exception as e:
        logger.error(f"Stream handler error: {e}")
