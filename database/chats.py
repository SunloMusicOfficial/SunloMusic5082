from core.database import db

async def set_chat_setting(chat_id: int, key: str, value):
    await db.db.chats.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)

async def get_chat_setting(chat_id: int, key: str, default=None):
    chat = await db.db.chats.find_one({"chat_id": chat_id})
    return chat.get(key, default) if chat else default
