import asyncio
import aiohttp
import yt_dlp
import os
import time
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_url = query
        title = query
        duration = 0
        thumbnail = None

        # 1. YouTube Search (Metadata ke saath)
        if not query.startswith("http"):
            logger.info(f"🔍 Searching YouTube for: {query}")
            try:
                # extract_flat=False se duration aur thumbnail milta hai
                ydl_opts = {"quiet": True, "extract_flat": False, "default_search": "ytsearch1"}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 'audio' add kiya taaki search result mein gaana aaye
                    info = ydl.extract_info(f"ytsearch1:{query} audio", download=False)
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                        if entry.get("id"):
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            title = entry.get("title", query)
                            duration = entry.get("duration", 0)
                            # Best thumbnail uthao
                            thumbnails = entry.get("thumbnails", [])
                            if thumbnails:
                                thumbnail = thumbnails[-1].get("url")
                            else:
                                thumbnail = entry.get("thumbnail")
                            logger.info(f"✅ Found URL: {video_url} | Duration: {duration}s")
            except Exception as e:
                logger.error(f"❌ Search failed: {e}")

        if "None" in video_url:
            return None

        # 2. API Call
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            logger.info(f"🚀 Requesting Audio File from API for: {video_url}")
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
                            
                            # Agar API direct file (audio/mp4) return kare
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                
                                logger.info(f"📥 API returned direct file ({content_type}). Saving as {ext}...")
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                logger.info(f"✅ Audio file saved to: {file_path}")
                                
                                # 🔥 FIX: Ab hum yt-dlp wala duration aur thumbnail return kar rahe hain
                                return {
                                    "id": video_url.split("v=")[-1], 
                                    "title": title, 
                                    "duration": duration, 
                                    "stream_url": file_path,
                                    "thumbnail": thumbnail, 
                                    "uploader": "API File"
                                }
                        else:
                            logger.error(f"❌ API returned error status: {resp.status}")
                            
            except asyncio.TimeoutError:
                logger.error("❌ API Timeout after 40 seconds.")
            except Exception as e:
                logger.error(f"❌ API Request failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
