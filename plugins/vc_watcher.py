import asyncio
from pytgcalls.types import Update
from utils.logger import get_logger
import core.calls as calls_module
from plugins.queue import current_songs
from utils.player_state import chat_states, playback_start_times, live_timer_tasks

logger = get_logger("VCWatcher")

async def setup_vc_watcher():
    if not calls_module.calls: return
    
    @calls_module.calls.on_update()
    async def on_update(client, update: Update):
        if update.status == "closed_voice_chat":
            chat_id = update.chat_id
            logger.info(f"🚪 Admin closed VC in {chat_id}. Clearing state.")
            current_songs.pop(chat_id, None)
            chat_states.pop(chat_id, None)
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks:
                live_timer_tasks[chat_id].cancel()
