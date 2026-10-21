import asyncio
import yt_dlp
import aiohttp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

# Multiple free proxy sources for robust fetching
PROXY_SOURCES = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"
]

class Downloader:
    def __init__(self):
        self.proxy_pool = []
        self.last_proxy_fetch = 0

    async def _fetch_proxies(self):
        """Fetch free proxies from multiple sources with retries."""
        logger.info("🔄 Fetching fresh proxies from multiple sources...")
        proxies = set()
        async with aiohttp.ClientSession() as session:
            for url in PROXY_SOURCES:
                try:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            for line in text.splitlines():
                                p = line.strip()
                                if p and not p.startswith('#'):
                                    proxies.add(p)
                except Exception as e:
                    logger.warning(f"Failed to fetch from {url}: {e}")
        
        self.proxy_pool = list(proxies)
        self.last_proxy_fetch = asyncio.get_event_loop().time()
        logger.info(f"✅ Loaded {len(self.proxy_pool)} proxies.")

    async def search_and_extract(self, query: str, platform="yt"):
        # Refresh proxies if empty or older than 15 minutes
        if not self.proxy_pool or (asyncio.get_event_loop().time() - self.last_proxy_fetch) > 900:
            await self._fetch_proxies()

        if not self.proxy_pool:
            logger.error("❌ No proxies available. Cannot bypass YouTube block.")
            return None

        # Try up to 5 random proxies
        import random
        working_proxies = random.sample(self.proxy_pool, min(5, len(self.proxy_pool)))
        
        for proxy in working_proxies:
            def _extract():
                try:
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "quiet": True,
                        "noplaylist": True,
                        "default_search": "ytsearch1",
                        "extractor_args": {"youtube": {"player_client": ["android_vr", "mweb"]}},
                        "proxy": f"http://{proxy}",
                        "socket_timeout": 10,
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
                    }
                except Exception as e:
                    logger.warning(f"Proxy {proxy} failed: {e}")
                    return None
            
            result = await asyncio.to_thread(_extract)
            if result:
                logger.info(f"✅ Success with proxy {proxy}")
                return result

        logger.error("❌ All proxies failed to extract stream.")
        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

    async def download_media(self, video_id: str, is_video=False):
        return None

downloader = Downloader()
