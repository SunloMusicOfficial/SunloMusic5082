import random
import asyncio
from pytgcalls.types import MediaStream
import core.calls as calls_module
from utils.player_state import get_player_state, delete_active_card
from utils.logger import get_logger
from utils.downloader import downloader

logger = get_logger("QueueManager")
queues = {}
current_songs = {}

async def add_to_queue(chat_id: int, song_data: dict):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song_data)

async def play_next_in_queue(chat_id: int):
    state = get_player_state(chat_id)
    
    if state.get("loop") and chat_id in current_songs:
        next_song = current_songs[chat_id]
    elif state.get("shuffle") and chat_id in queues and queues[chat_id]:
        next_song = random.choice(queues[chat_id])
        queues[chat_id].remove(next_song)
    elif chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id].pop(0)
    else:
        # 🔥 AUTOPLAY LOGIC
        if state.get("autoplay", False):
            logger.info(f"🔄 Autoplay is ON. Fetching random song for {chat_id}...")
            random_queries = ["lofi chill beats", "party dance mix", "trending english songs", "romantic hindi songs", "punjabi hits"]
            query = random.choice(random_queries)
            next_song = await downloader.search_and_extract(query)
            if not next_song:
                logger.warning("Autoplay failed to find song.")
                state["autoplay"] = False # Turn off if failed
        else:
            next_song = None
            
        if not next_song:
            try:
                await asyncio.wait_for(calls_module.calls.leave_call(chat_id), timeout=10)
                await delete_active_card(chat_id)
                if chat_id in current_songs: del current_songs[chat_id]
                logger.info(f"🚪 Left VC (Queue empty) in {chat_id}")
            except Exception as e:
                logger.error(f"Leave VC error: {e}")
            return None

    if "queue_msg" in next_song:
        try: await next_song["queue_msg"].delete()
        except: pass

    current_songs[chat_id] = next_song
    try:
        stream_url = next_song.get("stream_url") or next_song.get("file_path")
        await asyncio.wait_for(
            calls_module.calls.play(chat_id, MediaStream(stream_url)),
            timeout=20
        )
        logger.info(f"🎵 Playing next: {next_song['title']} in {chat_id}")
        return next_song
    except Exception as e:
        logger.error(f"Queue play error: {e}")
        return None
