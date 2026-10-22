import asyncio
import yt_dlp
import os
import time
import subprocess
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("Downloader")

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_url = query
        title = query
        duration = 0
        video_id = None
        
        if not query.startswith("http"):
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
            except Exception as e:
                logger.warning(f"⚠️ Search failed: {e}")
                
        if query.startswith("http"):
            video_id = query.split("v=")[-1].split("&")[0]

        api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
        api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")

        if api_url and api_key:
            try:
                import aiohttp
                os.makedirs("cache", exist_ok=True)
                timestamp = int(time.time())
                
                async with aiohttp.ClientSession() as session:
                    payload = {"url": video_url, "q": query, "api_key": api_key, "type": "audio"}
                    async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=60) as resp:
                        if resp.status == 200:
                            content_type = resp.headers.get("Content-Type", "")
                            if "application/json" in content_type:
                                data = await resp.json()
                                stream_url = data.get("url") or data.get("link") or data.get("download_url")
                                if stream_url:
                                    # 🔥 FIX: Use API's title and thumbnail to match the audio
                                    return {
                                        "id": video_id or query, 
                                        "title": data.get("title", title), 
                                        "duration": data.get("duration", duration), 
                                        "stream_url": stream_url, 
                                        "thumbnail": data.get("thumbnail", f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None), 
                                        "uploader": "API"
                                    }
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                if os.path.exists(file_path) and os.path.getsize(file_path) > 50000:
                                    return {"id": video_id or query, "title": title, "duration": duration, "stream_url": file_path, "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None, "uploader": "API File"}
                                else:
                                    if os.path.exists(file_path): os.remove(file_path)
            except Exception as e:
                logger.error(f"❌ API failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
