import asyncio
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt", retries=3):
        cookies = await get_active_cookies()
        
        if not cookies:
            logger.warning("⚠️ No active cookies found in pool. Trying without cookies...")
            return await self._extract(query, None)

        for attempt in range(min(retries, len(cookies))):
            cookie = cookies[attempt]
            cookie_data = cookie.get("data")
            cookie_name = cookie["name"]
            
            if not cookie_data:
                continue

            logger.info(f"🍪 Trying Cookie: {cookie_name}")
            
            # 🌟 FIX: Save cookie to a temporary file for yt-dlp
            temp_fd, temp_path = tempfile.mkstemp(suffix=".txt")
            with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                f.write(cookie_data)

            result = await self._extract(query, temp_path)

            # Cleanup temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)

            if result and "stream_url" in result:
                await mark_cookie_success(cookie_name)
                return result
            elif result == "COOKIE_DEAD":
                logger.warning(f"🚨 Cookie '{cookie_name}' expired/blocked. Rotating...")
                await mark_cookie_dead(cookie_name)
                continue
            else:
                # Agar error aaya (jaise video not found), toh log karo
                logger.error(f"❌ Extraction Error for {cookie_name}: {result}")
                continue # Try next cookie
                
        logger.error("❌ All cookies failed.")
        return None

    async def _extract(self, query, cookie_path):
        def _run():
            try:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "default_search": "ytsearch1",
                    # Cookies ke saath web aur mweb client sabse best kaam karte hain
                    "extractor_args": {"youtube": {"player_client": ["web", "mweb", "android_vr"]}},
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
                err = str(e)
                if "Sign in to confirm" in err or "bot" in err.lower() or "403" in err:
                    return "COOKIE_DEAD"
                return err # Return actual error string
        return await asyncio.to_thread(_run)

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
