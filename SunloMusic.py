# ... (imports same rahenge)
import asyncio
import importlib
import sys
from pathlib import Path
from ftmgram import idle, enums
from pytgcalls.types import Update, StreamEnded
from config.settings import settings
from core.bot import app
from core.userbot import userbot
import core.calls as calls_module
from core.database import db
from utils.logger import get_logger
from utils.keep_alive import self_ping
from utils.player_state import send_now_playing_card, delete_active_card
from plugins.queue import current_songs, play_next_in_queue

logger = get_logger("SunloMusic")
PLUGINS_DIR = Path("plugins")

# ... (load_plugins function same)

async def startup():
    # ... (startup code same)
    await app.start()
    await userbot.start()
    await db.connect()
    
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    
    @calls_module.calls.on_update()
    async def stream_handler(client, update: Update):
        try:
            # 🔥 CHECK FOR STREAM END
            if update.status == StreamEnded or str(update.status) == "stream_ended":
                chat_id = update.chat_id
                logger.info(f"🎵 Song ended in {chat_id}. Checking queue...")
                
                try:
                    next_song = await asyncio.wait_for(play_next_in_queue(chat_id), timeout=15)
                    if next_song:
                        await send_now_playing_card(app, chat_id, next_song)
                    else:
                        # Queue is empty, force leave
                        await calls_module.calls.leave_call(chat_id)
                        await delete_active_card(chat_id)
                        logger.info(f"🚪 Auto left VC in {chat_id}")
                except Exception as e:
                    logger.error(f"Queue empty or error: {e}")
                    try: await calls_module.calls.leave_call(chat_id)
                    except: pass
                    await delete_active_card(chat_id)
        except Exception as e:
            logger.error(f"Stream handler error: {e}")
            
    plugins = load_plugins()
    asyncio.create_task(self_ping(app))
    logger.info("🚀 Sunlo Music is ready to rock!")

# ... (rest of the file same)
