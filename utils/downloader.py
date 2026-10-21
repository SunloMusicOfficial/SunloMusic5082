import asyncio
import aiohttp
import yt_dlp
from utils.logger import get_logger

logger = get_logger("Downloader")

# 🔥 AAPKA SNAPDEPLOY COBALT API URL
SUNLO_CUSTOM_API = "https://cobalt-658d8.containers.snapdeploy.app" 

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_id = None
        title = "Unknown"
        duration = 0
        thumbnail = None

        # 1. Video ID nikaalo
        if not query.startswith("http"):
            # Try yt-dlp search first
            try:
                ydl_opts = {"quiet": True, "extract_flat": True, "default_search": "ytsearch1", "extractor_args": {"youtube": {"player_client": ["ios", "android"]}}}
                ydl = yt_dlp.YoutubeDL(ydl_opts)
                info = ydl.extract_info(query, download=False)
                if "entries" in info and info["entries"]:
                    info = info["entries"][0]
                    video_id = info.get("id")
                    title = info.get("title", query)
                    duration = info.get("duration", 0)
                    thumbnail = info.get("thumbnail")
            except Exception as e:
                logger.warning(f"yt-dlp search failed: {e}. Trying Invidious search...")
            
            # Fallback: Invidious API for search (Bypasses Render IP block for search)
            if not video_id:
                invidious_instances = ["https://inv.nadeko.net", "https://invidious.nerdvpn.de", "https://iv.melmac.space"]
                async with aiohttp.ClientSession() as session:
                    for base in invidious_instances:
                        try:
                            async with session.get(f"{base}/api/v1/search?q={query}&type=video", timeout=10) as resp:
                                if resp.status == 200:
                                    data = await resp.json()
                                    if data and len(data) > 0:
                                        video_id = data[0].get("videoId")
                                        title = data[0].get("title", query)
                                        duration = data[0].get("lengthSeconds", 0)
                                        thumbnail = data[0].get("videoThumbnails", [{}])[-1].get("url")
                                        logger.info(f"✅ Search success via Invidious: {title}")
                                        break
                        except: pass
        else:
            # Direct link
            video_id = query.split("v=")[-1].split("&")[0] if "v=" in query else query.split("/")[-1]
            title, duration, thumbnail = query, 0, None

        if not video_id:
            logger.error("❌ Could not find video ID from any search method.")
            return None

        # 2. Cobalt API se direct stream URL maango
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{SUNLO_CUSTOM_API}/api/json", 
                    json={"url": f"https://youtube.com/watch?v={video_id}", "isAudioOnly": True},
                    timeout=20
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") in ["stream", "redirect", "tunnel"]:
                            logger.info(f"✅ Cobalt API Success: {title}")
                            return {
                                "id": video_id, 
                                "title": title, 
                                "duration": duration,
                                "thumbnail": thumbnail, 
                                "stream_url": data["url"], 
                                "uploader": "CobaltAPI"
                            }
                    else:
                        logger.error(f"Cobalt API Error Status: {resp.status} - {await resp.text()}")
        except Exception as e:
            logger.error(f"Cobalt API Connection failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
