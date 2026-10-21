import asyncio
import aiohttp
import os
import time
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("KeepAlive")

async def send_ping_log(text: str):
    """Log Group mein premium message bhejne ke liye."""
    if settings.LOG_GROUP_ID != 0:
        try:
            # Circular import se bachne ke liye dynamic import
            from core.bot import app
            if app.is_connected:
                await app.send_message(settings.LOG_GROUP_ID, text, parse_mode="html")
        except Exception as e:
            logger.error(f"Failed to send ping log to group: {e}")

async def self_ping():
    """
    Har 10 minute mein apne public URL ko ping karta hai
    taaki Render free tier sleep na ho.
    """
    url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("KEEP_ALIVE_URL")
    
    if not url:
        logger.warning("⚠️ RENDER_EXTERNAL_URL not found. Self-ping disabled.")
        return

    logger.info(f"💓 Keep-Alive active. Pinging {url} every 10 minutes.")
    
    # Pehli baar startup par ek premium message bhej do
    await send_ping_log(
        f"💓 <b>𝐊𝐄𝐄𝐏-𝐀𝐋𝐈𝐕𝐄 𝐀𝐂𝐓𝐈𝐕𝐄</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Target URL:</b> <code>{url}</code>\n"
        f"⏱ <b>Interval:</b> <code>Every 10 Minutes</code>\n"
        f"🛡 <b>Purpose:</b> <i>Preventing Render Sleep</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    async with aiohttp.ClientSession() as session:
        while True:
            start_time = time.time()
            try:
                async with session.get(url, timeout=15) as resp:
                    end_time = time.time()
                    latency = round((end_time - start_time) * 1000, 2)
                    
                    if resp.status == 200:
                        logger.info(f"✅ Self-ping successful: {url} ({latency}ms)")
                        
                        # Premium Success Log
                        await send_ping_log(
                            f"✅ <b>𝐏𝐈𝐍𝐆 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🌐 <b>URL:</b> <code>{url}</code>\n"
                            f"📡 <b>Status Code:</b> <code>200 OK</code>\n"
                            f"⚡ <b>Response Time:</b> <code>{latency} ms</code>\n"
                            f"🟢 <b>Bot Status:</b> <code>Awake & Active</code>\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
                    else:
                        logger.warning(f"⚠️ Self-ping returned status {resp.status}")
                        await send_ping_log(
                            f"⚠️ <b>𝐏𝐈𝐍𝐆 𝐖𝐀𝐑𝐍𝐈𝐍𝐆</b>\n"
                            f"━━━━━━━━━━━━━━━━━━━━\n"
                            f"🌐 <b>URL:</b> <code>{url}</code>\n"
                            f"📡 <b>Status Code:</b> <code>{resp.status}</code>\n"
                            f"🟡 <b>Action:</b> <i>Bot is awake but server responded with error.</i>\n"
                            f"━━━━━━━━━━━━━━━━━━━━"
                        )
            except asyncio.TimeoutError:
                logger.error("❌ Self-ping timed out")
                await send_ping_log(
                    f"🚨 <b>𝐏𝐈𝐍𝐆 𝐓𝐈𝐌𝐄𝐎𝐔𝐓</b> 🚨\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🌐 <b>URL:</b> <code>{url}</code>\n"
                    f"❌ <b>Error:</b> <code>Connection Timed Out (15s)</code>\n"
                    f"🔴 <b>Status:</b> <i>Render might be sleeping or down!</i>\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
            except Exception as e:
                logger.error(f"❌ Self-ping failed: {e}")
                await send_ping_log(
                    f"🚨 <b>𝐏𝐈𝐍𝐆 𝐅𝐀𝐈𝐋𝐄𝐃</b> 🚨\n"
                    f"━━━━━━━━━━━━━━━━━━━━\n"
                    f"🌐 <b>URL:</b> <code>{url}</code>\n"
                    f"❌ <b>Error:</b> <code>{str(e)[:100]}</code>\n"
                    f"🔴 <b>Status:</b> <i>Check Render Logs immediately!</i>\n"
                    f"━━━━━━━━━━━━━━━━━━━━"
                )
            
            # 10 minute (600 seconds) wait karo
            await asyncio.sleep(600)
