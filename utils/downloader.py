import asyncio
import aiohttp
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success

logger = get_logger("Downloader")

# 🔥 FALLEN API ENDPOINT
SUNLO_API_URL = "https://tgmusic.fallenapi.fun"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        api_key = settings.SUNLO_API_KEY
        
        # ── ENGINE 1: Sunlo Music API (FallenApi) ──
        if api_key:
            try:
                logger.info(f"🔍 Using Sunlo Music API for: {query}")
                async with aiohttp.ClientSession() as session:
                    # API expects a URL or search query
                    async with session.get(
                        f"{SUNLO_API_URL}/download", 
                        params={"url": query, "api_key": api_key},
                        timeout=15
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            # API usually returns result under 'result' or direct 'url'
                            result = data.get("result", data)
                            stream_url = result.get("url") or result.get("download_url")
                            
                            if stream_url:
                                logger.info(f"✅ Sunlo API Success: {result.get('title', query)}")
                                return {
                                    "id": result.get("id", query),
                                    "title": result.get("title", "Unknown"),
                                    "duration": result.get("duration", 0),
                                    "stream_url": stream_url,
                                    "thumbnail": result.get("thumbnail"),
                                    "uploader": "Sunlo Music API"
                                }
                        else:
                            logger.warning(f"⚠️ Sunlo API returned status {resp.status}")
            except Exception as e:
                logger.warning(f"⚠️ Sunlo API failed: {e}. Falling back to yt-dlp...")

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
                if "Sign in to confirm" in str(e) or "403" in str(e):
                    return "COOKIE_DEAD"
                return None

        result = await asyncio.to_thread(_extract)
        
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

        if result == "COOKIE_DEAD" and cookie_name:
            await mark_cookie_dead(cookie_name)
            return None
        elif isinstance(result, dict) and cookie_name:
            await mark_cookie_success(cookie_name)
            
        return result if isinstance(result, dict) else None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
