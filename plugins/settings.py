from ftmgram import filters
from core.bot import app
from core.calls import calls
from utils.decorators import register_user

@app.on_message(filters.command("volume") & filters.group)
@register_user
async def volume_handler(client, message):
    if len(message.command) < 2:
        return await message.reply_text("🔊 **Usage:** `/volume <1-200>`")
    
    try:
        vol = int(message.command[1])
        if not 1 <= vol <= 200:
            raise ValueError
        await calls.change_volume_call(message.chat.id, vol)
        await message.reply_text(f"🔊 Volume set to **{vol}%**")
    except ValueError:
        await message.reply_text("❌ Please enter a number between 1 and 200.")
    except Exception:
        await message.reply_text("❌ Failed to change volume. Is music playing?")
