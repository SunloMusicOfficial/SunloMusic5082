import asyncio, time, re
from ftmgram import enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.logger import get_logger

logger = get_logger("PlayerState")

playback_start_times = {}
live_timer_tasks = {}
chat_states = {}
active_cards = {} # 🔥 Track Current Playing Message

def get_player_state(chat_id):
    if chat_id not in chat_states:
        chat_states[chat_id] = {"is_paused": False, "loop": False, "shuffle": False, "volume": 100}
    return chat_states[chat_id]

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
    play_btn = "▶️ ʀᴇꜱᴜᴍᴇ" if state.get("is_paused", False) else "⏸️ ᴘᴀᴜꜱᴇ"
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state.get("loop", False) else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state.get("shuffle", False) else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(play_btn, callback_data="pause_resume"), InlineKeyboardButton("⏭️ ꜱᴋɪᴘ", callback_data="skip")],
        [InlineKeyboardButton(shuffle_btn, callback_data="shuffle"), InlineKeyboardButton(loop_btn, callback_data="loop")],
        [InlineKeyboardButton("✨ ᴍᴏʀᴇ ᴄᴏɴᴛʀᴏʟꜱ", callback_data="more_controls")]
    ])

def get_expanded_buttons(chat_id):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⏪ -10ꜱ", callback_data="seek_m10"), InlineKeyboardButton("⏩ +10ꜱ", callback_data="seek_p10")],
        [InlineKeyboardButton("🔊 ᴠᴏʟᴜᴍᴇ +", callback_data="vol_up"), InlineKeyboardButton("🔉 ᴠᴏʟᴜᴍᴇ -", callback_data="vol_down")],
        [InlineKeyboardButton("⏹️ ꜱᴛᴏᴘ ꜱᴛʀᴇᴀᴍ", callback_data="stop")],
        [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴀɪɴ", callback_data="back_to_main")]
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

async def delete_active_card(chat_id):
    if chat_id in active_cards:
        try: await active_cards[chat_id].delete()
        except: pass
        del active_cards[chat_id]

async def send_now_playing_card(client, chat_id, song, is_video=False, m=None):
    # 🔥 Purana card delete karo
    await delete_active_card(chat_id)

    dur_str = get_time_str(song.get('duration', 0))
    title_short = song.get('title', 'Unknown')[:35] + "..." if len(song.get('title', 'Unknown')) > 35 else song.get('title', 'Unknown')
    requester = song.get('requester', 'Channel')
    
    caption = (
        f"<blockquote>🎧 <b>𝐒𝐓𝐑𝐄𝐀𝐌𝐈𝐍𝐆 {'𝐕𝐈𝐃𝐄𝐎' if is_video else '𝐍𝐎𝐖'}</b>\n\n"
        f"🎵 <b>{title_short}</b>\n⏳ <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 :</b> {dur_str}\n"
        f"👤 <b>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 :</b> {requester}</blockquote>\n"
        f"<code>00:00</code> {generate_bar(0, song.get('duration', 0))} <code>{dur_str}</code>"
    )

    playback_start_times[chat_id] = time.time()
    btns = get_player_buttons(chat_id)
    thumb = song.get('thumbnail')
    sent_msg = None
    
    if thumb and not is_video:
        try:
            sent_msg = await client.send_photo(chat_id, photo=thumb, caption=caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            if m:
                try: await m.delete()
                except: pass
        except Exception as e:
            logger.error(f"Thumbnail send failed: {e}")
            if m: sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else: sent_msg = await client.send_message(chat_id, caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
    else:
        if m: sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        else: sent_msg = await client.send_message(chat_id, caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)

    if chat_id in live_timer_tasks: 
        live_timer_tasks[chat_id].cancel()
    if sent_msg:
        active_cards[chat_id] = sent_msg # 🔥 Save current card
        live_timer_tasks[chat_id] = asyncio.create_task(update_live_timer(chat_id, sent_msg, song.get('duration', 0)))
