from ftmgram import filters, enums
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("allcommand"))
@register_user
async def all_commands(client, message):
    text = (
        "👑 <b>𝐒𝐔𝐍𝐋𝐎 𝐌𝐔𝐒𝐈𝐂 - 𝐔𝐋𝐓𝐈𝐌𝐀𝐓𝐄 𝐂𝐎𝐌𝐌𝐀𝐍𝐃 𝐋𝐈𝐒𝐓</b> 👑\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        "🎵 <b>𝐌𝐔𝐒𝐈𝐂 & 𝐏𝐋𝐀𝐘𝐁𝐀𝐂𝐊</b>\n"
        "▸ /play /vplay /cplay - Play track\n"
        "▸ /playfile - Play replied audio\n"
        "▸ /pause /resume /skip /stop\n"
        "▸ /seek &lt;time&gt; /speed &lt;val&gt;\n"
        "▸ /volume &lt;1-200&gt; /pitch &lt;val&gt;\n"
        "▸ /current /queue /history\n"
        "▸ /vcjoin /vcleave - VC control\n"
        "▸ /crossfade /loopqueue /shuffle\n"
        "▸ /remove /clearqueue\n\n"

        "📻 <b>𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆 & 𝐑𝐀𝐃𝐈𝐎</b>\n"
        "▸ /radio &lt;lofi/bollywood&gt;\n"
        "▸ /sleep &lt;min&gt; - Sleep timer\n"
        "▸ /ai_dj - Play random mood song\n\n"

        "🎛 <b>𝐀𝐔𝐃𝐈𝐎 𝐄𝐅𝐅𝐄𝐂𝐓𝐒</b>\n"
        "▸ /bass /8d /nightcore\n"
        "▸ /slowed /vaporwave /karaoke\n"
        "▸ /normal - Reset effects\n"
        "▸ /soundboard &lt;sound&gt; - Play effect\n\n"

        "📥 <b>𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐄𝐑𝐒</b>\n"
        "▸ /song /video - YT download\n"
        "▸ /spotify /soundcloud /jiosaavn\n"
        "▸ /ig /insta /fb /twitter /pinterest\n\n"

        "🖼 <b>𝐈𝐌𝐀𝐆𝐄 & 𝐀𝐈 𝐓𝐎𝐎𝐋𝐒</b>\n"
        "▸ /makestart - Generate start image\n"
        "▸ /geturl - Get Image URL/FileID\n"
        "▸ /shazam - Identify song (reply to voice)\n"
        "▸ /tts &lt;text&gt; - Text to speech\n\n"

        "🛠 <b>𝐓𝐎𝐎𝐋𝐒 & 𝐔𝐓𝐈𝐋𝐈𝐓𝐈𝐄𝐒</b>\n"
        "▸ /ping /id /uptime /stats /sysinfo\n"
        "▸ /calc /translate /shorten /base64\n"
        "▸ /whois /wiki /google /weather\n"
        "▸ /qr /report /top\n\n"

        "🎮 <b>𝐆𝐀𝐌𝐄𝐒 & 𝐅𝐔𝐍</b>\n"
        "▸ /dice /dart /slot /8ball\n"
        "▸ /truth /dare /joke /meme\n"
        "▸ /trivia - Music quiz\n\n"

        "👤 <b>𝐔𝐒𝐄𝐑 & 𝐏𝐋𝐀𝐘𝐋𝐈𝐒𝐓𝐒</b>\n"
        "▸ /playlist /save /backup /restore\n"
        "▸ /afk &lt;reason&gt; /mystats /recommend\n"
        "▸ /share /lyrics /dedicate /mention\n\n"

        "👑 <b>𝐀𝐃𝐌𝐈𝐍 & 𝐌𝐎𝐃𝐄𝐑𝐀𝐓𝐈𝐎𝐍</b>\n"
        "▸ /setwelcome /setgoodbye /setrules /rules\n"
        "▸ /setthumb /setcaption /setleave /autovc\n"
        "▸ /antilink /filter /lang\n"
        "▸ /lock /unlock /warn /resetwarn\n"
        "▸ /kick /purge /tagall /auth /setprefix\n\n"

        "⚙️ <b>𝐎𝐖𝐍𝐄𝐑 𝐎𝐍𝐋𝐘</b>\n"
        "▸ /broadcast /gban /ungban\n"
        "▸ /clean /reload /restart /maintenance\n"
        "▸ /addsudo /delsudo /setlog\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <i>Tip: Use /help for a quick overview.</i>"
    )
    await message.reply_text(text, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True)
