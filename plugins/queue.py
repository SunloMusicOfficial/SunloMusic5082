from pytgcalls.types import MediaStream
import core.calls as calls_module
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
            stream_url = next_song.get("stream_url") or next_song.get("file_path")
            await calls_module.calls.play(chat_id, MediaStream(stream_url))
            logger.info(f"🎵 Playing next in queue: {next_song['title']} in {chat_id}")
        except Exception as e:
            logger.error(f"Queue play error: {e}")
    else:
        try:
            await calls_module.calls.leave_call(chat_id)
            logger.info(f"🚪 Left VC (Queue empty) in {chat_id}")
        except:
            pass
