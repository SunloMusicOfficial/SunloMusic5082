import asyncio
import aiohttp
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success

logger = get_logger("Downloader")

# 🔥 Fallen API Endpoint
SUNLO_API_URL = "https://tgmusic.fallenapi.fun"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        api_key = settings.SUNLO_API_KEY
        
        # ── ENGINE 1: Sunlo Music API (FallenApi) ──
        if api_key:
            try:
                logger.info(f"🔍 Calling Fallen API for: {query}")
                async with aiohttp.ClientSession() as session:
                    # Fallen API usually uses /download endpoint
                    payload = {"url": query, "api_key": api_key}
                    
                    async with session.post(f"{SUNLO_API_URL}/download", json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            # 🔥 YAHAN FIX HAI: Fallen API 'cdnurl' return karta hai
                            stream_url = data.get("cdnurl") or data.get("url")
                            
                            if stream_url:
                                logger.info(f"✅ Fallen API Success: {data.get('title', query)}")
                                return {
                                    "id": data.get("id", query),
                                    "title": data.get("title", "Unknown"),
                                    "duration": data.get("duration", 0),
                                    "stream_url": stream_url,
                                    "thumbnail": data.get("thumbnail"),
                                    "uploader": "Fallen API"
                                }
                            else:
                                logger.warning(f"⚠️ Fallen API Response did not contain 'cdnurl': {data}")
                        else:
                            logger.warning(f"⚠️ Fallen API returned status {resp.status}")
            except Exception as e:
                logger.warning(f"⚠️ Fallen API failed: {e}. Falling back to yt-dlp...")

        # ── ENGINE 2: yt-dlp Fallback (With Cookies) ──
        return await self._ytdlp_fallback(query)

    async def _ytdlp_fallback(self, query):
        cookies = await get_active_cookies()
        cookie_path = None
        cookie_name = None
        
        if cookies:
            cookie = cookies[0]
            cookie_name = cookie["name"]
            temp_fd, cookie_path = tempfile.mkstemp(suffix=".txt")
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(cookie["data"])

        def _extract():
            try:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "default_search": "ytsearch1",
                    "extractor_args": {"youtube": {"player_client": ["mweb", "web"]}},
                    "socket_timeout": 15,
                    # 🔥 429 error se bachne ke liye sleep add kiya
                    "sleep_interval": 2, 
                    "max_sleep_interval": 5,
                }
                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if "entries" in info and info["entries"]:
                        info = info["entries"][0]
                    return {
                        "id": info.get("id"),
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "stream_url": info.get("url"),
                        "thumbnail": info.get("thumbnail"),
                        "uploader": info.get("uploader", "YouTube"),
                    }
            except Exception as e:
                logger.error(f"yt-dlp fallback failed: {e}")
                return None

        result = await asyncio.to_thread(_extract)
        
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

        return result

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
