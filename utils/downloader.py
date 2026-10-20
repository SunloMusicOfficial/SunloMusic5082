import asyncio
import yt_dlp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": f"{settings.CACHE_DIR}/%(id)s.%(ext)s",
    "quiet": True, "noplaylist": True, "geo_bypass": True, 
    "nocheckcertificate": True, "js_runtimes": {"node": {}},
    "remote_components": ["ejs:github"]
}

class Downloader:
    def __init__(self):
        self.ydl = yt_dlp.YoutubeDL(YDL_OPTS)

    async def search_multiple(self, query: str, limit=5):
        """Search top X results without downloading."""
        def _extract():
            try:
                search_query = f"ytsearch{limit}:{query}" if not query.startswith("http") else query
                info = self.ydl.extract_info(search_query, download=False)
                results = []
                if "entries" in info:
                    for entry in info["entries"]:
                        results.append({
                            "id": entry.get("id"),
                            "title": entry.get("title", "Unknown"),
                            "duration": entry.get("duration", 0),
                            "uploader": entry.get("uploader", "Unknown"),
                            "thumbnail": entry.get("thumbnail")
                        })
                return results
            except Exception as e:
                logger.error(f"Search error: {e}")
                return []
        return await asyncio.to_thread(_extract)

    async def get_stream(self, video_id: str):
        """Get stream URL by ID."""
        def _extract():
            try:
                info = self.ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                return {
                    "id": video_id,
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "stream_url": info.get("url"),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader", "Unknown")
                }
            except Exception as e:
                logger.error(f"Stream extract error: {e}")
                return None
        return await asyncio.to_thread(_extract)

downloader = Downloader()
