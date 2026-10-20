from core.database import db

async def increment_play_count():
    """Total kitne gaane play hue wo count karta hai."""
    await db.db.stats.update_one(
        {"type": "global"},
        {"$inc": {"plays": 1}},
        upsert=True
    )

async def get_stats():
    data = await db.db.stats.find_one({"type": "global"})
    return data.get("plays", 0) if data else 0
