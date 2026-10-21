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
        
        if not api_key:
            logger.error("SUNLO_API_KEY missing! Please contact the Owner.")
            return None
        
        logger.info(f"✅ Using SunloMusicApi for: {query}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{SUNLO_API_URL}/stream",
                    params={"q": query, "api_key": api_key}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "id": data.get("videoId"),
                            "title": data.get("title", "Unknown"),
                            "duration": data.get("duration", 0),
                            "thumbnail": data.get("thumbnail"),
                            "stream_url": data.get("url"),
                            "uploader": data.get("author", "Unknown")
                        }
                    else:
                        logger.error(f"SunloMusicApi error: HTTP {resp.status}")
        except Exception as e:
            logger.error(f"SunloMusicApi Connection failed: {e}")
        
        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        return None

downloader = Downloader()
