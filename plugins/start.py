from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from config.settings import settings
from config.constants import constants
from utils.decorators import register_user
from utils.logger import get_logger

logger = get_logger("StartPlugin")

@app.on_message(filters.command("start") & filters.private)
@register_user
async def start_handler(client, message):
    buttons = [
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?startgroup=true"),
            InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT),
            InlineKeyboardButton("📚 Help", callback_data="help_menu")
        ]
    ]
    
    try:
        await message.reply_photo(
            photo=constants.START_IMG,
            caption=constants.START_TEXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Start image failed, sending text instead: {e}")
        await message.reply_text(
            text=constants.START_TEXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )

@app.on_message(filters.command("help"))
@register_user
async def help_handler(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]
    ])
    await message.reply_text(
        text=constants.HELP_TEXT,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("help_menu|back_start"))
async def callback_help(client, query):
    if query.data == "help_menu":
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Start", callback_data="back_start")]
        ])
        await query.message.edit_text(
            text=constants.HELP_TEXT,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )
    elif query.data == "back_start":
        buttons = [
            [
                InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?startgroup=true"),
                InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)
            ],
            [
                InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT),
                InlineKeyboardButton("📚 Help", callback_data="help_menu")
            ]
        ]
        await query.message.edit_caption(
            caption=constants.START_TEXT,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
    await query.answer()
