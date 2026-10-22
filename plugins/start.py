from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from config.settings import settings
from config.constants import constants
from utils.decorators import register_user
from utils.logger import get_logger

logger = get_logger("StartPlugin")

@app.on_message(filters.command("start"))
@register_user
async def start_handler(client, message):
    # 🔥 DM Download Logic
    if len(message.command) > 1 and message.command[1].startswith("song_"):
        video_id = message.command[1].replace("song_", "")
        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎵 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐀𝐮𝐝𝐢𝐨", callback_data=f"dl_audio_{video_id}"),
                InlineKeyboardButton("🎬 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝 𝐕𝐢𝐝𝐞𝐨", callback_data=f"dl_video_{video_id}")
            ]
        ])
        return await message.reply_text(
            f"👋 **Welcome to Sunlo Music Downloader!**\n\n"
            f"You clicked on a song from a group. What would you like to download?",
            reply_markup=buttons
        )

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try: await message.delete()
        except: pass

    buttons = [
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?startgroup=true"), InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)],
        [InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT), InlineKeyboardButton("📚 Help", callback_data="help_menu")]
    ]
    try:
        await message.reply_photo(photo=constants.START_IMG, caption=constants.START_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
    except:
        await message.reply_text(text=constants.START_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@app.on_callback_query(filters.regex(r"^dl_(audio|video)_(.+)$"))
async def dm_download_handler(client, query):
    action, video_id = query.data.split("_")[1], query.data.split("_")[2]
    await query.message.delete()
    m = await client.send_message(query.message.chat.id, f"📥 **Downloading {action}...**")
    
    import aiohttp, os
    api_url = getattr(settings, "SUNLO_DOWNLOAD_API_URL", "")
    api_key = getattr(settings, "SUNLO_DOWNLOAD_API_KEY", "")
    
    try:
        os.makedirs("cache", exist_ok=True)
        file_path = f"cache/dl_{video_id}.mp3" if action == "audio" else f"cache/dl_{video_id}.mp4"
        async with aiohttp.ClientSession() as session:
            payload = {"url": f"https://youtube.com/watch?v={video_id}", "api_key": api_key, "type": action}
            async with session.post(f"{api_url.rstrip('/')}/download", json=payload, timeout=180) as resp:
                if resp.status == 200:
                    with open(file_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(65536):
                            f.write(chunk)
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 10000:
                        if action == "audio": await query.message.reply_audio(audio=file_path, performer="Sunlo Music")
                        else: await query.message.reply_video(video=file_path)
                        await m.delete()
                        os.remove(file_path)
                    else:
                        await m.edit_text("❌ Download failed. File is empty.")
                else:
                    await m.edit_text(f"❌ API Error: {resp.status}")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")

@app.on_message(filters.command("help"))
@register_user
async def help_handler(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try: await message.delete()
        except: pass
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]])
    await message.reply_text(text=constants.HELP_TEXT, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)

@app.on_callback_query(filters.regex("help_menu|back_start"))
async def callback_help(client, query):
    if query.data == "help_menu":
        await query.message.edit_text(text=constants.HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]]), parse_mode=enums.ParseMode.HTML)
    elif query.data == "back_start":
        buttons = [
            [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?startgroup=true"), InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)],
            [InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT), InlineKeyboardButton("📚 Help", callback_data="help_menu")]
        ]
        try:
            await query.message.delete()
            await query.message.reply_photo(photo=constants.START_IMG, caption=constants.START_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)
        except: pass
    await query.answer()
