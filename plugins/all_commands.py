from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("allcommand"))
@register_user
async def all_commands(client, message):
    text = (
        "👑 **𝐒𝐔𝐍𝐋𝐎 𝐌𝐔𝐒𝐈𝐂 - 𝐌𝐀𝐒𝐓𝐄𝐑 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐋𝐈𝐒𝐓** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎵 **𝐌𝐔𝐒𝐈𝐂 & 𝐏𝐋𝐀𝐘𝐁𝐀𝐂𝐊**\n"
        "▸ `/play` `/vplay` `/cplay` - Play track\n"
        "▸ `/pause` `/resume` - Control stream\n"
        "▸ `/skip` `/stop` - Skip or leave VC\n"
        "▸ `/seek <time>` - Seek time\n"
        "▸ `/speed` `/volume` `/pitch` - Audio tuning\n"
        "▸ `/current` `/queue` `/history` - Track info\n"
        "▸ `/radio` `/sleep` `/vcjoin` - Streaming modes\n"
        "▸ `/loopqueue` `/shuffle` `/crossfade` - Queue controls\n\n"
        "🎛 **𝐀𝐔𝐃𝐈𝐎 𝐄𝐅𝐅𝐄𝐂𝐓𝐒**\n"
        "▸ `/bass` `/8d` `/nightcore`\n"
        "▸ `/slowed` `/vaporwave` `/karaoke`\n"
        "▸ `/normal` - Reset effects\n\n"
        "📥 **𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐄𝐑𝐒**\n"
        "▸ `/song` `/video` - YT download\n"
        "▸ `/spotify` `/soundcloud` `/jiosaavn`\n"
        "▸ `/ig` `/fb` `/twitter` `/pinterest`\n\n"
        "🛠 **𝐓𝐎𝐎𝐋𝐒 & 𝐔𝐓𝐈𝐋𝐈𝐓𝐈𝐄𝐒**\n"
        "▸ `/ping` `/id` `/uptime` `/stats`\n"
        "▸ `/calc` `/translate` `/shorten` `/base64`\n"
        "▸ `/whois` `/wiki` `/google` `/weather`\n"
        "▸ `/qr` `/tts` `/report`\n\n"
        "🎮 **𝐆𝐀𝐌𝐄𝐒 & 𝐅𝐔𝐍**\n"
        "▸ `/dice` `/dart` `/slot` `/8ball`\n"
        "▸ `/truth` `/dare` `/joke` `/meme`\n"
        "▸ `/trivia` `/shazam` (Reply to voice)\n\n"
        "👤 **𝐔𝐒𝐄𝐑 & 𝐏𝐋𝐀𝐘𝐋𝐈𝐒𝐓𝐒**\n"
        "▸ `/playlist` `/save` `/backup` `/restore`\n"
        "▸ `/afk` `/mystats` `/recommend`\n"
        "▸ `/lyrics` `/dedicate`\n\n"
        "👑 **𝐀𝐃𝐌𝐈𝐍 & 𝐌𝐎𝐃𝐄𝐑𝐀𝐓𝐈𝐎𝐍**\n"
        "▸ `/setwelcome` `/setgoodbye` `/setthumb`\n"
        "▸ `/setcaption` `/setrules` `/antilink`\n"
        "▸ `/filter` `/lock` `/unlock`\n"
        "▸ `/kick` `/purge` `/warn` `/tagall`\n"
        "▸ `/auth` `/setprefix`\n\n"
        "⚙️ **𝐎𝐖𝐍𝐄𝐑 𝐎𝐍𝐋𝐘**\n"
        "▸ `/broadcast` `/gban` `/ungban`\n"
        "▸ `/clean` `/reload` `/restart` `/maintenance`\n"
        "▸ `/addsudo` `/delsudo`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
