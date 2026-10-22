import asyncio, time, re, os
from ftmgram import enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.logger import get_logger
from config.settings import settings
from PIL import Image, ImageDraw, ImageFont

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

# 🔥 TIMER 10 (MOTA LINE)
def generate_bar(current, total, length=8):
    if total == 0: return "━" * length
    played = int((current / total) * length)
    if played >= length: played = length - 1
    rem = length - played - 1
    return "♪" * played + "🎵" + "━" * rem

# 🔥 LAYOUT 14
def get_player_buttons(chat_id, video_id, current=0, total=0):
    state = get_player_state(chat_id)
    play_text = "▶️ ʀᴇꜱᴜᴍᴇ" if state.get("is_paused", False) else "⏸ ᴘᴀᴜꜱᴇ"
    time_btn_text = f"{get_time_str(current)} {generate_bar(current, total)} {get_time_str(total)}"
    
    auto_btn = "✅ ᴀᴜᴛᴏ ᴏɴ" if state.get("autoplay", False) else "🎵 ᴀᴜᴛᴏ ᴏꜰꜰ"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(time_btn_text, callback_data="ignore")],
        [InlineKeyboardButton(play_text, callback_data="pause_resume"), InlineKeyboardButton("⏭ ꜱᴋɪᴘ", callback_data="skip")],
        [InlineKeyboardButton(auto_btn, callback_data="autoplay"), InlineKeyboardButton("🔇 ꜱᴛᴏᴘ", callback_data="stop")],
        [InlineKeyboardButton("🎶 ᴍᴏʀᴇ", callback_data="more_controls")]
    ])

def get_expanded_buttons(chat_id, current=0, total=0):
    state = get_player_state(chat_id)
    loop_btn = "🔁 ʟᴏᴏᴘ ᴏɴ" if state.get("loop", False) else "🔁 ʟᴏᴏᴘ ᴏꜰꜰ"
    shuffle_btn = "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏɴ" if state.get("shuffle", False) else "🔀 ꜱʜᴜꜰꜰʟᴇ ᴏꜰꜰ"

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(shuffle_btn, callback_data="shuffle"), InlineKeyboardButton(loop_btn, callback_data="loop")],
        [InlineKeyboardButton("⏪ -10ꜱ", callback_data="seek_m10"), InlineKeyboardButton("+10ꜱ ⏩", callback_data="seek_p10")],
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

# 🔥 WATERMARK FUNCTION
def add_watermark(image_path):
    try:
        img = Image.open(image_path).convert("RGBA")
        draw = ImageDraw.Draw(img)
        # Default font (jaisa server par available ho)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
            
        text = "SUNLO MUSIC"
        # Image ke bottom right mein text add karo
        width, height = img.size
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = width - text_width - 20
        y = height - text_height - 20
        
        # Text ke peeche shadow
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 150))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 200))
        
        new_path = image_path.replace(".jpg", "_wm.jpg")
        img.convert("RGB").save(new_path, "JPEG")
        return new_path
    except Exception as e:
        logger.error(f"Watermark failed: {e}")
        return image_path

async def send_now_playing_card(client, chat_id, song, is_video=False, m=None):
    await delete_active_card(chat_id)
    
    title_short = song.get('title', 'Unknown')[:35] + "..." if len(song.get('title', 'Unknown')) > 35 else song.get('title', 'Unknown')
    dur_str = get_time_str(song.get('duration', 0))
    requester = song.get('requester', 'Channel')
    video_id = song.get('id', '')
    
    bot_username = settings.BOT_USERNAME.replace('@', '')
    title_link = f'<a href="https://t.me/{bot_username}?start=song_{video_id}">{title_short}</a>'
    
    # 🔥 CAPTION FIX (Length ki jagah Duration)
    caption = (
        f"🎧🎶 <b>Music Time</b> 🎶🎧\n\n"
        f"🎵 {title_link}\n"
        f"⏱ <b>Duration:</b> {dur_str}\n"
        f"🙋‍♂️ <b>Request:</b> {requester}"
    )

    playback_start_times[chat_id] = time.time()
    btns = get_player_buttons(chat_id, video_id, 0, song.get('duration', 0))
    thumb = song.get('thumbnail')
    sent_msg = None
    
    if thumb and not is_video:
        try:
            # Download image, add watermark, then send
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(thumb) as resp:
                    if resp.status == 200:
                        img_data = await resp.read()
                        temp_path = f"cache/temp_thumb_{video_id}.jpg"
                        with open(temp_path, "wb") as f:
                            f.write(img_data)
                        
                        wm_path = add_watermark(temp_path)
                        
                        sent_msg = await client.send_photo(chat_id, photo=wm_path, caption=caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
                        
                        # Cleanup
                        if os.path.exists(temp_path): os.remove(temp_path)
                        if os.path.exists(wm_path) and wm_path != temp_path: os.remove(wm_path)
                        if m:
                            try: await m.delete()
                            except: pass
                        thumb = None # Set to none so we don't send below
        except Exception as e:
            logger.error(f"Thumb error: {e}")

    if not sent_msg:
        if m: sent_msg = await m.edit_text(caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)
        else: sent_msg = await client.send_message(chat_id, caption, reply_markup=btns, parse_mode=enums.ParseMode.HTML)

    if chat_id in live_timer_tasks: 
        live_timer_tasks[chat_id].cancel()
    if sent_msg:
        active_cards[chat_id] = sent_msg 
        live_timer_tasks[chat_id] = asyncio.create_task(update_live_timer(chat_id, sent_msg, song.get('duration', 0)))
