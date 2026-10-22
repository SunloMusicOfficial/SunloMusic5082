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

# 🔥 TIMER 10 (MODIFIED - MOTA LINE)
def generate_bar(current, total, length=10):
    if total == 0: return "─" * length
    played = int((current / total) * length)
    if played >= length: played = length - 1
    rem = length - played - 1
    return "♪" * played + "🎵" + "━" * rem

def get_player_buttons(chat_id, video_id, current=0, total=0):
    state = get_player_state(chat_id)
    play_text = "▶️ ʀᴇꜱᴜᴍᴇ" if state.get("is_paused", False) else "⏸ ᴘᴀᴜꜱᴇ"
    auto_btn = "✅ ᴀᴜᴛᴏᴘʟᴀʏ ᴏɴ" if state.get("autoplay", False) else "🔄 ᴀᴜᴛᴏᴘʟᴀʏ ᴏꜰꜰ"
    
    time_btn_text = f"{get_time_str(current)} {generate_bar(current, total)} {get_time_str(total)}"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(time_btn_text, callback_data="ignore")], # Timer
        [
            InlineKeyboardButton(play_text, callback_data="pause_resume"), # Pause | Skip
            InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="skip")
        ],
        [
            InlineKeyboardButton(auto_btn, callback_data="autoplay") # Autoplay
        ],
        [
            InlineKeyboardButton("✨ ᴍᴏʀᴇ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="more_controls") # More Controls
        ]
    ])

def get_expanded_buttons(chat_id, current=0, total=0):
    state = get_player_state(chat_id)
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state.get("loop", False) else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state.get("shuffle", False) else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏪ -10ꜱ", callback_data="seek_m10"), InlineKeyboardButton("⏩ +10ꜱ", callback_data="seek_p10")],
        [InlineKeyboardButton(shuffle_btn, callback_data="shuffle"), InlineKeyboardButton(loop_btn, callback_data="loop")],
        [InlineKeyboardButton("⏹ ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍ", callback_data="stop")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ", callback_data="back_to_main")]
    ])

async def update_live_timer(chat_id, message, duration_sec):
    from plugins.queue import current_songs
    while chat_id in playback_start_times:
        await asyncio.sleep(5) 
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
    
    title_short = song.get('title', 'Unknown')[:35] + "..." if len(song.get('title', 'Unknown')) > 35 else song.get('title', 'Unknown')
    dur_str = get_time_str(song.get('duration', 0))
    requester = song.get('requester', 'Channel')
    video_id = song.get('id', '')
    
    bot_username = settings.BOT_USERNAME.replace('@', '')
    title_link = f'<a href="https://t.me/{bot_username}?start=song_{video_id}">{title_short}</a>'
    
    # 🔥 AAPKE CHUNE HUE 4 STYLES
    CAPTION_STYLE = 8 # <--- YAHAN NUMBER CHANGE KARO: 8, 10, 15, ya 16
    
    if CAPTION_STYLE == 8:
        # Style 8: The Emoji Heavy
        caption = (
            f"🎧🎶 <b>Music Time</b> 🎶🎧\n\n"
            f"🎵 {title_link}\n"
            f"⏳ Length: {dur_str}\n"
            f"🙋‍♂️ Request: {requester}"
        )
    elif CAPTION_STYLE == 10:
        # Style 10: The Love / Romantic
        caption = (
            f"💖 <b>Playing with Love</b> 💖\n\n"
            f"🎵 {title_link}\n"
            f"⏳ {dur_str}\n"
            f"💌 Dedicated to: {requester}"
        )
    elif CAPTION_STYLE == 15:
        # Style 15: The Subtle Dark
        caption = (
            f"🖤 <b>Playing</b>\n\n"
            f"🎶 {title_link}\n"
            f"🕒 {dur_str}\n"
            f"👤 {requester}"
        )
    elif CAPTION_STYLE == 16:
        # Style 16: The "Sunlo" Branded
        caption = (
            f"☀️ <b>Sunlo Music</b>\n\n"
            f"🎵 {title_link}\n"
            f"⏳ {dur_str}\n"
            f"🎙 {requester}"
        )
    else:
        # Fallback
        caption = f"🎧 <b>Now Playing</b>\n\n▶️ {title_link}\n⏳ {dur_str}\n👤 {requester}"

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
