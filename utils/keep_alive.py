import asyncio
import aiohttp
import time
from ftmgram import enums
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("KeepAlive")

# 🔥 AAPKA SNAPDEPLOY URL (Ping ke liye)
SUNLO_CUSTOM_API = "https://cobalt-658d8.containers.snapdeploy.app"

async def self_ping(app):
    render_url = settings.RENDER_EXTERNAL_URL
    
    if not render_url:
        logger.warning("⚠️ RENDER_EXTERNAL_URL not found. Self-ping disabled.")
        return

    logger.info(f"💓 Keep-Alive active for Render & Cobalt API")
    
    async with aiohttp.ClientSession() as session:
        while True:
            # 1. Render Ko Ping Karo (Bot ko zinda rakhne ke liye)
            try:
                async with session.get(render_url, timeout=15) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ Render Ping Success")
            except Exception as e:
                logger.error(f"❌ Render Ping Failed: {e}")

            # 2. SnapDeploy Cobalt Ko Ping Karo (API ko sone se rokne ke liye)
            try:
                # Root URL check karne se container wake rehta hai
                async with session.get(SUNLO_CUSTOM_API, timeout=15) as resp:
                    if resp.status == 200:
                        logger.info(f"✅ Cobalt API Ping Success (Awake)")
            except Exception as e:
                logger.warning(f"⚠️ Cobalt API Ping Failed: {e}")
            
            # 10 minute wait
            await asyncio.sleep(600)
