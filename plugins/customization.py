from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user
from database.chats import set_chat_setting, get_chat_setting

@app.on_message(filters.command("setthumb") & filters.group)
@register_user
async def setthumb_handler(client, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("↩️ Reply to a photo to set it as custom thumbnail.")
    file_id = message.reply_to_message.photo.file_id
    await set_chat_setting(message.chat.id, "custom_thumb", file_id)
    await message.reply_text("✅ Custom thumbnail set for this group!")

@app.on_message(filters.command("setcaption") & filters.group)
@register_user
async def setcaption_handler(client, message):
    if len(message.command) < 2: return await message.reply_text("⚙️ **Usage:** `/setcaption <your text>`\nUse `{title}` and `{user}` as variables.")
    caption = message.text.split(None, 1)[1]
    await set_chat_setting(message.chat.id, "custom_caption", caption)
    await message.reply_text("✅ Custom caption template saved!")
