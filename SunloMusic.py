import asyncio
import importlib
import sys
from pathlib import Path

from ftmgram import idle
from config.settings import settings
from core.bot import app
from core.userbot import userbot
from core.calls import calls
from core.database import db
from core.health import health_monitor
from utils.logger import get_logger
from utils.log_cleaner import clear_old_logs

logger = get_logger("SunloMusic")
PLUGINS_DIR = Path("plugins")

def load_plugins():
    """Automatically load all plugins from the plugins directory."""
    loaded = []
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        if file.name.startswith("_"): 
            continue
        module_name = f"plugins.{file.stem}"
        try:
            importlib.import_module(module_name)
            loaded.append(file.stem)
        except Exception as e:
            logger.error(f"❌ Failed to load {file.stem}: {e}")
    return loaded

async def startup():
    print("""
    ╔══════════════════════════════════════════╗
    ║        🎵  S U N L O   M U S I C  🎵       ║
    ║     Fastest • Lightweight • Premium       ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Clear old logs if they are too big
    clear_old_logs()
    
    # Validate environment variables
    settings.validate()
    
    # Start Assistant Userbot (For Voice Chat)
    await userbot.start()
    logger.info("🤖 Assistant Userbot started")
    
    # Start Main Bot
    await app.start()
    me = await app.get_me()
    logger.info(f"✅ Bot started as @{me.username}")
    
    # Connect to MongoDB Database
    await db.connect()
    logger.info("🗄️ Database connected successfully")
    
    # Start PyTgCalls Engine
    await calls.start()
    logger.info("📞 PyTgCalls voice engine started")
    
    # Load Plugins
    plugins = load_plugins()
    logger.info(f"🔌 {len(plugins)} plugins loaded successfully")
    
    # Start Health Monitor (Background Task)
    asyncio.create_task(health_monitor(calls, app, userbot))
    logger.info("💚 Health monitor is now active")
    
    logger.info("🚀 Sunlo Music is ready to rock!")

async def shutdown():
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
    try:
        await startup()
        await idle() # Keeps the bot running
    except KeyboardInterrupt:
        logger.warning("Keyboard Interrupt detected.")
    finally:
        await shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Fatal startup error: {e}")
        sys.exit(1)
