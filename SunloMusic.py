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
from utils.keep_alive import self_ping
from utils.player_state import send_now_playing_card, delete_active_card
from plugins.queue import current_songs

try:
    from pytgcalls.types import Update, StreamEnded
except ImportError:
    from pytgcalls.types import Update
    StreamEnded = "stream_ended"

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
            logger.error(f"❌ Failed to load {file.stem}: {e}")
    return loaded

async def send_log(text):
    if settings.LOG_GROUP_ID != 0:
        try:
            await app.send_message(settings.LOG_GROUP_ID, text, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            logger.error(f"Log group error: {e}")

async def startup():
    print("""
    ╔══════════════════════════════════════════╗
    ║        🎵  S U N L O   M U S I C  🎵       ║
    ║     Fastest • Lightweight • Premium       ║
    ╚══════════════════════════════════════════╝
    """)
    
    settings.validate()
    
    print("⏳ Starting Bot & Userbot...")
    try:
        await app.start()
        await userbot.start()
    except FloodWait as e:
        print(f"🛑 FloodWait: {e.value} seconds.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)
    
    me = await app.get_me()
    user_me = await userbot.get_me()
    
    print("🗄️ Connecting to Database...")
    try:
        await db.connect()
    except Exception as e:
        print(f"❌ Database failed: {e}")
        sys.exit(1)
    
    print("📞 Starting Voice Engine...")
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    
    @calls_module.calls.on_update()
    async def stream_handler(client, update: Update):
        try:
            if update.status == StreamEnded or str(update.status) == "stream_ended":
                chat_id = update.chat_id
                print(f"🎵 Song ended in {chat_id}. Checking queue...")
                
                from plugins.queue import play_next_in_queue
                try:
                    next_song = await asyncio.wait_for(play_next_in_queue(chat_id), timeout=20)
                    if next_song:
                        await send_now_playing_card(app, chat_id, next_song)
                except Exception as e:
                    print(f"Stream end error: {e}")
                    try: await calls_module.calls.leave_call(chat_id)
                    except: pass
                    await delete_active_card(chat_id)
        except Exception as e:
            print(f"Update handler error: {e}")
            
    print("🔌 Loading Plugins...")
    plugins = load_plugins()
    print(f"✅ {len(plugins)} Plugins Loaded.")
    
    asyncio.create_task(health_monitor(app, userbot))
    asyncio.create_task(self_ping(app))
    
    # 🔥 RESTORED START MESSAGES
    await send_log(f"🤖 <b>𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n👤 <b>Name:</b> {user_me.first_name}\n🆔 <b>ID:</b> <code>{user_me.id}</code>")
    await send_log(f"🚀 <b>𝐒𝐔𝐍𝐋𝐎 𝐌𝐔𝐒𝐈𝐂 𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n🤖 <b>Bot:</b> @{me.username}\n⚙️ <b>Plugins:</b> <code>{len(plugins)} Loaded</code>")
    
    print("🚀 Sunlo Music is ready to rock!")

async def shutdown():
    print("🛑 Shutting down gracefully...")
    try:
        if calls_module.calls: await calls_module.calls.stop()
        await app.stop()
        await userbot.stop()
        await db.disconnect()
    except: pass
    print("👋 Goodbye!")

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
