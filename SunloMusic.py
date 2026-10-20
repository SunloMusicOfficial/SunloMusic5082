import asyncio
import importlib
import sys
import time
from pathlib import Path

from ftmgram import idle
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

async def auto_leave_vc():
    """Leaves VC if no song has been playing for 5 minutes."""
    while True:
        await asyncio.sleep(60) # Check every minute
        try:
            active_calls = await calls_module.calls.calls
            for chat_id in list(active_calls.keys()):
                # If no current song info exists or it's older than 5 mins (dummy check)
                if chat_id not in current_songs:
                    await calls_module.calls.leave_call(chat_id)
                    logger.info(f"🚪 Auto-Left VC in {chat_id} (Inactive)")
        except Exception:
            pass

async def startup():
    print("""
    ╔══════════════════════════════════════════╗
    ║        🎵  S U N L O   M U S I C  🎵       ║
    ║     Fastest • Lightweight • Premium       ║
    ╚══════════════════════════════════════════╝
    """)
    
    clear_old_logs()
    settings.validate()
    
    await userbot.start()
    logger.info("🤖 Assistant Userbot started")
    
    await app.start()
    me = await app.get_me()
    logger.info(f"✅ Bot started as @{me.username}")
    
    await db.connect()
    logger.info("🗄️ Database connected successfully")
    
    from pytgcalls import PyTgCalls
    calls_module.calls = PyTgCalls(userbot)
    await calls_module.calls.start()
    logger.info("📞 PyTgCalls voice engine started")
    
    # Setup VC Watcher
    from plugins.vc_watcher import setup_vc_watcher
    await setup_vc_watcher()

    plugins = load_plugins()
    logger.info(f"🔌 {len(plugins)} plugins loaded successfully")
    
    asyncio.create_task(health_monitor(app, userbot))
    asyncio.create_task(auto_leave_vc())
    logger.info("💚 Health monitor & Auto-Leave active")
    logger.info("🚀 Sunlo Music is ready to rock!")

async def shutdown():
    logger.warning("🛑 Shutting down gracefully...")
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
