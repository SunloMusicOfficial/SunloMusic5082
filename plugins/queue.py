from pytgcalls.types import MediaStream
from core.calls import calls
from utils.downloader import downloader
from utils.logger import get_logger

logger = get_logger("QueueManager")
queues = {}

async def add_to_queue(chat_id: int, song_data: dict):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song_data)

async def play_next_in_queue(chat_id: int):
    if chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id].pop(0)
        try:
            # Agar direct URL hai toh stream karo, warna download karke play karo
            stream_url = next_song.get("stream_url") or next_song.get("file_path")
            
            await calls.play(
                chat_id,
                MediaStream(stream_url)
            )
            logger.info(f"🎵 Playing next in queue: {next_song['title']} in {chat_id}")
        except Exception as e:
            logger.error(f"Queue play error: {e}")
    else:
        # Queue empty, leave VC
        try:
            await calls.leave_call(chat_id)
            logger.info(f"🚪 Left VC (Queue empty) in {chat_id}")
        except:
            pass
