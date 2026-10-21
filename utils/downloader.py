import asyncio
import aiohttp
from utils.logger import get_logger
from utils.cache import cache_manager
from config.settings import settings

logger = get_logger("Downloader")

# Piped API instances (fallback ke liye)
PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://api.piped.private.coffee",
    "https://pipedapi.reallyaweso.me"
]

class Downloader:
    async def _fetch_piped(self, endpoint: str):
        """Try multiple Piped instances until one works."""
        for base in PIPED_INSTANCES:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{base}{endpoint}", timeout=10) as resp:
                        if resp.status == 200:
                            return await resp.json()
            except Exception as e:
                logger.warning(f"Piped instance {base} failed: {e}")
                continue
        return None

    async def search_multiple(self, query: str, limit=5):
        """Search top X results using Piped API."""
        try:
            data = await self._fetch_piped(f"/search?q={query}&filter=music_songs")
            if not data or "items" not in data:
                return []

            results = []
            for item in data["items"][:limit]:
                results.append({
                    "id": item.get("url", "").replace("/watch?v=", ""),
                    "title": item.get("title", "Unknown"),
                    "duration": item.get("duration", 0),
                    "uploader": item.get("uploaderName", "Unknown"),
                    "thumbnail": item.get("thumbnail")
                })
            return results
        except Exception as e:
            logger.error(f"Piped search failed: {e}")
            return []

    async def get_stream(self, video_id: str):
        """Get direct stream URL from Piped API."""
        try:
            data = await self._fetch_piped(f"/streams/{video_id}")
            if not data or "audioStreams" not in data:
                return None

            # Best audio stream chuno
            audio_streams = data.get("audioStreams", [])
            best_audio = None
            for stream in audio_streams:
                if stream.get("mimeType", "").startswith("audio"):
                    best_audio = stream
                    break

            if not best_audio:
                return None

            return {
                "id": video_id,
                "title": data.get("title", "Unknown"),
                "duration": data.get("duration", 0),
                "stream_url": best_audio.get("url"),
                "thumbnail": data.get("thumbnailUrl"),
                "uploader": data.get("uploader", "Unknown"),
                "file_path": cache_manager.get_cached_file(video_id)
            }
        except Exception as e:
            logger.error(f"Piped get_stream failed: {e}")
            return None

    async def search_and_extract(self, query: str, platform="yt"):
        results = await self.search_multiple(query, limit=1)
        if results:
            return await self.get_stream(results[0]["id"])
        return None

    async def download_media(self, video_id: str, is_video=False):
        """Piped se download karne ke liye (optional)."""
        try:
            # Piped API directly download support nahi karta, isliye yt-dlp fallback
            import yt_dlp
            ydl_opts = {
                "format": "bestaudio/best" if not is_video else "best[ext=mp4]/best",
                "quiet": True,
                "outtmpl": f"{settings.CACHE_DIR}/%(id)s.%(ext)s",
            }
            ydl = yt_dlp.YoutubeDL(ydl_opts)
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)
            return cache_manager.add_to_cache(ydl.prepare_filename(info), video_id, "mp4" if is_video else "mp3")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None

downloader = Downloader()
