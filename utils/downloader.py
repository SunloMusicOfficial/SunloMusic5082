import asyncio
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
        self.ydl = None # Abhi load nahi hoga

    def _get_ydl(self):
        # Jab zaroorat padegi tab load hoga (Lazy Loading)
        if self.ydl is None:
            import yt_dlp
            self.ydl = yt_dlp.YoutubeDL(YDL_OPTS)
        return self.ydl

    async def search_and_extract(self, query: str, platform="yt"):
        def _extract():
            try:
                ydl = self._get_ydl()
                search_query = query
                if not search_query.startswith("http"):
                    prefix = "ytsearch1:" if platform == "yt" else "scsearch1:"
                    search_query = f"{prefix}{search_query}"
                
                info = ydl.extract_info(search_query, download=False)
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]
                
                video_id = info.get("id")
                formats = info.get("formats", [])
                stream_url = info.get("url")
                
                if not stream_url and formats:
                    for f in formats:
                        if f.get("acodec") != "none":
                            stream_url = f.get("url")
                            break
                            
                thumbnails = info.get("thumbnails", [])
                thumbnail_url = info.get("thumbnail")
                if not thumbnail_url and thumbnails:
                    thumbnail_url = thumbnails[-1].get("url")

                return {
                    "id": video_id, "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0), "stream_url": stream_url,
                    "file_path": cache_manager.get_cached_file(video_id),
                    "uploader": info.get("uploader", "Unknown"),
                    "thumbnail": thumbnail_url
                }
            except Exception as e:
                logger.error(f"Extract error: {e}")
                return None
        return await asyncio.to_thread(_extract)

    async def download_media(self, video_id: str, is_video=False) -> str:
        def _download():
            try:
                ydl = self._get_ydl()
                opts = YDL_OPTS.copy()
                if is_video:
                    opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
                return cache_manager.add_to_cache(ydl.prepare_filename(info), video_id, "mp4" if is_video else "mp3")
            except Exception as e:
                logger.error(f"Download error: {e}")
                return None
        return await asyncio.to_thread(_download)

downloader = Downloader()
