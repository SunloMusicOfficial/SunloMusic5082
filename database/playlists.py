from core.database import db
from utils.logger import get_logger

logger = get_logger("DB_Playlists")

async def add_to_playlist(user_id: int, song_title: str, video_id: str):
    """Gaana user ki personal playlist mein save karta hai."""
    try:
        await db.db.playlists.update_one(
            {"user_id": user_id},
            {"$push": {"songs": {"title": song_title, "id": video_id}}},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Playlist error: {e}")
        return False

async def get_playlist(user_id: int):
    data = await db.db.playlists.find_one({"user_id": user_id})
    return data.get("songs", []) if data else []
