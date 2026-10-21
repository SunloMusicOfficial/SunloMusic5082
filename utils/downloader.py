import asyncio
import aiohttp
import yt_dlp
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("Downloader")

SUNLO_API_URL = "https://api.nexgenbots.xyz"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        # 1. Try SunloMusicApi
        api_key = settings.SUNLO_API_KEY
        if api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{SUNLO_API_URL}/stream",
                        params={"q": query, "api_key": api_key},
                        timeout=10
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("url"):
                                logger.info(f"✅ SunloMusicApi success: {query}")
                                return {
                                    "id": data.get("videoId", query),
                                    "title": data.get("title", "Unknown"),
                                    "duration": data.get("duration", 0),
                                    "thumbnail": data.get("thumbnail"),
                                    "stream_url": data.get("url"),
                                    "uploader": data.get("author", "Unknown")
                                }
                            else:
                                logger.error(f"⚠️ API 200 OK but no URL. Response: {data}")
                        else:
                            logger.error(f"⚠️ API Error {resp.status}: {await resp.text()}")
            except Exception as e:
                logger.error(f"⚠️ SunloMusicApi failed: {e}")

        # 2. Fallback to yt-dlp with iOS Client (Bypasses Render IP block)
        logger.info("🔄 Trying yt-dlp fallback with iOS client...")
        return await self._fallback_search(query)

    async def _fallback_search(self, query: str):
        def _extract():
            try:
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True,
                    "noplaylist": True,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "default_search": "ytsearch1",
                    "extractor_args": {
                        "youtube": {
                            "player_client": ["ios", "android"], # iOS is best for bypassing blocks
                            "skip": ["hls", "dash"]
                        }
                    }
                }
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(query, download=False)
                
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]

                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "stream_url": info.get("url"),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader", "Unknown"),
                    "file_path": None
                }
            except Exception as e:
                logger.error(f"❌ yt-dlp fallback failed: {e}")
                return None
        return await asyncio.to_thread(_extract)

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        return None

downloader = Downloader()
