import asyncio
import importlib
import sys
from pathlib import Path

from ftmgram import idle
from config.settings import settings
from core.bot import create_bot, app as global_app
from core.userbot import create_userbot, userbot as global_userbot
from core.calls import create_calls, calls as global_calls
from core.database import db
from core.health import health_monitor
from utils.logger import get_logger
from utils.log_cleaner import clear_old_logs

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

async def startup(app, userbot, calls):
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
    
    await calls.start()
    logger.info("📞 PyTgCalls voice engine started")
    
    plugins = load_plugins()
    logger.info(f"🔌 {len(plugins)} plugins loaded successfully")
    
    asyncio.create_task(health_monitor(calls, app, userbot))
    logger.info("💚 Health monitor is now active")
    logger.info("🚀 Sunlo Music is ready to rock!")

async def shutdown(app, userbot, calls):
    logger.warning("🛑 Shutting down gracefully...")
    try:
        await calls.stop()
        await app.stop()
        await userbot.stop()
        await db.disconnect()
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    logger.info("👋 Goodbye!")

async def main():
    # Initialize all clients inside the event loop
    app = create_bot()
    userbot = create_userbot()
    calls = create_calls(userbot)
    
    try:
        await startup(app, userbot, calls)
        await idle()
    except KeyboardInterrupt:
        pass
    finally:
        await shutdown(app, userbot, calls)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Fatal startup error: {e}")
        sys.exit(1)
