import asyncio
import aiohttp
import time
from ftmgram import enums
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("KeepAlive")

async def self_ping(app):
    """Har 12 minute mein Render ko ping karega taaki sleep na ho."""
    url = settings.RENDER_EXTERNAL_URL
    
    if not url:
        logger.warning("⚠️ RENDER_EXTERNAL_URL not found. Self-ping disabled.")
        return

    logger.info(f"💓 Keep-Alive active for Render (12 min interval). Target: {url}")
    
    # Startup Message (Premium)
    if settings.LOG_GROUP_ID != 0:
        try:
            await app.send_message(
                settings.LOG_GROUP_ID, 
                "💓 <b>𝐑𝐄𝐍𝐃𝐄𝐑 𝐊𝐄𝐄𝐏-𝐀𝐋𝐈𝐕𝐄 𝐀𝐂𝐓𝐈𝐕𝐄</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 <b>Target:</b> <code>{url}</code>\n"
                f"⏱ <b>Interval:</b> <code>Every 12 Minutes</code>\n"
                "🛡 <b>Purpose:</b> <i>Preventing Render Sleep</i>\n"
                "━━━━━━━━━━━━━━━━━━━━", 
                parse_mode=enums.ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send startup ping log: {e}")

    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            try:
                async with session.get(url, timeout=15) as resp:
                    latency = round((time.time() - start_time) * 1000, 2)
                    status_text = "✅ <b>𝐏𝐈𝐍𝐆 𝐒𝐔𝐂𝐂𝐄𝐒𝐒</b>" if resp.status == 200 else f"⚠️ <b>𝐖𝐀𝐑𝐍𝐈𝐍𝐆: {resp.status}</b>"
                    
                    logger.info(f"Self-ping: {resp.status} ({latency}ms)")
                    
                    # Premium Log Message
                    if settings.LOG_GROUP_ID != 0:
                        try:
                            await app.send_message(
                                settings.LOG_GROUP_ID,
                                f"{status_text}\n"
                                f"━━━━━━━━━━━━━━━━━━━━\n"
                                f"📡 <b>Response:</b> <code>{resp.status} OK</code>\n"
                                f"⚡ <b>Latency:</b> <code>{latency} ms</code>\n"
                                f"🟢 <b>Status:</b> <code>Bot is Awake</code>\n"
                                f"━━━━━━━━━━━━━━━━━━━━", 
                                parse_mode=enums.ParseMode.HTML
                            )
                        except Exception as e:
                            pass # Ignore log send errors to keep loop running
                            
            except Exception as e:
                logger.error(f"Self-ping failed: {e}")
                if settings.LOG_GROUP_ID != 0:
                    try:
                        await app.send_message(
                            settings.LOG_GROUP_ID,
                            f"🚨 <b>𝐏𝐈𝐍𝐆 𝐅𝐀𝐈𝐋𝐄𝐃</b> 🚨\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"❌ <b>Error:</b> <code>{str(e)[:100]}</code>\n"
                            f"🔴 <b>Action:</b> <i>Render might be down!</i>\n"
                            f"━━━━━━━━━━━━━━━━━━━━", 
                            parse_mode=enums.ParseMode.HTML
                        )
                    except Exception as e:
                        pass
            
            # 🔥 12 Minutes (720 seconds) wait
            await asyncio.sleep(720)
