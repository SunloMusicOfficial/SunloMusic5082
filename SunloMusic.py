import asyncio
import importlib
import sys
import time
from pathlib import Path

try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

from ftmgram import idle, enums
from ftmgram.errors import FloodWait
from config.settings import settings
from core.bot import app
from core.userbot import userbot
import core.calls as calls_module
from core.database import db
from core.health import health_monitor
from utils.logger import get_logger
from utils.log_cleaner import clear_old_logs
from utils.keep_alive import self_ping
from plugins.queue import current_songs
from utils.player_state import send_now_playing_card, delete_active_card
from pytgcalls.types import Update, StreamEnded

logger = get_logger("SunloMusic")
PLUGINS_DIR = Path("plugins")

def load_plugins():
    loaded = []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"): continue
        module_name = f"plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
            loaded.append(file.stem)
        except Exception as e:
            logger.error(f"❌ Failed to load {file.stem}: {e}")
    return loaded

async def send_log(text):
    if settings.LOG_GROUP_ID != 0:
        try:
            await app.send_message(settings.LOG_GROUP_ID, text, parse_mode=enums.ParseMode.HTML)
        except: pass

async def startup():
    print("""
    ╔══════════════════════════════════════════╗
    ║        🎵  S U N L O   M U S I C  🎵       ║
    ║     Fastest • Lightweight • Premium       ║
    ╚══════════════════════════════════════════╝
    """)
    
    clear_old_logs()
    settings.validate()
    
    logger.info("⏳ Starting Bot & Userbot...")
    try:
        await app.start()
        await userbot.start()
    except FloodWait as e:
        logger.critical(f"🛑 FloodWait: Please wait {e.value} seconds.")
        sys.exit(1)
    
    await db.connect()
    
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    
    # 🔥 STREAM ENDED HANDLER
    @calls_module.calls.on_update()
    async def stream_handler(client, update: Update):
        try:
            if update.status == StreamEnded or str(update.status) == "stream_ended":
                chat_id = update.chat_id
                logger.info(f"🎵 Song ended in {chat_id}.")
                
                from plugins.queue import play_next_in_queue
                try:
                    next_song = await asyncio.wait_for(play_next_in_queue(chat_id), timeout=20)
                    if next_song:
                        await send_now_playing_card(app, chat_id, next_song)
                except Exception as e:
                    logger.error(f"Stream end error: {e}")
        except Exception as e:
            logger.error(f"Update handler error: {e}")
            
    plugins = load_plugins()
    
    asyncio.create_task(health_monitor(app, userbot))
    asyncio.create_task(self_ping(app))
    
    logger.info("🚀 Sunlo Music is ready to rock!")

async def shutdown():
    logger.warning("🛑 Shutting down gracefully...")
    try:
        if calls_module.calls: await calls_module.calls.stop()
        await app.stop()
        await userbot.stop()
        await db.disconnect()
    except: pass
    logger.info("👋 Goodbye!")

async def main():
    try:
        await startup()
        await idle()
    except KeyboardInterrupt:
        pass
    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Fatal startup error: {e}")
        sys.exit(1)
