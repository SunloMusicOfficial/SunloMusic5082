from core.database import db
from utils.logger import get_logger

logger = get_logger("DB_Users")

async def add_user(user_id: int, first_name: str, username: str):
    """Naye user ko database mein save karta hai."""
    try:
        await db.db.users.update_one(
            {"user_id": user_id},
            {"$set": {"first_name": first_name, "username": username}},
            upsert=True
        )
    except Exception as e:
        logger.error(f"Error adding user: {e}")

async def get_user(user_id: int):
    return await db.db.users.find_one({"user_id": user_id})

async def get_total_users():
    return await db.db.users.count_documents({})
