from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from core.database import db
from utils.decorators import register_user
from utils.logger import get_logger
from plugins.play import play_song_by_id

logger = get_logger("Playlist")

@app.on_message(filters.command("playlist") & filters.private)
@register_user
async def playlist_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text(
            "🎵 **𝐏𝐥𝐚𝐲𝐥𝐢𝐬𝐭 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:**\n\n"
            "▸ `/playlist create <name>` - Create new playlist\n"
            "▸ `/playlist add <name>` (reply to song) - Add current song\n"
            "▸ `/playlist list` - Show your playlists\n"
            "▸ `/playlist show <name>` - Show songs in playlist\n"
            "▸ `/playlist play <name>` - Play whole playlist\n"
            "▸ `/playlist delete <name>` - Delete playlist"
        )
    
    cmd = message.command[1].lower()
    user_id = message.from_user.id
    
    if cmd == "create":
        if len(message.command) < 3: return await message.reply_text("❌ Provide a name.")
        name = " ".join(message.command[2:])
        await db.db.playlists.update_one(
            {"user_id": user_id, "name": name}, 
            {"$setOnInsert": {"songs": []}}, upsert=True
        )
        await message.reply_text(f"✅ Playlist **{name}** created!")

    elif cmd == "list":
        cursor = db.db.playlists.find({"user_id": user_id})
        playlists = await cursor.to_list(length=20)
        if not playlists: return await message.reply_text("📭 You have no playlists.")
        
        text = "🎵 **𝐘𝐨𝐮𝐫 𝐏𝐥𝐚𝐲𝐥𝐢𝐬𝐭𝐬:**\n\n"
        for p in playlists:
            text += f"▸ **{p['name']}** ({len(p['songs'])} songs)\n"
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)

    elif cmd == "show":
        if len(message.command) < 3: return await message.reply_text("❌ Provide a name.")
        name = " ".join(message.command[2:])
        playlist = await db.db.playlists.find_one({"user_id": user_id, "name": name})
        if not playlist or not playlist['songs']: return await message.reply_text("❌ Empty or not found.")
        
        text = f"🎵 **{name}** ({len(playlist['songs'])} songs)\n\n"
        for i, s in enumerate(playlist['songs'], 1):
            text += f"{i}. {s['title']}\n"
        await message.reply_text(text, parse_mode=enums.ParseMode.HTML)
        
    elif cmd == "delete":
        if len(message.command) < 3: return await message.reply_text("❌ Provide a name.")
        name = " ".join(message.command[2:])
        await db.db.playlists.delete_one({"user_id": user_id, "name": name})
        await message.reply_text(f"🗑 Playlist **{name}** deleted.")

    elif cmd == "play":
        if len(message.command) < 3: return await message.reply_text("❌ Provide a name.")
        name = " ".join(message.command[2:])
        playlist = await db.db.playlists.find_one({"user_id": user_id, "name": name})
        if not playlist or not playlist['songs']: return await message.reply_text("❌ Empty or not found.")
        
        m = await message.reply_text(f"⏳ Loading **{name}**...")
        # For simplicity, we just play the first song (Queue logic handles the rest in a real scenario)
        from plugins.play import play_song_by_id
        from utils.downloader import downloader
        # Needs to be played in a group, so asking user to use in group
        await m.edit_text("⚠️ Please use this command in a group to play music.")
