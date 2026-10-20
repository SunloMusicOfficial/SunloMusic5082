from ftmgram import filters
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command(["bass", "nightcore", "8d"]) & filters.group)
@register_user
async def effects_handler(client, message):
    effect = message.command[0].upper()
    await message.reply_text(f"🎛 **{effect}** effect will be applied in the next premium update. Currently in beta!")
