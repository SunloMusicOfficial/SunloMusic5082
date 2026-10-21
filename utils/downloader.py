import asyncio
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs

import aiohttp
import yt_dlp

from config.settings import settings
from database.cookies import get_active_cookies
from utils.logger import get_logger

logger = get_logger("SunloMusicDownloader")


class Downloader:
    def __init__(self):
        self._download_lock = asyncio.Semaphore(
            max(1, settings.DOWNLOAD_WORKERS)
        )

    # --------------------------------------------------
    # GENERAL HELPERS
    # --------------------------------------------------

    def _cache_dir(self):
        path = Path(settings.CACHE_DIR).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _normalise_query(query):
        return str(query or "").strip()

    @staticmethod
    def _youtube_id(query):
        query = str(query or "").strip()

        if len(query) == 11 and all(
            char.isalnum() or char in "_-" for char in query
        ):
            return query

        try:
            parsed = urlparse(query)
            host = (parsed.hostname or "").lower()

            if host == "youtu.be":
                video_id = parsed.path.strip("/").split("/")[0]
                return video_id or None

            if host == "youtube.com" or host.endswith(".youtube.com"):
                if parsed.path == "/watch":
                    return parse_qs(parsed.query).get("v", [None])[0]

                parts = parsed.path.strip("/").split("/")

                if len(parts) >= 2 and parts[0] in (
                    "shorts", "embed", "live"
                ):
                    return parts[1]

        except Exception:
            pass

        return None

    @staticmethod
    def _youtube_url(query):
        query = str(query or "").strip()
        video_id = Downloader._youtube_id(query)

        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"

        return query

    @staticmethod
    def _is_youtube_url(query):
        try:
            host = (urlparse(str(query)).hostname or "").lower()
            return (
                host == "youtu.be"
                or host == "youtube.com"
                or host.endswith(".youtube.com")
            )
        except Exception:
            return False

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    async def search_multiple(self, query: str, limit=5):
        """Search YouTube and return a list of song results."""
        query = self._normalise_query(query)

        if not query:
            return []

        try:
            limit = max(1, min(int(limit), 10))
        except (ValueError, TypeError):
            limit = 5

        try:
            return await asyncio.to_thread(
                self._search_sync, query, limit
            )
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("SunloMusic search failed: %s", exc)
            return []

    def _search_sync(self, query, limit):
        search_query = query

        if not self._is_youtube_url(query) and not self._youtube_id(query):
            search_query = f"ytsearch{limit}:{query}"
        else:
            search_query = self._youtube_url(query)

        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "extract_flat": True,
            "socket_timeout": 20,
            "retries": 2,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            data = ydl.extract_info(search_query, download=False)

        if not data:
            return []

        entries = data.get("entries")
        if entries is None:
            entries = [data]

        results = []

        for item in entries:
            if not item:
                continue

            video_id = str(item.get("id") or "")
            if not video_id:
                continue

            webpage_url = (
                item.get("webpage_url")
                or f"https://www.youtube.com/watch?v={video_id}"
            )

            results.append({
                "id": video_id,
                "title": item.get("title") or "Unknown",
                "duration": item.get("duration") or 0,
                "stream_url": item.get("url"),
                "thumbnail": item.get("thumbnail"),
                "uploader": item.get("uploader") or "YouTube",
                "webpage_url": webpage_url,
            })

            if len(results) >= limit:
                break

        return results

    async def search_and_extract(self, query: str, platform="yt"):
        """
        Keep compatibility with /play, AI DJ and multi-downloader.
        Search is handled by yt-dlp; download is a separate operation.
        """
        query = self._normalise_query(query)

        if not query:
            return None

        results = await self.search_multiple(query, limit=1)

        if results:
            return results[0]

        # Last attempt for direct URLs or video IDs.
        try:
            return await self._ytdlp_fallback(query)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Metadata extraction failed: %s", exc)
            return None

    # --------------------------------------------------
    # DIRECT METADATA EXTRACTION
    # --------------------------------------------------

    async def _ytdlp_fallback(self, query):
        query = self._normalise_query(query)

        if not query:
            return None

        cookie_path = None

        try:
            cookies = await get_active_cookies()

            if cookies:
                cookie_data = cookies[0].get("data", "")

                if cookie_data:
                    fd, cookie_path = tempfile.mkstemp(suffix=".txt")

                    with os.fdopen(fd, "w", encoding="utf-8") as file:
                        file.write(cookie_data)

            return await asyncio.to_thread(
                self._extract_sync, query, cookie_path
            )

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("Metadata fallback failed: %s", exc)
            return None

        finally:
            if cookie_path and os.path.exists(cookie_path):
                try:
                    os.remove(cookie_path)
                except OSError:
                    pass

    def _extract_sync(self, query, cookie_path=None):
        query = self._youtube_url(query)

        options = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "default_search": "ytsearch1",
            "socket_timeout": 20,
            "retries": 2,
        }

        if cookie_path:
            options["cookiefile"] = cookie_path

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(query, download=False)

        if info and info.get("entries") is not None:
            entries = info.get("entries") or []
            info = next((entry for entry in entries if entry), None)

        if not info:
            return None

        video_id = str(info.get("id") or "")

        return {
            "id": video_id,
            "title": info.get("title") or "Unknown",
            "duration": info.get("duration") or 0,
            "stream_url": info.get("url"),
            "thumbnail": info.get("thumbnail"),
            "uploader": info.get("uploader") or "YouTube",
            "webpage_url": (
                info.get("webpage_url")
                or (
                    f"https://www.youtube.com/watch?v={video_id}"
                    if video_id else None
                )
            ),
        }

    # --------------------------------------------------
    # SUNLOMUSIC API DOWNLOAD
    # --------------------------------------------------

    async def _download_from_api(self, source, output_path, is_video=False):
        api_key = settings.SUNLO_DOWNLOAD_API_KEY

        if not api_key:
            logger.info("SunloMusic API key is not configured.")
            return None

        source = self._youtube_url(source)

        if not self._is_youtube_url(source):
            return None

        params = {
            "url": source,
            "type": "video" if is_video else "audio",
            "api_key": api_key,
        }

        timeout = aiohttp.ClientTimeout(
            total=180,
            connect=20,
            sock_read=90,
        )

        temporary_path = str(output_path) + ".part"

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    f"{settings.SUNLO_DOWNLOAD_API_URL}/download",
                    params=params,
                ) as response:

                    if response.status != 200:
                        # Do not print the request URL: it contains the key.
                        error = await response.text()
                        logger.warning(
                            "SunloMusic download API returned HTTP %s: %s",
                            response.status,
                            error[:200],
                        )
                        return None

                    content_type = response.headers.get(
                        "Content-Type", ""
                    ).lower()

                    # The verified API returns raw media bytes.
                    # Reject JSON/HTML responses instead of saving them as audio.
                    if (
                        "json" in content_type
                        or "text/html" in content_type
                    ):
                        logger.warning(
                            "SunloMusic download API returned a non-media response."
                        )
                        return None

                    bytes_written = 0

                    with open(temporary_path, "wb") as output:
                        async for chunk in response.content.iter_chunked(
                            256 * 1024
                        ):
                            if chunk:
                                output.write(chunk)
                                bytes_written += len(chunk)

                    if bytes_written == 0:
                        logger.warning("Download API returned an empty file.")
                        return None

            os.replace(temporary_path, output_path)

            logger.info(
                "SunloMusic download completed: %s (%s bytes)",
                output_path.name,
                bytes_written,
            )

            return str(output_path)

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("SunloMusic API download failed: %s", exc)
            return None

        finally:
            if os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass

    # --------------------------------------------------
    # YT-DLP DOWNLOAD FALLBACK
    # --------------------------------------------------

    async def _download_with_ytdlp(self, source, is_video=False):
        cookie_path = None

        try:
            cookies = await get_active_cookies()

            if cookies:
                cookie_data = cookies[0].get("data", "")

                if cookie_data:
                    fd, cookie_path = tempfile.mkstemp(suffix=".txt")

                    with os.fdopen(fd, "w", encoding="utf-8") as file:
                        file.write(cookie_data)

            return await asyncio.to_thread(
                self._download_sync,
                source,
                is_video,
                cookie_path,
            )

        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error("yt-dlp download fallback failed: %s", exc)
            return None

        finally:
            if cookie_path and os.path.exists(cookie_path):
                try:
                    os.remove(cookie_path)
                except OSError:
                    pass

    def _download_sync(self, source, is_video=False, cookie_path=None):
        cache_dir = self._cache_dir()
        source = self._youtube_url(source)

        options = {
            "format": (
                "best[ext=mp4]/best"
                if is_video
                else "bestaudio/best"
            ),
            "outtmpl": str(cache_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "socket_timeout": 25,
            "retries": 2,
            "overwrites": False,
        }

        if cookie_path:
            options["cookiefile"] = cookie_path

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(source, download=True)

            if info and info.get("entries") is not None:
                entries = info.get("entries") or []
                info = next((entry for entry in entries if entry), None)

            if not info:
                return None

            filename = ydl.prepare_filename(info)
            path = Path(filename)

            if path.is_file() and path.stat().st_size > 0:
                return str(path)

            video_id = str(info.get("id") or "")
            if video_id:
                for candidate in cache_dir.glob(f"{video_id}.*"):
                    if (
                        candidate.is_file()
                        and not candidate.name.endswith(".part")
                        and candidate.stat().st_size > 0
                    ):
                        return str(candidate)

        return None

    # --------------------------------------------------
    # PUBLIC DOWNLOAD METHOD
    # --------------------------------------------------

    async def download_media(self, query, is_video=False):
        """
        Download media and return a local file path.
        Compatible with plugins/downloads.py and multi_downloader.py.
        """
        query = self._normalise_query(query)

        if not query:
            return None

        video_id = self._youtube_id(query)
        cache_dir = self._cache_dir()

        if video_id:
            filename = (
                f"{video_id}_video.mp4"
                if is_video
                else f"{video_id}_sunlo.m4a"
            )
            output_path = cache_dir / filename
        else:
            output_path = None

        if (
            output_path
            and output_path.is_file()
            and output_path.stat().st_size > 0
        ):
            return str(output_path)

        async with self._download_lock:
            if (
                output_path
                and output_path.is_file()
                and output_path.stat().st_size > 0
            ):
                return str(output_path)

            # Use the API only when the input is a YouTube ID/URL.
            if output_path is not None:
                result = await self._download_from_api(
                    query,
                    output_path,
                    is_video=is_video,
                )

                if result:
                    return result

            # API key missing or API failed: preserve yt-dlp fallback.
            logger.info("Trying SunloMusic yt-dlp fallback.")

            return await self._download_with_ytdlp(
                query,
                is_video=is_video,
            )

    # --------------------------------------------------
    # VOICE-CHAT PLAYBACK
    # --------------------------------------------------

    async def get_stream(self, video_id: str):
        """
        Resolve metadata, download a local audio file and return
        a song dictionary whose stream_url points to that file.
        """
        video_id = self._normalise_query(video_id)

        if not video_id:
            return None

        song = await self._ytdlp_fallback(
            self._youtube_url(video_id)
        )

        if not song:
            song = await self.search_and_extract(video_id)

        if not song:
            return None

        source = (
            song.get("webpage_url")
            or song.get("id")
            or video_id
        )

        file_path = await self.download_media(
            source,
            is_video=False,
        )

        if not file_path or not os.path.isfile(file_path):
            logger.error("SunloMusic could not obtain the audio file.")
            return None

        song["file_path"] = file_path
        song["stream_url"] = file_path

        return song


downloader = Downloader()
