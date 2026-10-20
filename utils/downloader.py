import asyncio
import yt_dlp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")
YDL_OPTS = {
    "format": "bestaudio/best",
    "outtmpl": f"{settings.CACHE_DIR}/%(id)s.%(ext)s",
    "quiet": True, "noplaylist": True, "geo_bypass": True, "nocheckcertificate": True,
}

class Downloader:
    def __init__(self):
        self.ydl = yt_dlp.YoutubeDL(YDL_OPTS)

    async def search_and_extract(self, query: str):
        def _extract():
            try:
                if not query.startswith("http"): query = f"ytsearch1:{query}"
                info = self.ydl.extract_info(query, download=False)
                if "entries" in info: info = info["entries"][0]
                video_id = info.get("id")
                return {
                    "id": video_id, "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0), "stream_url": info.get("url"),
                    "file_path": cache_manager.get_cached_file(video_id),
                    "uploader": info.get("uploader", "Unknown")
                }
            except Exception as e:
                logger.error(f"Extract error: {e}")
                return None
        return await asyncio.to_thread(_extract)

    async def download_audio(self, video_id: str) -> str:
        def _download():
            try:
                info = self.ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                return cache_manager.add_to_cache(self.ydl.prepare_filename(info), video_id)
            except Exception as e:
                logger.error(f"Download error: {e}")
                return None
        return await asyncio.to_thread(_download)

downloader = Downloader()
