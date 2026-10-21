import asyncio
import aiohttp
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        # ── STEP 1: API Call ──
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            try:
                logger.info(f"📡 Calling Download API for: {query}")
                async with aiohttp.ClientSession() as session:
                    # API ke hisaab se parameters (url & query dono bhej rahe hain)
                    payload = {"url": query, "q": query, "api_key": api_key}
                    
                    # Try POST first
                    async with session.post(f"{api_url}/download", json=payload, timeout=20) as resp:
                        response_text = await resp.text()
                        logger.info(f"📥 API Response ({resp.status}): {response_text[:500]}")
                        
                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                # 🔥 Universal Parser: Har key check kar raha hai
                                stream_url = (
                                    data.get("url") or data.get("link") or 
                                    data.get("download_url") or data.get("downloadUrl") or
                                    (data.get("data") and isinstance(data.get("data"), dict) and data["data"].get("url")) or
                                    (data.get("result") and isinstance(data.get("result"), dict) and data["result"].get("url"))
                                )
                                
                                if stream_url:
                                    logger.info("✅ Stream URL found in API response!")
                                    return {
                                        "id": data.get("id", query),
                                        "title": data.get("title", "Unknown"),
                                        "duration": data.get("duration", 0),
                                        "stream_url": stream_url,
                                        "thumbnail": data.get("thumbnail"),
                                        "uploader": "Custom API"
                                    }
                                else:
                                    logger.error("⚠️ API returned 200 but could not find URL in JSON.")
                            except Exception as e:
                                logger.error(f"Failed to parse JSON: {e}")
            except Exception as e:
                logger.error(f"❌ Connection to API failed: {e}")

        # ── STEP 2: yt-dlp Fallback (Agar API fail ho jaye) ──
        logger.info("🔄 API failed or bypassed, trying yt-dlp fallback...")
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
                    "socket_timeout": 20,
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

        if isinstance(result, dict) and cookie_name:
            await mark_cookie_success(cookie_name)
            
        return result if isinstance(result, dict) else None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
