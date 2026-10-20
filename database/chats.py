from core.database import db
from utils.logger import get_logger

logger = get_logger("DB_Chats")

async def add_chat(chat_id: int, title: str):
    """Group ko database mein add karta hai."""
    try:
        await db.db.chats.update_one(
            {"chat_id": chat_id},
            {"$set": {"title": title}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error adding chat: {e}")

async def get_chat(chat_id: int):
    return await db.db.chats.find_one({"chat_id": chat_id})

async def set_chat_volume(chat_id: int, volume: int):
    await db.db.chats.update_one(
        {"chat_id": chat_id}, {"$set": {"volume": volume}}, upsert=True
    )
