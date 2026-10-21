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
        video_url = query
        title = query
        duration = 0
        thumbnail = None

        if not query.startswith("http"):
            logger.info(f"🔍 Searching YouTube for: {query}")
            try:
                ydl_opts = {"quiet": True, "extract_flat": True, "default_search": "ytsearch1"}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                        if entry.get("id"):
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            title = entry.get("title", query)
                            thumbnail = entry.get("thumbnail")
                            logger.info(f"✅ Found URL: {video_url}")
            except Exception as e:
                logger.error(f"❌ Search failed: {e}")

        if "None" in video_url:
            return None

        # ── API CALL (Timeout 30s) ──
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            logger.info(f"🚀 Calling API for: {video_url}")
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {"url": video_url, "api_key": api_key, "type": "audio"}
                    async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=30) as resp:
                        response_text = await resp.text()
                        logger.info(f"📥 API Status: {resp.status} | Response: {response_text[:300]}")
                        
                        if resp.status == 200:
                            data = await resp.json()
                            stream_url = (data.get("url") or data.get("link") or 
                                          data.get("download_url") or data.get("downloadUrl") or
                                          (data.get("data") and isinstance(data.get("data"), dict) and data["data"].get("url")))
                            if stream_url:
                                logger.info("✅ Found Stream URL from API!")
                                return {"id": video_url.split("v=")[-1], "title": data.get("title", title),
                                        "duration": data.get("duration", duration), "stream_url": stream_url,
                                        "thumbnail": data.get("thumbnail", thumbnail), "uploader": "API"}
            except asyncio.TimeoutError:
                logger.error("❌ API Timeout after 30 seconds. Server is not responding.")
            except Exception as e:
                logger.error(f"❌ API Connection failed: {e}")

        # ── FALLBACK: yt-dlp with cookies ──
        logger.info("🔄 Falling back to yt-dlp with cookies...")
        return await self._ytdlp_fallback(video_url, title, duration, thumbnail)

    async def _ytdlp_fallback(self, video_url, title, duration, thumbnail):
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
                ydl_opts = {"format": "bestaudio/best", "quiet": True, "noplaylist": True,
                            "extractor_args": {"youtube": {"player_client": ["mweb", "web"]}},
                            "socket_timeout": 20}
                if cookie_path:
                    ydl_opts["cookiefile"] = cookie_path
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(video_url, download=False)
                    return {"id": info.get("id"), "title": info.get("title", title),
                            "duration": info.get("duration", duration), "stream_url": info.get("url"),
                            "thumbnail": info.get("thumbnail", thumbnail), "uploader": "YouTube"}
            except Exception as e:
                logger.error(f"❌ yt-dlp failed: {e}")
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
