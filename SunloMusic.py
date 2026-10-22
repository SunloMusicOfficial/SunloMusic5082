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

def load_plugins():
    loaded = []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"): continue
        module_name = f"plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
            loaded.append(file.stem)
        except Exception as e:
            print(f"❌ Failed to load {file.stem}: {e}")
    return loaded

async def send_log(text):
    if settings.LOG_GROUP_ID != 0:
        try: await app.send_message(settings.LOG_GROUP_ID, text, parse_mode=enums.ParseMode.HTML)
        except: pass

async def startup():
    print("""
    ╔══════════════════════════════════════════╗
    ║        🎵  S U N L O   M U S I C  🎵       ║
    ║     Fastest • Lightweight • Premium       ║
    ╚══════════════════════════════════════════╝
    """)
    settings.validate()
    await app.start()
    await userbot.start()
    await db.connect()
    
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    
    @calls_module.calls.on_update()
    async def stream_handler(client, update: Update):
        try:
            if isinstance(update, StreamEnded):
                # 🔥 FIX: Direct update.chat_id
                chat_id = update.chat_id
                print(f"🎵 Song ended in {chat_id}. Checking queue...")
                
                try:
                    next_song = await asyncio.wait_for(play_next_in_queue(chat_id), timeout=15)
                    if next_song:
                        await send_now_playing_card(app, chat_id, next_song)
                    else:
                        await calls_module.calls.leave_call(chat_id)
                        await delete_active_card(chat_id)
                        print(f"🚪 Auto left VC in {chat_id}")
                except Exception as e:
                    print(f"Queue error: {e}")
                    try: await calls_module.calls.leave_call(chat_id)
                    except: pass
                    await delete_active_card(chat_id)
        except Exception as e:
            print(f"Update handler error: {e}")
            
    plugins = load_plugins()
    print(f"✅ {len(plugins)} Plugins Loaded.")
    asyncio.create_task(self_ping(app))
    
    me = await app.get_me()
    user_me = await userbot.get_me()
    await send_log(f"🤖 <b>𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n👤 <b>Name:</b> {user_me.first_name}")
    await send_log(f"🚀 <b>𝐒𝐔𝐍𝐋𝐎 𝐌𝐔𝐒𝐈𝐂 𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n🤖 <b>Bot:</b> @{me.username}")
    print("🚀 Sunlo Music is ready to rock!")

async def shutdown():
    try:
        if calls_module.calls: await calls_module.calls.stop()
        await app.stop()
        await userbot.stop()
        await db.disconnect()
    except: pass

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
        print(f"Fatal startup error: {e}")
        sys.exit(1)
