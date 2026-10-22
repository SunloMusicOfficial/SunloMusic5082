from core.database import db

async def add_sudo(user_id: int):
    await db.db.sudo_users.update_one({"user_id": user_id}, {"$set": {"user_id": user_id}}, upsert=True)

async def remove_sudo(user_id: int):
    await db.db.sudo_users.delete_one({"user_id": user_id})

async def get_sudo_users():
    users = await db.db.sudo_users.find({}).to_list(length=None)
    return [u["user_id"] for u in users]

async def is_sudo(user_id: int):
    user = await db.db.sudo_users.find_one({"user_id": user_id})
    return True if user else False
