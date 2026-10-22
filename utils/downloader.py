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
        video_id = None

        # 1. Use yt-dlp search (Lightweight, bypasses simple IP blocks)
        if not query.startswith("http"):
            logger.info(f"🔍 Searching for: {query}")
            try:
                ydl_opts = {"quiet": True, "extract_flat": True, "default_search": "ytsearch1"}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                        if entry.get("id"):
                            video_id = entry["id"]
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            title = entry.get("title", query)
                            duration = entry.get("duration", 0)
                            logger.info(f"✅ Found URL: {video_url}")
            except Exception as e:
                logger.warning(f"⚠️ yt-dlp search failed: {e}")

        if query.startswith("http"):
            video_id = query.split("v=")[-1].split("&")[0]

        # Agar video_id nahi mila, toh API ko raw query bhejenge
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            logger.info(f"🚀 Requesting API for: {video_url}")
            try:
                os.makedirs("cache", exist_ok=True)
                timestamp = int(time.time())
                
                async with aiohttp.ClientSession() as session:
                    # API ko dono (url aur q) bhej rahe hain taaki jo bhi support kare kaam kare
                    payload = {"url": video_url, "q": query, "api_key": api_key, "type": "audio"}
                    
                    async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=40) as resp:
                        if resp.status == 200:
                            content_type = resp.headers.get("Content-Type", "")
                            
                            if "application/json" in content_type:
                                data = await resp.json()
                                stream_url = data.get("url") or data.get("link") or data.get("download_url")
                                if stream_url:
                                    return {"id": video_id or query, "title": data.get("title", title), "duration": data.get("duration", duration), "stream_url": stream_url, "thumbnail": data.get("thumbnail", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None), "uploader": "API"}
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                logger.info(f"✅ Saved: {file_path}")
                                return {
                                    "id": video_id or query, 
                                    "title": title, 
                                    "duration": duration, 
                                    "stream_url": file_path,
                                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None, 
                                    "uploader": "API File"
                                }
                        else:
                            logger.error(f"❌ API error {resp.status}")
            except Exception as e:
                logger.error(f"❌ API failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
