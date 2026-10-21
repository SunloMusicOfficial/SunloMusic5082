import asyncio
from yukiapi import YukiAPI
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_multiple(self, query: str, limit=5):
        """Search top X results for the interactive UI."""
        try:
            async with YukiAPI() as yuki:
                results = await yuki.search(query, limit=limit)
                parsed_results = []
                for res in results:
                    parsed_results.append({
                        "id": res.get("id"),
                        "title": res.get("title", "Unknown"),
                        "duration": res.get("duration", 0),
                        "uploader": res.get("uploader", "Unknown"),
                        "thumbnail": res.get("thumbnail")
                    })
                return parsed_results
        except Exception as e:
            logger.error(f"YukiAPI search_multiple failed: {e}")
            # Fallback: yt-dlp
            return await self._fallback_search_multiple(query, limit)

    async def get_stream(self, video_id: str):
        """Get direct stream URL by video ID."""
        try:
            async with YukiAPI() as yuki:
                # YukiAPI can take video_id or URL
                stream_url = await yuki.get_stream(video_id, type="audio")
                # Details nikalne ke liye
                title, dur_min, dur_sec, thumb, vidid = await yuki.details(video_id)
                duration = (int(dur_min) * 60) + int(dur_sec)
                
                return {
                    "id": vidid,
                    "title": title,
                    "duration": duration,
                    "stream_url": stream_url,
                    "thumbnail": thumb,
                    "uploader": "YukiAPI",
                    "file_path": cache_manager.get_cached_file(vidid)
                }
        except Exception as e:
            logger.error(f"YukiAPI get_stream failed: {e}")
            return await self._fallback_get_stream(video_id)

    async def search_and_extract(self, query: str, platform="yt"):
        # Compatibility method for older code
        results = await self.search_multiple(query, limit=1)
        if results:
            return await self.get_stream(results[0]["id"])
        return None

    async def download_media(self, video_id: str, is_video=False):
        try:
            async with YukiAPI() as yuki:
                file_path = await yuki.download(
                    video_id,
                    type="video" if is_video else "audio",
                    output_dir=settings.CACHE_DIR
                )
                return file_path
        except Exception as e:
            logger.error(f"YukiAPI download failed: {e}")
            return None

    # ── FALLBACK METHODS (Using yt-dlp) ──
    async def _fallback_search_multiple(self, query: str, limit=5):
        try:
            import yt_dlp
            YDL_OPTS = {
                "format": "bestaudio/best",
                "quiet": True,
                "noplaylist": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "extractor_args": {"youtube": {"player_client": ["android_vr"]}},
                "js_runtimes": {"node": {}},
                "remote_components": ["ejs:github"],
            }
            def _extract():
                ydl = yt_dlp.YoutubeDL(YDL_OPTS)
                info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
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
            return await asyncio.to_thread(_extract)
        except Exception as e:
            logger.error(f"Fallback search_multiple failed: {e}")
            return []

    async def _fallback_get_stream(self, video_id: str):
        try:
            import yt_dlp
            YDL_OPTS = {
                "format": "bestaudio/best",
                "quiet": True,
                "noplaylist": True,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "extractor_args": {"youtube": {"player_client": ["android_vr"]}},
                "js_runtimes": {"node": {}},
                "remote_components": ["ejs:github"],
            }
            def _extract():
                ydl = yt_dlp.YoutubeDL(YDL_OPTS)
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                return {
                    "id": info.get("id"),
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "stream_url": info.get("url"),
                    "thumbnail": info.get("thumbnail"),
                    "uploader": info.get("uploader", "Unknown"),
                    "file_path": None
                }
            return await asyncio.to_thread(_extract)
        except Exception as e:
            logger.error(f"Fallback get_stream failed: {e}")
            return None

downloader = Downloader()
