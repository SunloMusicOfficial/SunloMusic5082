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
        video_id = None

        # 1. Smart YouTube Search
        if not query.startswith("http"):
            logger.info(f"🔍 Scraping YouTube for: {query}")
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                # Search query me 'song' add kar rahe hain taaki podcast na aaye
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}+song"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, headers=headers, timeout=10) as resp:
                        html = await resp.text()
                        
                        match = re.search(r'var ytInitialData = ({.*?});</script>', html, re.DOTALL)
                        if match:
                            data = json.loads(match.group(1))
                            
                            # Saare videoRenderers nikalo
                            def find_videos(obj, results):
                                if isinstance(obj, dict):
                                    if "videoRenderer" in obj:
                                        results.append(obj["videoRenderer"])
                                    for k, v in obj.items():
                                        find_videos(v, results)
                                elif isinstance(obj, list):
                                    for item in obj:
                                        find_videos(item, results)
                                return results
                            
                            renderers = find_videos(data, [])
                            best_renderer = None
                            
                            for r in renderers:
                                # Duration check karo (15 minute se kam honi chahiye)
                                if "lengthText" in r:
                                    dur_str = r["lengthText"]["simpleText"]
                                    parts = list(map(int, dur_str.split(":")))
                                    dur = 0
                                    if len(parts) == 2: dur = parts[0]*60 + parts[1]
                                    elif len(parts) == 3: dur = parts[0]*3600 + parts[1]*60 + parts[2]
                                    
                                    if 60 < dur < 900: # 1 min se 15 min ke beech
                                        best_renderer = r
                                        break
                            
                            # Agar filter se koi na mile, toh pehla wala utha lo
                            if not best_renderer and renderers:
                                best_renderer = renderers[0]

                            if best_renderer:
                                video_id = best_renderer["videoId"]
                                video_url = f"https://www.youtube.com/watch?v={video_id}"
                                title = best_renderer["title"]["runs"][0]["text"]
                                
                                if "lengthText" in best_renderer:
                                    dur_str = best_renderer["lengthText"]["simpleText"]
                                    parts = list(map(int, dur_str.split(":")))
                                    if len(parts) == 2: duration = parts[0]*60 + parts[1]
                                    elif len(parts) == 3: duration = parts[0]*3600 + parts[1]*60 + parts[2]
                                
                                thumbnails = best_renderer.get("thumbnail", {}).get("thumbnails", [])
                                if thumbnails:
                                    thumbnail = thumbnails[-1]["url"]
                                
                                logger.info(f"✅ Found: {title} | Dur: {duration}s")
            except Exception as e:
                logger.warning(f"⚠️ Web Scraper failed: {e}")

        if not video_id and not query.startswith("http"):
            return None
        elif query.startswith("http"):
            video_id = query.split("v=")[-1].split("&")[0]

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
                                    return {"id": video_id, "title": data.get("title", title), "duration": data.get("duration", duration), "stream_url": stream_url, "thumbnail": data.get("thumbnail", thumbnail), "uploader": "API"}
                            else:
                                ext = ".m4a" if "mp4" in content_type else ".mp3"
                                file_path = f"cache/api_{timestamp}{ext}"
                                
                                with open(file_path, "wb") as f:
                                    async for chunk in resp.content.iter_chunked(65536):
                                        f.write(chunk)
                                
                                logger.info(f"✅ Saved: {file_path}")
                                return {
                                    "id": video_id, 
                                    "title": title, 
                                    "duration": duration, 
                                    "stream_url": file_path,
                                    "thumbnail": thumbnail, 
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
