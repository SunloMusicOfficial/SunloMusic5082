from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("mention") & filters.group)
@register_user
async def mention_handler(client, message):
    if not message.reply_to_message: return await message.reply_text("↩️ Reply to a user to mention them.")
    user = message.reply_to_message.from_user
    await message.reply_text(f"🔔 {user.mention} (ID: `{user.id}`)")

@app.on_message(filters.command("help"))
async def help_handler(client, message):
    text = (
        "📚 **Sunlo Music - Help Menu**\n\n"
        "🎵 **Playback**\n"
        "▸ `/play` - Play song (Search or Link)\n"
        "▸ `/vplay` - Play video\n"
        "▸ `/pause` / `/resume` - Control stream\n"
        "▸ `/skip` - Next track\n"
        "▸ `/stop` - Leave VC\n"
        "▸ `/volume` - Set volume (1-200)\n"
        "▸ `/seek` - Seek time (e.g. 1:30)\n\n"
        "🎛 **Effects**\n"
        "▸ `/bass` `/8d` `/nightcore` `/slowed`\n"
        "▸ `/karaoke` `/normal`\n\n"
        "👤 **User**\n"
        "▸ `/song` - Download audio\n"
        "▸ `/video` - Download video\n"
        "▸ `/lyrics` - Get lyrics\n"
        "▸ `/afk` - Set AFK\n"
        "▸ `/stats` `/id` `/ping`\n\n"
        "🛡 **Admin**\n"
        "▸ `/antilink` `/setwelcome`\n"
        "▸ `/kick` `/purge` `/tagall`"
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
