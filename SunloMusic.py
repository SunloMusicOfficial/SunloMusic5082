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
from config.settings import settings
from core.bot import app
from core.userbot import userbot
import core.calls as calls_module
from core.database import db
from core.health import health_monitor
from utils.logger import get_logger
from utils.log_cleaner import clear_old_logs
from plugins.queue import current_songs

logger = get_logger("SunloMusic")
PLUGINS_DIR = Path("plugins")
START_TIME = time.time()

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
        except Exception as e:
            logger.error(f"Log group error: {e}")

async def auto_leave_vc():
    while True:
        await asyncio.sleep(60)
        try:
            active_calls = await calls_module.calls.calls
            for chat_id in list(active_calls.keys()):
                if chat_id not in current_songs:
                    await calls_module.calls.leave_call(chat_id)
                    logger.info(f"🚪 Auto-Left VC in {chat_id} (Inactive)")
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
    # Pehle Bot aur Userbot Start karo taaki Log Group kaam kare
    await app.start()
    await userbot.start()
    
    me = await app.get_me()
    user_me = await userbot.get_me()
    
    logger.info("🗄️ Connecting to Database...")
    try:
        await db.connect()
    except Exception as e:
        error_msg = f"❌ <b>Database Connection Failed!</b>\n\n<code>{e}</code>\n\n<i>Please check your MONGO_URI in Environment Variables.</i>"
        await send_log(error_msg)
        logger.critical(f"Fatal: Database failed. Exiting...")
        sys.exit(1) # Exit if DB fails
    
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    
    logger.info("⏳ Loading Plugins...")
    plugins = load_plugins()
    
    asyncio.create_task(health_monitor(app, userbot))
    asyncio.create_task(auto_leave_vc())
    
    await send_log(
        f"🤖 <b>𝐀𝐒𝐒𝐈𝐒𝐓𝐀𝐍𝐓 𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Name:</b> {user_me.first_name}\n"
        f"🆔 <b>ID:</b> <code>{user_me.id}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    await send_log(
        f"🚀 <b>𝐒𝐔𝐍𝐋𝐎 𝐌𝐔𝐒𝐈𝐂 𝐁𝐎𝐓 𝐒𝐓𝐀𝐑𝐓𝐄𝐃</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Bot:</b> @{me.username}\n"
        f"⚙️ <b>Plugins:</b> <code>{len(plugins)} Loaded</code>\n"
        f"🗄 <b>Database:</b> <code>Connected</code>\n"
        f"🎙 <b>Voice Engine:</b> <code>Active</code>\n"
        f"⚡ <b>Status:</b> <code>Online & Fast</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    logger.info("🚀 Sunlo Music is ready to rock!")

async def shutdown():
    logger.warning("🛑 Shutting down gracefully...")
    await send_log("🛑 <b>Bot is shutting down...</b>")
    try:
        if calls_module.calls:
            await calls_module.calls.stop()
        await app.stop()
        await userbot.stop()
        await db.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
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
