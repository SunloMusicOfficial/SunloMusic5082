import random
from pytgcalls.types import MediaStream
import core.calls as calls_module
from utils.player_state import get_player_state
from utils.logger import get_logger

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
        try:
            await calls_module.calls.leave_call(chat_id)
            if chat_id in current_songs: del current_songs[chat_id]
            logger.info(f"🚪 Left VC (Queue empty) in {chat_id}")
        except: pass
        return None

    current_songs[chat_id] = next_song
    try:
        stream_url = next_song.get("stream_url") or next_song.get("file_path")
        effect = state.get("effect")
        
        ffmpeg_args = None
        if effect == "bass": ffmpeg_args = "-af bass=g=15"
        elif effect == "8d": ffmpeg_args = "-af apulsator=hz=0.08"
        elif effect == "nightcore": ffmpeg_args = "-af atempo=1.2,asetrate=48000*1.2"
        elif effect == "slowed": ffmpeg_args = "-af atempo=0.85,asetrate=44100*0.85"
        elif effect == "vaporwave": ffmpeg_args = "-af atempo=0.8,asetrate=44100*0.8"
        elif effect == "karaoke": ffmpeg_args = "-af pan=stereo|c0=c0|c1=-1*c1"

        await calls_module.calls.play(chat_id, MediaStream(stream_url, ffmpeg_parameters=ffmpeg_args))
        logger.info(f"🎵 Playing next: {next_song['title']} in {chat_id}")
        return next_song # 🔥 Return song data for UI
    except Exception as e:
        logger.error(f"Queue play error: {e}")
        return None
