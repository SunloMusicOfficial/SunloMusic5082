import time
import json
from core.database import db
from utils.crypto import encrypt_cookie, decrypt_cookie

async def add_cookie(name: str, data: str):
    await db.db.cookies.update_one(
        {"name": name},
        {"$set": {"data": encrypt_cookie(data), "status": "active", "success": 0, "fails": 0, "added_at": time.time()}},
        upsert=True
    )

async def get_all_cookies():
    cursor = db.db.cookies.find({})
    res = await cursor.to_list(length=None)
    for r in res:
        if r.get("data"): r["data"] = decrypt_cookie(r["data"])
    return res

async def get_active_cookies():
    cursor = db.db.cookies.find({"status": "active"})
    res = await cursor.to_list(length=None)
    for r in res:
        if r.get("data"): r["data"] = decrypt_cookie(r["data"])
    return res

async def mark_cookie_dead(name: str):
    await db.db.cookies.update_one({"name": name}, {"$set": {"status": "dead"}, "$inc": {"fails": 1}})

async def mark_cookie_success(name: str):
    await db.db.cookies.update_one({"name": name}, {"$inc": {"success": 1}})

async def delete_cookie(name: str):
    await db.db.cookies.delete_one({"name": name})

# 🌟 Format Converter (JSON to Netscape)
def json_to_netscape(json_data):
    lines = ["# Netscape HTTP Cookie File"]
    for cookie in json_data:
        domain = cookie.get("domain", ".youtube.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = cookie.get("path", "/")
        secure = "TRUE" if cookie.get("secure") else "FALSE"
        expiration = int(cookie.get("expirationDate", 0))
        name = cookie.get("name", "")
        value = cookie.get("value", "")
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
    return "\n".join(lines)
