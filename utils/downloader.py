import asyncio
import aiohttp
import yt_dlp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_id = None
        title = "Unknown"
        duration = 0
        thumbnail = None

        # 1. Video ID nikaalo (Agar direct link nahi hai toh)
        if not query.startswith("http"):
            try:
                ydl_opts = {"quiet": True, "extract_flat": True, "noplaylist": True, "default_search": "ytsearch1"}
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(query, download=False)
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]
                video_id = info.get("id")
                title = info.get("title", "Unknown")
                duration = info.get("duration", 0)
                thumbnail = info.get("thumbnail")
            except Exception as e:
                logger.warning(f"Metadata search failed: {e}")
                # Fallback search via David Cyril API
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://api.davidcyriltech.my.id/search/youtube?q={query}") as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if data and len(data) > 0:
                                    video_id = data[0].get("videoId")
                                    title = data[0].get("title")
                                    duration = data[0].get("duration", 0)
                except: pass
        else:
            video_id = query.split("v=")[-1].split("&")[0] if "v=" in query else query.split("/")[-1]

        if not video_id:
            logger.error("❌ Could not find video ID")
            return None

        # 2. Try Vevioz API (Direct MP3 URL)
        try:
            logger.info(f"🔄 Trying Vevioz API for {video_id}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.vevioz.com/@api/json/mp3/{video_id}", timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "url" in data:
                            logger.info("✅ Vevioz API Success!")
                            return {
                                "id": video_id, "title": title, "duration": duration,
                                "thumbnail": thumbnail, "stream_url": data["url"], "uploader": "Vevioz"
                            }
        except Exception as e:
            logger.warning(f"⚠️ Vevioz failed: {e}")

        # 3. Try David Cyril API (Direct MP3 URL)
        try:
            logger.info(f"🔄 Trying DavidCyril API for {video_id}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://api.davidcyriltech.my.id/download/ytmp3?url=https://youtube.com/watch?v={video_id}", timeout=15) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("success"):
                            result = data.get("result", {})
                            logger.info("✅ DavidCyril API Success!")
                            return {
                                "id": video_id, "title": result.get("title", title), "duration": duration,
                                "thumbnail": thumbnail, "stream_url": result.get("download_url"), "uploader": "DavidCyril"
                            }
        except Exception as e:
            logger.warning(f"⚠️ DavidCyril failed: {e}")

        # 4. Last Resort: yt-dlp (Agar sab fail ho jaye)
        logger.info("🔄 Trying yt-dlp final fallback...")
        return await self._fallback_search(video_id, title, duration, thumbnail)

    async def _fallback_search(self, video_id, title, duration, thumbnail):
        def _extract():
            try:
                ydl_opts = {
                    "format": "bestaudio/best", "quiet": True, "noplaylist": True,
                    "geo_bypass": True, "nocheckcertificate": True,
                    "extractor_args": {"youtube": {"player_client": ["tv", "mweb"]}},
                }
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                return {
                    "id": video_id, "title": info.get("title", title), "duration": info.get("duration", duration),
                    "stream_url": info.get("url"), "thumbnail": info.get("thumbnail", thumbnail), "uploader": info.get("uploader", "Unknown")
                }
            except Exception as e:
                logger.error(f"❌ yt-dlp final fallback failed: {e}")
                return None
        return await asyncio.to_thread(_extract)

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        return None

downloader = Downloader()
