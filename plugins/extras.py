from ftmgram import filters
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("lyrics") & filters.group)
@register_user
async def lyrics_handler(client, message):
    await message.reply_text("📜 **Live Synced Lyrics** feature is currently under development. Coming very soon!")
