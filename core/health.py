import asyncio
from utils.logger import get_logger
import core.calls as calls_module

logger = get_logger("HealthMonitor")

async def health_monitor(app, userbot):
    while True:
        try:
            await asyncio.sleep(300) # 5 minutes
            
            # Check if PyTgCalls is disconnected
            if calls_module.calls:
                try:
                    active_calls = len(await calls_module.calls.calls)
                    logger.info(f"💚 Health Check: Bot is alive. Active Voice Chats: {active_calls}")
                except Exception as e:
                    logger.error(f"⚠️ PyTgCalls disconnected! Attempting reconnect... Error: {e}")
                    try:
                        from pytgcalls import PyTgCalls
                        calls_module.calls = PyTgCalls(userbot)
                        await calls_module.calls.start()
                        logger.info("✅ PyTgCalls reconnected successfully!")
                    except Exception as e2:
                        logger.critical(f"❌ Failed to reconnect PyTgCalls: {e2}")
            else:
                logger.warning("⚠️ PyTgCalls instance not found!")
                
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health Monitor Error: {e}")
