from ftmgram import filters
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from config.settings import settings
from config.constants import constants
from utils.decorators import register_user

@app.on_message(filters.command("start") & filters.private)
@register_user
async def start_handler(client, message):
    buttons = [
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{settings.BOT_USERNAME}?startgroup=true"),
            InlineKeyboardButton("📢 Support", url=settings.SUPPORT_CHANNEL)
        ],
        [
            InlineKeyboardButton("👑 Owner", url=settings.SUPPORT_CHAT)
        ]
    ]
    await message.reply_photo(
        photo=constants.START_IMG,
        caption=constants.START_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
