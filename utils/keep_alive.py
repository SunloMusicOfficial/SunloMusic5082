import asyncio
import aiohttp
import time
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("KeepAlive")

async def self_ping(app):
    """Render ko sleep hone se rokne ke liye self-ping."""
    url = settings.RENDER_EXTERNAL_URL
    
    if not url:
        logger.warning("⚠️ RENDER_EXTERNAL_URL not found. Self-ping disabled.")
        return

    logger.info(f"💓 Keep-Alive active. Target: {url}")
    
    # Startup Message
    if settings.LOG_GROUP_ID != 0:
        try:
            await app.send_message(settings.LOG_GROUP_ID, 
                f"💓 <b>𝐊𝐄𝐄𝐏-𝐀𝐋𝐈𝐕𝐄 𝐀𝐂𝐓𝐈𝐕𝐄</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 <b>Target:</b> <code>{url}</code>\n"
                f"⏱ <b>Interval:</b> <code>Every 10 Minutes</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━", parse_mode="html")
        except: pass

    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            try:
                async with session.get(url, timeout=15) as resp:
                    latency = round((time.time() - start_time) * 1000, 2)
                    status_text = "✅ <b>𝐏𝐈𝐍𝐆 𝐒𝐔𝐂𝐂𝐄𝐒𝐒</b>" if resp.status == 200 else f"⚠️ <b>𝐖𝐀𝐑𝐍𝐈𝐍𝐆: {resp.status}</b>"
                    
                    logger.info(f"Self-ping: {resp.status} ({latency}ms)")
                    
                    if settings.LOG_GROUP_ID != 0:
                        await app.send_message(settings.LOG_GROUP_ID,
                            f"{status_text}\n"
                            f"📡 <b>Response:</b> <code>{resp.status}</code>\n"
                            f"⚡ <b>Latency:</b> <code>{latency} ms</code>\n"
                            f"🟢 <b>Status:</b> <code>Bot is Awake</code>", parse_mode="html")
            except Exception as e:
                logger.error(f"Self-ping failed: {e}")
                if settings.LOG_GROUP_ID != 0:
                    await app.send_message(settings.LOG_GROUP_ID,
                        f"🚨 <b>𝐏𝐈𝐍𝐆 𝐅𝐀𝐈𝐋𝐄𝐃</b> 🚨\n"
                        f"❌ <b>Error:</b> <code>{str(e)[:50]}</code>\n"
                        f"🔴 <b>Action:</b> <i>Render might be down!</i>", parse_mode="html")
            
            await asyncio.sleep(600) # 10 Minutes
