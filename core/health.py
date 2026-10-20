import asyncio
from utils.logger import get_logger
import core.calls as calls_module

logger = get_logger("HealthMonitor")

async def health_monitor(app, userbot):
    while True:
        try:
            await asyncio.sleep(300)
            if calls_module.calls:
                active_calls = len(await calls_module.calls.calls)
                logger.info(f"💚 Health Check: Bot is alive. Active Voice Chats: {active_calls}")
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health Monitor Error: {e}")
