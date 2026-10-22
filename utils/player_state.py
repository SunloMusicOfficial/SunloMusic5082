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
        chat_states[chat_id] = {"is_paused": False, "loop": False, "shuffle": False, "volume": 100, "autoplay": False}
    return chat_states[chat_id]

def get_time_str(sec):
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"

def generate_bar(current, total, length=10):
    if total == 0: return "─" * length
    played = int((current / total) * length)
    if played >= length: played = length
    return "▬" * played + "🔘" + "─" * (length - played)

def get_player_buttons(chat_id, video_id, title):
    state = get_player_state(chat_id)
    play_btn = "▶️" if state.get("is_paused", False) else "⏸"
    loop_btn = "🔁 ᴏɴ" if state.get("loop", False) else "🔁 ᴏꜰꜰ"
    shuffle_btn = "🔀 ᴏɴ" if state.get("shuffle", False) else "🔀 ᴏꜰꜰ"
    auto_btn = "✅ ᴀᴜᴛᴏᴘʟᴀʏ" if state.get("autoplay", False) else "🔄 ᴀᴜᴛᴏᴘʟᴀʏ"
    
    # URL to search on YouTube
    yt_url = f"https://youtube.com/results?search_query={title.replace(' ', '+')}"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔍 𝐕𝐢𝐝𝐞𝐨 𝐋𝐢𝐧𝐤", url=yt_url),
            InlineKeyboardButton("📥 𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝", url=f"https://t.me/{settings.BOT_USERNAME.replace('@', '')}?start=song_{video_id}")
        ],
        [
            InlineKeyboardButton(play_btn, callback_data="pause_resume"),
            InlineKeyboardButton("⏭", callback_data="skip"),
            InlineKeyboardButton("⏹", callback_data="stop")
        ],
        [
            InlineKeyboardButton(auto_btn, callback_data="autoplay"),
            InlineKeyboardButton(shuffle_btn, callback_data="shuffle"),
            InlineKeyboardButton(loop_btn, callback_data="loop")
        ]
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
            btns = get_player_buttons(chat_id, "", "")
            if message.caption: await message.edit_caption(caption=new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
            else: await message.edit_text(new_caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        except: pass

async def delete_active_card(chat_id):
    if chat_id in active_cards:
        try: await active_cards[chat_id].delete()
        except: pass
        del active_cards[chat_id]

async def send_now_playing_card(client, chat_id, song, is_video=False, m=None):
    await delete_active_card(chat_id)
    
    dur_str = get_time_str(song.get('duration', 0))
    title_short = song.get('title', 'Unknown')[:40] + "..." if len(song.get('title', 'Unknown')) > 40 else song.get('title', 'Unknown')
    requester = song.get('requester', 'Channel')
    
    # 🔥 Premium Caption (Buttons se pehle timer)
    caption = (
        f"<blockquote>🎧 <b>𝐍𝐨𝐰 𝐏𝐥𝐚𝐲𝐢𝐧𝐠</b>\n\n"
        f"▶️ <b>𝐓𝐢𝐭𝐥𝐞 :</b> {title_short}\n"
        f"⏳ <b>𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 :</b> {dur_str}\n"
        f"👤 <b>𝐑𝐞𝐪𝐮𝐞𝐬𝐭 :</b> {requester}</blockquote>\n\n"
        f"<code>00:00</code> {generate_bar(0, song.get('duration', 0))} <code>{dur_str}</code>"
    )

    playback_start_times[chat_id] = time.time()
    btns = get_player_buttons(chat_id, song.get('id', ''), song.get('title', ''))
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
