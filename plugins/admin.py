from ftmgram import filters
from core.bot import app
from config.settings import settings
from database.users import get_total_users
from core.calls import calls

@app.on_message(filters.command("stats") & filters.user(settings.OWNER_ID))
async def stats_handler(client, message):
    users = await get_total_users()
    active_vcs = len(await calls.calls)
    text = (
        "📊 **Bot Statistics**\n\n"
        f"👥 **Total Users:** `{users}`\n"
        f"🎙 **Active Voice Chats:** `{active_vcs}`\n"
        f"⚡ **Status:** Online & Fast"
    )
    await message.reply_text(text)
