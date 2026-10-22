import asyncio, time, re
from ftmgram import enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("PlayerState")

playback_start_times = {}
live_timer_tasks = {}
chat_states = {}
active_cards = {}

def get_player_state(chat_id):
    if chat_id not in chat_states:
        chat_states[chat_id] = {"is_paused": False, "loop": False, "shuffle": False, "autoplay": False}
    return chat_states[chat_id]

def get_time_str(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def generate_bar(current, total, length=10):
    if total == 0: return "─" * length
    played = int((current / total) * length)
    if played >= length: played = length
    return "▬" * played + "🔘" + "─" * (length - played)

# 🔥 NEW CLEAN UI (3 Rows as requested)
def get_player_buttons(chat_id, video_id, current=0, total=0):
    state = get_player_state(chat_id)
    play_text = "▶️ ʀᴇꜱᴜᴍᴇ" if state.get("is_paused", False) else "⏸ ᴘᴀᴜꜱᴇ"
    time_btn_text = f"{get_time_str(current)} {generate_bar(current, total)} {get_time_str(total)}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(time_btn_text, callback_data="ignore")], # Row 1: Timer only
        [
            InlineKeyboardButton(play_text, callback_data="pause_resume"), # Row 2: Pause | Skip
            InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="skip")
        ],
        [
            InlineKeyboardButton("✨ ᴍᴏʀᴇ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="more_controls") # Row 3: More Controls
        ]
    ])

def get_expanded_buttons(chat_id, current=0, total=0):
    state = get_player_state(chat_id)
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state.get("loop", False) else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state.get("shuffle", False) else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"
    auto_btn = "✅ ᴀᴜᴛᴏᴘʟᴀʏ ᴏɴ" if state.get("autoplay", False) else "🔄 ᴀᴜᴛᴏᴘʟᴀʏ ᴏꜰꜰ"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(auto_btn, callback_data="autoplay")],
        [InlineKeyboardButton("⏪ -10ꜱ", callback_data="seek_m10"), InlineKeyboardButton("⏩ +10ꜱ", callback_data="seek_p10")],
        [InlineKeyboardButton(shuffle_btn, callback_data="shuffle"), InlineKeyboardButton(loop_btn, callback_data="loop")],
        [InlineKeyboardButton("⏹ ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍ", callback_data="stop")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_main")]
    ])

async def update_live_timer(chat_id, message, duration_sec):
    from plugins.queue import current_songs
    while chat_id in playback_start_times:
        await asyncio.sleep(10) 
        if chat_id not in playback_start_times: break
        state = get_player_state(chat_id)
        if state.get("is_paused", False): continue
        elapsed = int(time.time() - playback_start_times[chat_id])
        if elapsed > duration_sec: break
        
        song = current_songs.get(chat_id, {})
        vid = song.get('id', '')
        
        btns = get_player_buttons(chat_id, vid, elapsed, duration_sec)
        try:
            await message.edit_reply_markup(reply_markup=btns)
        except: pass

async def delete_active_card(chat_id):
    if chat_id in active_cards:
        try: await active_cards[chat_id].delete()
        except: pass
        del active_cards[chat_id]

async def send_now_playing_card(client, chat_id, song, is_video=False, m=None):
    await delete_active_card(chat_id)
    
    title_short = song.get('title', 'Unknown')[:40] + "..." if len(song.get('title', 'Unknown')) > 40 else song.get('title', 'Unknown')
    dur_str = get_time_str(song.get('duration', 0))
    requester = song.get('requester', 'Channel')
    video_id = song.get('id', '')
    
    # 🔥 CLICKABLE TITLE LINK TO DM
    bot_username = settings.BOT_USERNAME.replace('@', '')
    title_link = f'<a href="https://t.me/{bot_username}?start=song_{video_id}">{title_short}</a>'
    
    caption = (
        f"<blockquote>🎧 <b>𝐍𝐨𝐰 𝐏𝐥𝐚𝐲𝐢𝐧𝐠</b>\n\n"
        f"▶️ <b>𝐓𝐢𝐭𝐥𝐞 :</b> {title_link}\n"
        f"⏳ <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 :</b> {dur_str}\n"
        f"👤 <b>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 :</b> {requester}</blockquote>"
    )

    playback_start_times[chat_id] = time.time()
    btns = get_player_buttons(chat_id, video_id, 0, song.get('duration', 0))
    thumb = song.get('thumbnail')
    sent_msg = None
    
    if thumb and not is_video:
        try:
            sent_msg = await client.send_photo(chat_id, photo=thumb, caption=caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            if m:
                try: await m.delete()
                except: pass
        except Exception:
            if m: sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else: sent_msg = await client.send_message(chat_id, caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
    else:
        if m: sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        else: sent_msg = await client.send_message(chat_id, caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)

    if chat_id in live_timer_tasks: 
        live_timer_tasks[chat_id].cancel()
    if sent_msg:
        active_cards[chat_id] = sent_msg 
        live_timer_tasks[chat_id] = asyncio.create_task(update_live_timer(chat_id, sent_msg, song.get('duration', 0)))
