from core.database import db

async def increment_play_count(title: str):
    await db.db.top_songs.update_one({"title": title}, {"$inc": {"count": 1}}, upsert=True)

async def get_top_charts():
    cursor = db.db.top_songs.find().sort("count", -1).limit(10)
    return await cursor.to_list(length=10)
