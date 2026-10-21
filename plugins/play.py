import asyncio, time, re
from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import MediaStream
from core.bot import app
import core.calls as calls_module
from utils.decorators import register_user
from utils.downloader import downloader
from utils.ratelimiter import is_rate_limited
from plugins.queue import add_to_queue, current_songs, get_player_state
from database.stats import increment_play_count
from database.users import increment_user_plays
from utils.logger import get_logger

logger = get_logger("PlayPlugin")
playback_start_times = {}
live_timer_tasks = {}

def get_time_str(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def generate_bar(current, total, length=8):
    if total == 0: return "🔘" + "─" * (length - 1)
    played = int((current / total) * length)
    if played >= length: played = length - 1
    return "▬" * played + "🔘" + "▬" * (length - played - 1)

def get_player_buttons(chat_id):
    state = get_player_state(chat_id)
    play_btn = "▶️ ʀᴇꜱᴜᴍᴇ" if state["is_paused"] else "⏸️ ᴘᴀᴜꜱᴇ"
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state["loop"] else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state["shuffle"] else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(play_btn, callback_data="pause_resume"), InlineKeyboardButton("⏭️ ꜱᴋɪᴘ", callback_data="skip")],
        [InlineKeyboardButton(shuffle_btn, callback_data="shuffle"), InlineKeyboardButton(loop_btn, callback_data="loop")],
        [InlineKeyboardButton("⏪ -10s", callback_data="seek_m10"), InlineKeyboardButton("⏩ +10s", callback_data="seek_p10")],
        [InlineKeyboardButton("⏹️ ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍ", callback_data="stop")]
    ])

async def update_live_timer(chat_id, message, duration_sec):
    while chat_id in playback_start_times:
        await asyncio.sleep(10) 
        if chat_id not in playback_start_times: break
        state = get_player_state(chat_id)
        if state.get("is_paused", False): continue
        elapsed = int(time.time() - playback_start_times[chat_id])
        if elapsed > duration_sec: break
        time_str, dur_str = get_time_str(elapsed), get_time_str(duration_sec)
        bar = generate_bar(elapsed, duration_sec)
        try:
            caption = message.caption.html if message.caption else message.text.html
            new_caption = re.sub(r'<code>\d{2}:\d{2}</code>.*?<code>\d{2}:\d{2}</code>', f'<code>{time_str}</code> {bar} <code>{dur_str}</code>', caption)
            btns = get_player_buttons(chat_id)
            if message.caption: await message.edit_caption(caption=new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else: await message.edit_text(new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        except: pass

@app.on_message(filters.command(["play", "vplay", "cplay"]) & (filters.group | filters.channel))
@register_user
async def play_handler(client, message):
    cmd = message.command[0].lower()
    is_video = cmd == "vplay"
    is_channel = cmd == "cplay"
    
    if not is_channel and is_rate_limited(message.from_user.id):
        return await message.reply_text("⚠️ **Sabar karein!** 3 second ka cooldown hai.")
    
    try: await message.delete()
    except: pass
    
    if len(message.command) < 2: return await client.send_message(message.chat.id, f"🎵 **ᴜꜱᴀɢᴇ:** `/{cmd} <song name>`")
    
    query = " ".join(message.command[1:])
    m = await client.send_message(message.chat.id, "🔍 <b>𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠...</b>", parse_mode=enums.ParseMode.HTML)
    
    song = await downloader.search_and_extract(query)
    if not song:
        return await m.edit_text("❌ <b>ɴᴏ ʀᴇꜱᴜʟᴛꜱ ꜰᴏᴜɴᴅ!</b>\n<i>API down or Video unavailable.</i>", parse_mode=enums.ParseMode.HTML)

    await play_song_by_id(client, message, m, song['id'], is_video)

async def play_song_by_id(client, message, m, video_id, is_video=False):
    song = await downloader.get_stream(video_id)
    if not song: 
        return await m.edit_text("❌ <b>ꜰᴀɪʟᴇᴅ.</b>\n<i>Could not extract stream URL.</i>", parse_mode=enums.ParseMode.HTML)
    
    await increment_play_count(song.get('title', 'Unknown'))
    if hasattr(message, 'from_user') and message.from_user:
        await increment_user_plays(message.from_user.id)
    
    chat_id = message.chat.id
    from plugins.music_extras import history_db
    if chat_id not in history_db: history_db[chat_id] = []
    if song.get('title') not in history_db[chat_id]:
        history_db[chat_id].append(song.get('title'))
        if len(history_db[chat_id]) > 20: history_db[chat_id].pop(0)

    active_calls = await calls_module.calls.calls
    dur_str = get_time_str(song.get('duration', 0))
    title_short = song.get('title', 'Unknown')[:35] + "..." if len(song.get('title', 'Unknown')) > 35 else song.get('title', 'Unknown')

    requester = message.from_user.mention if hasattr(message, 'from_user') and message.from_user else "Channel"
    
    caption = (
        f"<blockquote>🎧 <b>𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆 {'𝐕𝐈𝐃𝐄𝐎' if is_video else '𝐍𝐎𝐖'}</b>\n\n"
        f"🎵 <b>{title_short}</b>\n⏳ <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 :</b> {dur_str}\n"
        f"👤 <b>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 :</b> {requester}</blockquote>\n"
        f"<code>00:00</code> {generate_bar(0, song.get('duration', 0))} <code>{dur_str}</code>"
    )

    if chat_id in active_calls:
        await add_to_queue(chat_id, song)
        await m.edit_text(f"📥 <b>𝐀𝐝𝐝𝐞𝐝 𝐭𝐨 𝐐𝐮𝐞𝐮𝐞 :</b>\n🎵 {title_short}", parse_mode=enums.ParseMode.HTML)
    else:
        await m.edit_text("▸ <b>𝐂𝐨𝐧𝐧𝐞𝐜𝐭𝐢𝐧𝐠...</b>", parse_mode=enums.ParseMode.HTML)
        try:
            await calls_module.calls.play(chat_id, MediaStream(song['stream_url']))
            current_songs[chat_id] = song
            playback_start_times[chat_id] = time.time()
            btns = get_player_buttons(chat_id)
            
            thumb = song.get('thumbnail')
            sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            
            if thumb and not is_video:
                try:
                    await m.delete()
                    sent_msg = await client.send_photo(chat_id, photo=thumb, caption=caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
                except: pass
                
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            live_timer_tasks[chat_id] = asyncio.create_task(update_live_timer(chat_id, sent_msg, song.get('duration', 0)))
        except Exception as e:
            logger.error(f"Play error: {e}")
            await m.edit_text(f"❌ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴠᴄ.</b>\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)
