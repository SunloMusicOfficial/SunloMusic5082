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
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try: await message.delete()
        except: pass
        
    # 🔥 DM Download Logic Check
    if len(message.command) > 1 and message.command[1].startswith("song_"):
        video_id = message.command[1].replace("song_", "")
        # Redirect to /song command
        message.command = ["/song", video_id]
        message.text = f"/song https://youtube.com/watch?v={video_id}"
        from plugins.downloads import song_dl
        return await song_dl(client, message)

    buttons = [
        [InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?startgroup=true"), InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)],
        [InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT), InlineKeyboardButton("📚 Help", callback_data="help_menu")]
    ]
    
    await message.reply_photo(photo=constants.START_IMG, caption=constants.START_TEXT, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@app.on_message(filters.command("help"))
@register_user
async def help_handler(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        try: await message.delete()
        except: pass
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]])
    await message.reply_text(text=constants.HELP_TEXT, reply_markup=buttons, parse_mode=enums.ParseMode.HTML, link_preview_options=None)

@app.on_callback_query(filters.regex("help_menu|back_start"))
async def callback_help(client, query):
    if query.data == "help_menu":
        await query.message.edit_text(text=constants.HELP_TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]]), parse_mode=enums.ParseMode.HTML, link_preview_options=None)
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
