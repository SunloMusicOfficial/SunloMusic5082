import asyncio
import aiohttp
import yt_dlp
from utils.logger import get_logger

logger = get_logger("Downloader")

SUNLO_CUSTOM_API = "https://cobalt-658d8.containers.snapdeploy.app"

class Downloader:
    async def search_and_extract(self, query: str, platform="yt"):
        video_id = None
        title = "Unknown"
        duration = 0
        thumbnail = None

        # 1. Search for Video ID
        if not query.startswith("http"):
            logger.info(f"🔍 Searching for: {query}")
            
            # Try Piped API for search (Very reliable, no IP block)
            piped_instances = ["https://pipedapi.kavin.rocks", "https://pipedapi.adminforge.de", "https://api.piped.yt"]
            async with aiohttp.ClientSession() as session:
                for base in piped_instances:
                    try:
                        async with session.get(f"{base}/search?q={query}&filter=videos", timeout=5) as resp:
                            if resp.status == 200:
                                data = await resp.json()
                                if data.get("items"):
                                    item = data["items"][0]
                                    video_id = item.get("url", "").replace("/watch?v=", "")
                                    title = item.get("title", query)
                                    duration = item.get("duration", 0)
                                    thumbnail = item.get("thumbnail")
                                    logger.info(f"✅ Piped Search Success: {title}")
                                    break
                    except Exception as e:
                        logger.warning(f"Piped instance {base} failed: {e}")

            # Fallback to yt-dlp if Piped fails
            if not video_id:
                logger.info("🔄 Piped failed, trying yt-dlp search...")
                try:
                    ydl_opts = {"quiet": True, "extract_flat": True, "default_search": "ytsearch1"}
                    ydl = yt_dlp.YoutubeDL(ydl_opts)
                    info = ydl.extract_info(query, download=False)
                    if "entries" in info and info["entries"]:
                        info = info["entries"][0]
                        video_id = info.get("id")
                        title = info.get("title", query)
                        duration = info.get("duration", 0)
                        thumbnail = info.get("thumbnail")
                        logger.info(f"✅ yt-dlp Search Success: {title}")
                except Exception as e:
                    logger.error(f"❌ yt-dlp search failed: {e}")
        else:
            video_id = query.split("v=")[-1].split("&")[0] if "v=" in query else query.split("/")[-1]
            title = "YouTube Link"
            logger.info(f"🔗 Direct Link detected: {video_id}")

        if not video_id:
            logger.error("❌ NO VIDEO ID FOUND")
            return None

        # 2. Call Cobalt API
        logger.info(f"📡 Calling Cobalt API for Video ID: {video_id}")
        try:
            async with aiohttp.ClientSession() as session:
                # Cobalt V10 requires specific JSON payload and headers
                payload = {"url": f"https://youtube.com/watch?v={video_id}", "isAudioOnly": True}
                headers = {"Accept": "application/json", "Content-Type": "application/json"}
                
                async with session.post(f"{SUNLO_CUSTOM_API}/api/json", json=payload, headers=headers, timeout=20) as resp:
                    response_text = await resp.text()
                    logger.info(f"📥 Cobalt API Response Status: {resp.status}")
                    
                    if resp.status == 200:
                        try:
                            data = await resp.json()
                            logger.info(f"📥 Cobalt API JSON: {data}")
                            
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
                                logger.error(f"❌ Cobalt Status not stream/redirect: {data.get('status')}")
                        except Exception as e:
                            logger.error(f"❌ Failed to parse JSON: {e}. Raw response: {response_text}")
                    else:
                        logger.error(f"❌ Cobalt API Error {resp.status}: {response_text}")
        except Exception as e:
            logger.error(f"❌ Cobalt API Connection failed: {e}")

        return None

    async def get_stream(self, video_id: str):
        return await self.search_and_extract(video_id)

downloader = Downloader()
