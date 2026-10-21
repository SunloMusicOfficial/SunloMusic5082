import asyncio
import aiohttp
import yt_dlp
import os
import tempfile
from utils.logger import get_logger
from config.settings import settings
from database.cookies import get_active_cookies, mark_cookie_success

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_url = query
        title = query
        duration = 0
        thumbnail = None

        # 1. Search for YouTube URL (Agar direct link nahi hai)
        if not query.startswith("http"):
            logger.info(f"🔍 Searching YouTube for: {query}")
            try:
                ydl_opts = {
                    "quiet": True,
                    "extract_flat": True,
                    "default_search": "ytsearch1",
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if "entries" in info and info["entries"]:
                        entry = info["entries"][0]
                        if entry.get("id"):
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                            title = entry.get("title", query)
                            thumbnail = entry.get("thumbnail")
                            logger.info(f"✅ Found URL: {video_url}")
                        else:
                            logger.error("❌ Search returned empty ID.")
                    else:
                        logger.error("❌ No search results found.")
            except Exception as e:
                logger.error(f"❌ Search failed: {e}")

        if "None" in video_url:
             return None

        # 2. API Call
        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            logger.info(f"🚀 Calling API for: {video_url}")
            try:
                async with aiohttp.ClientSession() as session:
                    # 🔥 YAHAN FIX: type='audio' add kiya hai
                    payload = {
                        "url": video_url, 
                        "api_key": api_key,
                        "type": "audio" 
                    }
                    
                    async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=20) as resp:
                        response_text = await resp.text()
                        logger.info(f"📥 API Status: {resp.status} | Response: {response_text[:300]}")
                        
                        if resp.status == 200:
                            try:
                                data = await resp.json()
                                # Har possible key check kar raha hai link ke liye
                                stream_url = (
                                    data.get("url") or data.get("link") or 
                                    data.get("download_url") or data.get("downloadUrl") or
                                    (data.get("data") and isinstance(data.get("data"), dict) and data["data"].get("url"))
                                )
                                
                                if stream_url:
                                    logger.info("✅ Found Stream URL from API!")
                                    return {
                                        "id": video_url.split("v=")[-1],
                                        "title": data.get("title", title),
                                        "duration": data.get("duration", duration),
                                        "stream_url": stream_url,
                                        "thumbnail": data.get("thumbnail", thumbnail),
                                        "uploader": "API"
                                    }
                            except Exception as e:
                                logger.error(f"❌ Parse Error: {e}")
            except Exception as e:
                logger.error(f"❌ API Connection failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
