from core.database import db

async def add_user(user_id: int, first_name: str, username: str):
    await db.db.users.update_one({"user_id": user_id}, {"$set": {"first_name": first_name, "username": username}}, upsert=True)

async def get_total_users():
    return await db.db.users.count_documents({})

async def add_gban(user_id: int):
    await db.db.users.update_one({"user_id": user_id}, {"$set": {"is_gbanned": True}}, upsert=True)

async def remove_gban(user_id: int):
    await db.db.users.update_one({"user_id": user_id}, {"$set": {"is_gbanned": False}}, upsert=True)

async def is_gbanned(user_id: int):
    user = await db.db.users.find_one({"user_id": user_id})
    return user.get("is_gbanned", False) if user else False

async def increment_user_plays(user_id: int):
    await db.db.users.update_one({"user_id": user_id}, {"$inc": {"plays": 1}}, upsert=True)

async def get_user_plays(user_id: int):
    user = await db.db.users.find_one({"user_id": user_id})
    return user.get("plays", 0) if user else 0

async def set_afk(user_id: int, reason: str):
    await db.db.users.update_one({"user_id": user_id}, {"$set": {"afk_reason": reason}}, upsert=True)

async def remove_afk(user_id: int):
    await db.db.users.update_one({"user_id": user_id}, {"$unset": {"afk_reason": ""}})

async def get_afk(user_id: int):
    user = await db.db.users.find_one({"user_id": user_id})
    return user.get("afk_reason") if user else None

async def get_all_users():
    cursor = db.db.users.find({}, {"user_id": 1})
    return await cursor.to_list(length=None)
