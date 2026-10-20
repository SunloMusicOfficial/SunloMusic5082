import asyncio
from ftmgram import filters
from core.bot import app
from utils.decorators import register_user
from plugins.queue import get_player_state

@app.on_message(filters.command("crossfade") & filters.group)
@register_user
async def crossfade_handler(client, message):
    chat_id = message.chat.id
    state = get_player_state(chat_id)
    
    if len(message.command) < 2:
        current = state.get("crossfade", 0)
        return await message.reply_text(f"⏱ **Crossfade:** `{current} seconds`\n\nUsage: `/crossfade 5` (Set 0 to disable)")
    
    try:
        secs = int(message.command[1])
        if secs > 15: raise ValueError
        state["crossfade"] = secs
        await message.reply_text(f"✅ **Crossfade set to {secs} seconds.**")
    except:
        await message.reply_text("❌ Invalid input. Max 15 seconds.")

# NOTE: Actual overlapping crossfade requires complex FFmpeg node mapping in PyTgCalls.
# This sets the variable so a smart queue can trigger the next song 'X' seconds before the current ends.
