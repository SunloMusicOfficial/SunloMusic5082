import asyncio
import time
import re
from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import MediaStream
from core.bot import app
import core.calls as calls_module
from utils.decorators import register_user
from utils.downloader import downloader
from plugins.queue import add_to_queue
from utils.logger import get_logger

logger = get_logger("PlayPlugin")

# ── STYLE 3: MINIMAL GLASS (SEARCHING & CONNECTING) ──
SEARCHING_TEXT = "▸ <b>𝐅𝐢𝐧𝐝𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐬𝐨𝐧𝐠...</b>"
CONNECTING_TEXT = "▸ <b>𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐧𝐠 𝐭𝐨 𝐬𝐭𝐫𝐞𝐚𝐦...</b>"

# State management
playback_start_times = {}
live_timer_tasks = {}
chat_states = {} 

def get_time_str(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def generate_bar(current, total, length=8):
    if total == 0: return "🔘" + "─" * (length - 1)
    played = int((current / total) * length)
    if played >= length: played = length - 1
    return "▬" * played + "🔘" + "▬" * (length - played - 1)

def get_player_buttons(chat_id):
    state = chat_states.get(chat_id, {"is_paused": False, "loop": False, "shuffle": False})
    
    play_btn = "▶️ ʀᴇꜱᴜᴍᴇ" if state["is_paused"] else "⏸️ ᴘᴀᴜꜱᴇ"
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state["loop"] else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state["shuffle"] else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(play_btn, callback_data="pause_resume"),
            InlineKeyboardButton("⏭️ ꜱᴋɪᴘ", callback_data="skip")
        ],
        [
            InlineKeyboardButton(shuffle_btn, callback_data="shuffle"),
            InlineKeyboardButton(loop_btn, callback_data="loop")
        ],
        [
            InlineKeyboardButton("⏹️ ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍ", callback_data="stop")
        ]
    ])

async def update_live_timer(chat_id, message, duration_sec):
    while chat_id in playback_start_times:
        await asyncio.sleep(10) # 10s update
        if chat_id not in playback_start_times:
            break
            
        state = chat_states.get(chat_id, {})
        if state.get("is_paused", False):
            continue

        elapsed = int(time.time() - playback_start_times[chat_id])
        if elapsed > duration_sec:
            break

        time_str = get_time_str(elapsed)
        dur_str = get_time_str(duration_sec)
        bar = generate_bar(elapsed, duration_sec)

        try:
            caption = message.caption.html if message.caption else message.text.html
            new_caption = re.sub(r'<code>\d{2}:\d{2}</code>.*?<code>\d{2}:\d{2}</code>', 
                                 f'<code>{time_str}</code> {bar} <code>{dur_str}</code>', caption)
            
            btns = get_player_buttons(chat_id)
            if message.caption:
                await message.edit_caption(caption=new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else:
                await message.edit_text(new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        except Exception:
            pass

@app.on_message(filters.command("play") & filters.group)
@register_user
async def play_handler(client, message):
    try:
        await message.delete()
    except:
        pass

    if len(message.command) < 2:
        return await client.send_message(message.chat.id, "🎵 **ᴜꜱᴀɢᴇ:** `/play <song name>`")

    query = " ".join(message.command[1:])
    
    m = await client.send_message(message.chat.id, SEARCHING_TEXT, parse_mode=enums.ParseMode.HTML)

    song = await downloader.search_and_extract(query)
    if not song:
        return await m.edit_text("❌ <b>ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ!</b>", parse_mode=enums.ParseMode.HTML)

    chat_id = message.chat.id
    active_calls = await calls_module.calls.calls
    dur_str = get_time_str(song['duration'])
    title_short = song['title'][:35] + "..." if len(song['title']) > 35 else song['title']

    # ── ULTRA PREMIUM GLASS LAYOUT ──
    caption = (
        f"<blockquote>"
        f"🎧 <b>𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆 𝐍𝐎𝐖</b>\n\n"
        f"🎵 <b>{title_short}</b>\n"
        f"⏳ <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 :</b> {dur_str}\n"
        f"👤 <b>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 :</b> {message.from_user.mention}"
        f"</blockquote>\n"
        f"<code>00:00</code> {generate_bar(0, song['duration'])} <code>{dur_str}</code>"
    )

    if chat_id in active_calls:
        await add_to_queue(chat_id, song)
        await m.edit_text(f"📥 <b>𝐀𝐝𝐝𝐞𝐝 𝐭𝐨 𝐐𝐮𝐞𝐮𝐞 :</b>\n🎵 {title_short}", parse_mode=enums.ParseMode.HTML)
    else:
        await m.edit_text(CONNECTING_TEXT, parse_mode=enums.ParseMode.HTML)
        
        try:
            stream_url = song.get("stream_url") or song.get("file_path")
            await calls_module.calls.play(chat_id, MediaStream(stream_url))
            
            playback_start_times[chat_id] = time.time()
            chat_states[chat_id] = {"is_paused": False, "loop": False, "shuffle": False}
            
            btns = get_player_buttons(chat_id)
            thumb = song.get("thumbnail")
            
            if thumb:
                try:
                    await m.delete()
                    sent_msg = await client.send_photo(
                        chat_id=chat_id,
                        photo=thumb,
                        caption=caption,
                        reply_markup=btns,
                        parse_mode=enums.ParseMode.HTML
                    )
                except Exception:
                    sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else:
                sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)

            if chat_id in live_timer_tasks:
                live_timer_tasks[chat_id].cancel()
            live_timer_tasks[chat_id] = asyncio.create_task(update_live_timer(chat_id, sent_msg, song['duration']))

        except Exception as e:
            logger.error(f"Play error: {e}")
            await m.edit_text("❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ.</b>", parse_mode=enums.ParseMode.HTML)
