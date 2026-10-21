import asyncio
import aiohttp
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success

logger = get_logger("Downloader")

# Fallen API Endpoint
SUNLO_API_URL = "https://tgmusic.fallenapi.fun"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        api_key = settings.SUNLO_API_KEY
        
        # ── ENGINE 1: Sunlo Music API (FallenApi) ──
        if api_key:
            try:
                logger.info(f"🔍 Calling Sunlo API for: {query}")
                async with aiohttp.ClientSession() as session:
                    # API ko GET aur POST dono tarike se try karte hain (robustness ke liye)
                    payload = {"url": query, "api_key": api_key}
                    
                    # 1. Try POST
                    async with session.post(f"{SUNLO_API_URL}/download", json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            stream_url = data.get("url") or data.get("link") or data.get("result", {}).get("url")
                            if stream_url:
                                return self._format_api_response(data, query, stream_url)
                    
                    # 2. Try GET (Agar POST fail ho)
                    async with session.get(f"{SUNLO_API_URL}/download?url={query}&api_key={api_key}", timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            stream_url = data.get("url") or data.get("link") or data.get("result", {}).get("url")
                            if stream_url:
                                return self._format_api_response(data, query, stream_url)
                                
            except Exception as e:
                logger.warning(f"⚠️ Sunlo API failed: {e}. Falling back to yt-dlp...")

        # ── ENGINE 2: yt-dlp Fallback (With Cookies) ──
        return await self._ytdlp_fallback(query)

    def _format_api_response(self, data, query, stream_url):
        result = data.get("result", data)
        logger.info(f"✅ Sunlo API Success: {result.get('title', query)}")
        
        # Duration parsing
        dur = result.get("duration", 0)
        if isinstance(dur, str) and ":" in dur:
            try:
                parts = list(map(int, dur.split(':')))
                dur = parts[0]*60 + parts[1] if len(parts) == 2 else parts[0]*3600 + parts[1]*60 + parts[2]
            except: dur = 0
            
        return {
            "id": result.get("id", query),
            "title": result.get("title", "Unknown"),
            "duration": dur,
            "stream_url": stream_url,
            "thumbnail": result.get("thumbnail"),
            "uploader": "Sunlo API"
        }

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
                logger.error(f"yt-dlp fallback failed: {e}")
                return None

        result = await asyncio.to_thread(_extract)
        
        if cookie_path and os.path.exists(cookie_path):
            os.remove(cookie_path)

        return result

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
