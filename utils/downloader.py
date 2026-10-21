import asyncio
import aiohttp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

NEXGEN_API = "https://api.nexgenbots.xyz"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        # API se direct stream URL fetch karo
        api_key = getattr(settings, "NEXGEN_API_KEY", None)
        if not api_key:
            logger.error("NEXGEN_API_KEY missing! Add it to .env or Render Environment Variables.")
            return None

        try:
            async with aiohttp.ClientSession() as session:
                # API endpoint (Assuming standard structure, adjust if needed)
                async with session.get(
                    f"{NEXGEN_API}/stream",
                    params={"q": query, "api_key": api_key}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "id": data.get("videoId"),
                            "title": data.get("title", "Unknown"),
                            "duration": data.get("duration", 0),
                            "thumbnail": data.get("thumbnail"),
                            "stream_url": data.get("url"), # Direct audio stream
                            "uploader": data.get("author", "Unknown")
                        }
                    else:
                        logger.error(f"API returned status {resp.status}: {await resp.text()}")
        except Exception as e:
            logger.error(f"NexGenBots API failed: {e}")
        
        return None

    async def get_stream(self, video_id: str):
        # Same as search_and_extract, API handles direct ID fetching
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        # Downloads handled by API (for /song command)
        return None

downloader = Downloader()
