import asyncio
from yukiapi import YukiAPI
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        try:
            async with YukiAPI() as yuki:
                # 1. Details fetch karo (title, duration, thumbnail, video_id)
                title, dur_min, dur_sec, thumb, vidid = await yuki.details(query)
                duration = (int(dur_min) * 60) + int(dur_sec)

                # 2. Direct stream URL nikaalo (PyTgCalls ke liye ready)
                stream_url = await yuki.get_stream(query, type="audio")

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
            logger.error(f"YukiAPI search_and_extract failed: {e}")
            # Fallback: agar YukiAPI fail ho jaye toh yt-dlp try karo (optional)
            return await self._fallback_search(query, platform)

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

    async def _fallback_search(self, query: str, platform="yt"):
        """Agar YukiAPI kaam na kare toh purana yt-dlp use karega."""
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
                search_query = query if query.startswith("http") else f"ytsearch1:{query}"
                info = ydl.extract_info(search_query, download=False)
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
            return await asyncio.to_thread(_extract)
        except Exception as e:
            logger.error(f"Fallback yt-dlp failed: {e}")
            return None

downloader = Downloader()
