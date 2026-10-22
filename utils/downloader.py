import asyncio
import aiohttp
import yt_dlp
import os
import time
import re
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_url = query
        title = query
        duration = 0
        thumbnail = None

        # 1. YouTube URL nikaalo (Bina yt-dlp ke, taaki block na ho)
        if not query.startswith("http"):
            logger.info(f"🔍 Scraping YouTube for: {query}")
            
            # Try 1: Direct Web Scraper (Sabse Fast & Block-Free)
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, headers=headers, timeout=10) as resp:
                        html = await resp.text()
                        match = re.search(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
                        if match:
                            video_id = match.group(1)
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            logger.info(f"✅ Found URL via Web Scraper: {video_url}")
            except Exception as e:
                logger.warning(f"⚠️ Web Scraper failed: {e}")

            # Try 2: yt-dlp search (Agar scraper fail ho jaye)
            if video_url == query:
                cookies = await get_active_cookies()
                cookie_path = None
                if cookies:
                    temp_fd, cookie_path = tempfile.mkstemp(suffix=".txt")
                    with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
                        f.write(cookies[0]["data"])

                try:
                    ydl_opts = {"quiet": True, "extract_flat": True, "default_search": "ytsearch1"}
                    if cookie_path:
                        ydl_opts["cookiefile"] = cookie_path

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                        if "entries" in info and info["entries"]:
                            entry = info["entries"][0]
                            if entry.get("id"):
                                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                                logger.info(f"✅ Found URL via yt-dlp: {video_url}")
                except Exception as e:
                    logger.warning(f"⚠️ yt-dlp search failed: {e}")
                finally:
                    if cookie_path and os.path.exists(cookie_path):
                        os.remove(cookie_path)

            # Agar dono fail ho gaye
            if video_url == query:
                logger.error("❌ Could not find video URL.")
                return None

        # 2. API ko Sahi URL bhejo
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            logger.info(f"🚀 Requesting API for URL: {video_url}")
            try:
                os.makedirs("cache", exist_ok=True)
                timestamp = int(time.time())
                
                async with aiohttp.ClientSession() as session:
                    payload = {"url": video_url, "api_key": api_key, "type": "audio"}
                    
                    async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=40) as resp:
                        if resp.status == 200:
                            content_type = resp.headers.get("Content-Type", "")
                            
                            # Agar API JSON return kare
                            if "application/json" in content_type:
                                data = await resp.json()
                                stream_url = data.get("url") or data.get("link") or data.get("download_url")
                                if stream_url:
                                    logger.info("✅ Found Stream URL from JSON API")
                                    return {
                                        "id": video_url.split("v=")[-1], 
                                        "title": data.get("title", title), 
                                        "duration": data.get("duration", duration), 
                                        "stream_url": stream_url, 
                                        "thumbnail": data.get("thumbnail", thumbnail), 
                                        "uploader": "API"
                                    }
                            
                            # Agar API direct file return kare
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                
                                logger.info(f"📥 Saving API file as {ext}...")
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                logger.info(f"✅ Saved: {file_path}")
                                return {
                                    "id": video_url.split("v=")[-1], 
                                    "title": title, 
                                    "duration": duration, 
                                    "stream_url": file_path,
                                    "thumbnail": thumbnail, 
                                    "uploader": "API File"
                                }
                        else:
                            error_text = await resp.text()
                            logger.error(f"❌ API error {resp.status}: {error_text[:100]}")
                            
            except asyncio.TimeoutError:
                logger.error("❌ API Timeout.")
            except Exception as e:
                logger.error(f"❌ API failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
