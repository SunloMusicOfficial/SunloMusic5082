import asyncio
import aiohttp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        """Direct best match search using yt-dlp (extract_flat)."""
        def _search():
            try:
                import yt_dlp
                ydl_opts = {
                    "quiet": True, 
                    "extract_flat": True, 
                    "noplaylist": True,
                    "extractor_args": {"youtube": {"player_client": ["web"]}} # metadata ke liye web theek hai
                }
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                search_query = query if query.startswith("http") else f"ytsearch1:{query}"
                info = ydl.extract_info(search_query, download=False)
                
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]
                
                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnails", [{}])[-1].get("url") if info.get("thumbnails") else info.get("thumbnail"),
                    "uploader": info.get("uploader", "Unknown")
                }
            except Exception as e:
                logger.error(f"Search failed: {e}")
                return None
        return await asyncio.to_thread(_search)

    async def get_stream(self, video_id: str):
        """Get direct stream URL using Cobalt API (Bypasses YouTube block)."""
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {"url": url, "isAudioOnly": True}

        # Try multiple Cobalt instances
        cobalt_instances = ["https://api.cobalt.tools/", "https://co.wuk.sh/"]
        
        for base in cobalt_instances:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(base, json=payload, headers=headers, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            if data.get("status") in ["stream", "redirect", "tunnel"]:
                                return data.get("url")
            except Exception as e:
                logger.warning(f"Cobalt instance {base} failed: {e}")

        logger.error(f"All Cobalt instances failed for {video_id}")
        return None

    async def download_media(self, video_id: str, is_video=False):
        # Download logic (optional)
        return None

downloader = Downloader()
