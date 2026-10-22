
import asyncio
import aiohttp
import yt_dlp
import os
import time
import re
import json
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

        # 1. YouTube Search via ytInitialData (Accurate & No yt-dlp block)
        if not query.startswith("http"):
            logger.info(f"🔍 Scraping YouTube for: {query}")
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, headers=headers, timeout=10) as resp:
                        html = await resp.text()
                        
                        # Extract ytInitialData JSON
                        match = re.search(r'var ytInitialData = ({.*?});</script>', html, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            
                            # Function to find the first videoRenderer object
                            def find_video(obj):
                                if isinstance(obj, dict):
                                    if "videoRenderer" in obj:
                                        return obj["videoRenderer"]
                                    for k, v in obj.items():
                                        res = find_video(v)
                                        if res: return res
                                elif isinstance(obj, list):
                                    for item in obj:
                                        res = find_video(item)
                                        if res: return res
                                return None
                            
                            renderer = find_video(data)
                            if renderer:
                                video_id = renderer["videoId"]
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                title = renderer["title"]["runs"][0]["text"]
                                
                                # Extract Duration
                                if "lengthText" in renderer:
                                    dur_str = renderer["lengthText"]["simpleText"]
                                    parts = list(map(int, dur_str.split(":")))
                                    if len(parts) == 2: duration = parts[0]*60 + parts[1]
                                    elif len(parts) == 3: duration = parts[0]*3600 + parts[1]*60 + parts[2]
                                
                                # Extract Thumbnail
                                thumbnails = renderer.get("thumbnail", {}).get("thumbnails", [])
                                if thumbnails:
                                    thumbnail = thumbnails[-1]["url"]
                                
                                logger.info(f"✅ Found URL: {video_url} | Title: {title} | Dur: {duration}s")
                        else:
                            logger.warning("⚠️ Could not parse ytInitialData, fallback to simple regex.")
                            fallback = re.search(r'watch\?v=([a-zA-Z0-9_-]{11})', html)
                            if fallback:
                                video_url = f"https://www.youtube.com/watch?v={fallback.group(1)}"
            except Exception as e:
                logger.warning(f"⚠️ Web Scraper failed: {e}")

        if "None" in video_url or video_url == query:
            logger.error("❌ Could not find proper video URL.")
            return None

        # 2. API Call
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
                            
                            if "application/json" in content_type:
                                data = await resp.json()
                                stream_url = data.get("url") or data.get("link") or data.get("download_url")
                                if stream_url:
                                    return {
                                        "id": video_id, 
                                        "title": data.get("title", title), 
                                        "duration": data.get("duration", duration), 
                                        "stream_url": stream_url, 
                                        "thumbnail": data.get("thumbnail", thumbnail), 
                                        "uploader": "API"
                                    }
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                
                                logger.info(f"📥 Saving API file as {ext}...")
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                logger.info(f"✅ Saved: {file_path}")
                                return {
                                    "id": video_id, 
                                    "title": title, # Ab sahi title aayega
                                    "duration": duration, # Ab sahi timer chalega
                                    "stream_url": file_path,
                                    "thumbnail": thumbnail, # Ab thumbnail aayega
                                    "uploader": "API File"
                                }
                        else:
                            logger.error(f"❌ API error {resp.status}: {await resp.text()}")
            except Exception as e:
                logger.error(f"❌ API Request failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
