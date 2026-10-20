import asyncio
from utils.logger import get_logger

logger = get_logger("HealthMonitor")

async def health_monitor(calls, app, userbot):
    """Background task to check if bot and voice engine are alive."""
    while True:
        try:
            # Simple ping check every 5 minutes
            await asyncio.sleep(300)
            
            # Log stats
            active_calls = len(await calls.active_calls)
            logger.info(f"💚 Health Check: Bot is alive. Active Voice Chats: {active_calls}")
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Health Monitor Error: {e}")
