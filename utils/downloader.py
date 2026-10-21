import asyncio
import aiohttp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

SUNLO_API_URL = "https://api.nexgenbots.xyz"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        api_key = settings.SUNLO_API_KEY
        
        # 1. Try SunloMusicApi (NexGenBots)
        if api_key:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{SUNLO_API_URL}/stream",
                        params={"q": query, "api_key": api_key}
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
                        logger.warning(f"⚠️ SunloMusicApi status {resp.status}. Falling back...")
            except Exception as e:
                logger.warning(f"⚠️ SunloMusicApi failed: {e}. Falling back...")
        
        # 2. Fallback to yt-dlp
        return await self._fallback_search(query)

    async def _fallback_search(self, query: str):
        def _extract():
            try:
                import yt_dlp
                ydl_opts = {
                    "format": "bestaudio/best",
                    "quiet": True, 
                    "noplaylist": True, 
                    "geo_bypass": True, 
                    "nocheckcertificate": True,
                    "extractor_args": {"youtube": {"player_client": ["android_vr"]}},
                    "js_runtimes": {"node": {}},
                    "remote_components": ["ejs:github"],
                    "default_search": "ytsearch1"
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
                logger.error(f"yt-dlp fallback failed: {e}")
                return None
        return await asyncio.to_thread(_extract)

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        return None

downloader = Downloader()
