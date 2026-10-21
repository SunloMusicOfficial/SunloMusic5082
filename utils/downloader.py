import asyncio
import yt_dlp
import http.cookiejar
import io
from utils.logger import get_logger
from database.cookies import get_active_cookies, mark_cookie_dead, mark_cookie_success
from config.settings import settings
from ftmgram import enums

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt", retries=3):
        cookies = await get_active_cookies()
        if not cookies:
            return await self._extract(query, None)

        for attempt in range(min(retries, len(cookies))):
            cookie = cookies[attempt]
            cookie_data = cookie["data"]
            
            # 🌟 Advanced: In-Memory Cookiejar (No disk file)
            cj = http.cookiejar.MozillaCookieJar()
            try:
                cj._cookies = http.cookiejar.MozillaCookieJar()._really_load(
                    io.StringIO(cookie_data), "cookies.txt", True, True
                )
            except Exception:
                pass # Agar format kharab ho toh skip

            logger.info(f"🍪 Trying Cookie: {cookie['name']}")
            result = await self._extract(query, cj)

            if result and "stream_url" in result:
                await mark_cookie_success(cookie["name"])
                return result
            elif result == "COOKIE_DEAD":
                logger.warning(f"🚨 Cookie '{cookie['name']}' is dead.")
                await mark_cookie_dead(cookie["name"])
                
                # 🌟 Advanced: Alert Owner on Telegram
                if settings.OWNER_ID:
                    try:
                        from core.bot import app
                        await app.send_message(
                            settings.OWNER_ID, 
                            f"🚨 <b>COOKIE EXPIRED</b>\nAccount: <code>{cookie['name']}</code> has been marked as DEAD.\n<i>Please upload new cookies via web dashboard.</i>",
                            parse_mode=enums.ParseMode.HTML
                        )
                    except: pass
                continue
            else:
                return None
        return None

    async def _extract(self, query, cookiejar):
        def _run():
            try:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "default_search": "ytsearch1",
                    "extractor_args": {"youtube": {"player_client": ["mweb", "android_vr"]}},
                }
                if cookiejar:
                    ydl_opts["cookiejar"] = cookiejar # 🌟 Pass in-memory cookiejar

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=False)
                    if "entries" in info and info["entries"]: info = info["entries"][0]
                    return {
                        "id": info.get("id"),
                        "title": info.get("title", "Unknown"),
                        "duration": info.get("duration", 0),
                        "stream_url": info.get("url"),
                        "thumbnail": info.get("thumbnail"),
                        "uploader": info.get("uploader", "Unknown"),
                    }
            except Exception as e:
                err = str(e)
                if "Sign in to confirm" in err or "403" in err:
                    return "COOKIE_DEAD"
                return None
        return await asyncio.to_thread(_run)

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
