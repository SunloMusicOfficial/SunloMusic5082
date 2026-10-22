import asyncio, os
from ftmgram import filters, enums
from pytgcalls.types import MediaStream
from core.bot import app
import core.calls as calls_module
from utils.decorators import register_user
from utils.downloader import downloader
from utils.ratelimiter import is_rate_limited
from plugins.queue import add_to_queue, current_songs
from database.stats import increment_play_count
from database.users import increment_user_plays
from utils.player_state import get_player_state, send_now_playing_card, get_time_str
from utils.logger import get_logger

logger = get_logger("PlayPlugin")

@app.on_message(filters.command(["play", "vplay", "cplay"]) & (filters.group | filters.channel))
@register_user
async def play_handler(client, message):
    cmd = message.command[0].lower()
    is_video = cmd == "vplay"
    is_channel = cmd == "cplay"
    
    if not is_channel and is_rate_limited(message.from_user.id):
        return await message.reply_text("⚠️ <b>Sabar karein!</b> 3 second ka cooldown hai.", parse_mode=enums.ParseMode.HTML)
    
    try: await message.delete()
    except: pass
    
    if len(message.command) < 2: 
        return await client.send_message(message.chat.id, f"🎵 <b>Usage:</b> <code>/{cmd} <song name></code>", parse_mode=enums.ParseMode.HTML)
    
    query = " ".join(message.command[1:])
    m = await client.send_message(message.chat.id, "🔍 <b>Searching...</b>", parse_mode=enums.ParseMode.HTML)
    
    song = await downloader.search_and_extract(query)
    
    # 🔥 FIX: File exists check
    if not song or not song.get('stream_url'):
        return await m.edit_text("❌ <b>Failed.</b>\n<i>Could not extract stream URL.</i>", parse_mode=enums.ParseMode.HTML)
        
    stream_url = song['stream_url']
    if not stream_url.startswith("http"):
        if not os.path.exists(stream_url) or os.path.getsize(stream_url) < 10000:
            return await m.edit_text("❌ <b>Download failed.</b>\n<i>File was corrupted or empty. Please try again.</i>", parse_mode=enums.ParseMode.HTML)

    await play_song_by_id(client, message, m, song, is_video)

async def play_song_by_id(client, message, m, song, is_video=False):
    chat_id = message.chat.id
    
    if hasattr(message, 'from_user') and message.from_user:
        song['requester'] = message.from_user.mention
        await increment_user_plays(message.from_user.id)
    else:
        song['requester'] = "Channel"
        
    await increment_play_count(song.get('title', 'Unknown'))

    dur_str = get_time_str(song.get('duration', 0))
    title_short = song.get('title', 'Unknown')[:35] + "..." if len(song.get('title', 'Unknown')) > 35 else song.get('title', 'Unknown')

    active_calls = await calls_module.calls.calls
    if chat_id in active_calls and chat_id in current_songs:
        await add_to_queue(chat_id, song)
        queue_caption = (
            f"📥 <b>Added to Queue</b> 📥\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎵 <b>{title_short}</b>\n"
            f"⏳ <b>Duration :</b> {dur_str}\n"
            f"👤 <b>Request :</b> {song['requester']}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        thumb = song.get('thumbnail')
        try:
            if thumb:
                await m.delete()
                await client.send_photo(chat_id, photo=thumb, caption=queue_caption, parse_mode=enums.ParseMode.HTML)
            else:
                await m.edit_text(queue_caption, parse_mode=enums.ParseMode.HTML)
        except:
            await client.send_message(chat_id, queue_caption, parse_mode=enums.ParseMode.HTML)
        return

    try: await m.edit_text("▸ <b>Connecting...</b>", parse_mode=enums.ParseMode.HTML)
    except: pass
    
    try:
        # Cleanup before playing
        if chat_id in active_calls:
            try: await asyncio.wait_for(calls_module.calls.leave_call(chat_id), timeout=5)
            except: pass
            await asyncio.sleep(2)

        stream_url = song['stream_url']
        if not stream_url.startswith("http"):
            stream_url = os.path.abspath(stream_url)

        # 🔥 FIX: Increase timeout to 40s to handle slow API downloads
        await asyncio.wait_for(calls_module.calls.play(chat_id, MediaStream(stream_url)), timeout=40)
        
        current_songs[chat_id] = song
        await send_now_playing_card(client, chat_id, song, is_video, m)
        
    except asyncio.TimeoutError:
        logger.error(f"❌ PyTgCalls Play Timeout for {chat_id}")
        current_songs.pop(chat_id, None)
        try: await calls_module.calls.leave_call(chat_id)
        except: pass
        try: await m.edit_text("❌ <b>Failed to play!</b>\n<i>Voice Engine timed out. The API might be slow or file is invalid.</i>", parse_mode=enums.ParseMode.HTML)
        except: pass
    except Exception as e:
        logger.error(f"Play error: {e}")
        current_songs.pop(chat_id, None)
        try: await m.edit_text(f"❌ <b>Failed to join VC.</b>\n<code>{e}</code>", parse_mode=enums.ParseMode.HTML)
        except: pass
