import time
from ftmgram import filters, enums
from ftmgram.types import CallbackQuery
from core.bot import app
import core.calls as calls_module
from plugins.queue import play_next_in_queue, current_songs
from utils.decorators import register_user
from utils.logger import get_logger
from utils.player_state import playback_start_times, live_timer_tasks, get_player_buttons, get_expanded_buttons, get_player_state, send_now_playing_card

logger = get_logger("Controls")

@app.on_message(filters.command("skip") & filters.group)
@register_user
async def skip_cmd(client, message):
    chat_id = message.chat.id
    if chat_id not in current_songs:
        return await message.reply_text("❌ **No song is currently playing.**")
    
    playback_start_times.pop(chat_id, None)
    if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
    
    m = await message.reply_text("⏭ **Skipping...**")
    next_song = await play_next_in_queue(chat_id)
    
    try: await m.delete()
    except: pass
    
    # 🔥 Naya Card bhejo
    if next_song:
        await send_now_playing_card(client, chat_id, next_song)

@app.on_message(filters.command(["stop", "end"]) & filters.group)
@register_user
async def stop_cmd(client, message):
    chat_id = message.chat.id
    try: await calls_module.calls.leave_call(chat_id)
    except: pass
    current_songs.pop(chat_id, None)
    playback_start_times.pop(chat_id, None)
    if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
    await message.reply_text("⏹ **Stream stopped and left VC.**")

@app.on_message(filters.command("pause") & filters.group)
@register_user
async def pause_cmd(client, message):
    chat_id = message.chat.id
    state = get_player_state(chat_id)
    try:
        await calls_module.calls.pause(chat_id)
        state["is_paused"] = True
        await message.reply_text("⏸ **Stream Paused.**")
    except: await message.reply_text("❌ **No active stream.**")

@app.on_message(filters.command("resume") & filters.group)
@register_user
async def resume_cmd(client, message):
    chat_id = message.chat.id
    state = get_player_state(chat_id)
    try:
        await calls_module.calls.resume(chat_id)
        state["is_paused"] = False
        await message.reply_text("▶️ **Stream Resumed.**")
    except: await message.reply_text("❌ **No paused stream.**")

@app.on_callback_query(filters.regex("^(pause_resume|shuffle|loop|skip|stop|seek_m10|seek_p10|more_controls|back_to_main|vol_up|vol_down)$"))
async def controls_callback(client, query: CallbackQuery):
    data, chat_id = query.data, query.message.chat.id
    state = get_player_state(chat_id)

    try:
        if data == "pause_resume":
            if state.get("is_paused", False):
                await calls_module.calls.resume(chat_id)
                state["is_paused"] = False
                await query.answer("▶️ Stream Resumed")
                playback_start_times[chat_id] = time.time() - state.get("paused_time", 0)
            else:
                await calls_module.calls.pause(chat_id)
                state["is_paused"] = True
                if chat_id in playback_start_times:
                    state["paused_time"] = time.time() - playback_start_times[chat_id]
                await query.answer("⏸ Stream Paused")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))

        elif data == "more_controls":
            await query.message.edit_reply_markup(reply_markup=get_expanded_buttons(chat_id))
            await query.answer("✨ More Controls Opened")

        elif data == "back_to_main":
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
            await query.answer("🔙 Back to Main")

        elif data in ["vol_up", "vol_down"]:
            current_vol = state.get("volume", 100)
            new_vol = min(200, current_vol + 20) if data == "vol_up" else max(10, current_vol - 20)
            state["volume"] = new_vol
            await calls_module.calls.change_volume_call(chat_id, new_vol)
            await query.answer(f"🔊 Volume: {new_vol}%")

        elif data in ["seek_m10", "seek_p10"]:
            if chat_id not in playback_start_times:
                return await query.answer("❌ No active stream.", show_alert=True)
            current_time = int(time.time() - playback_start_times[chat_id])
            seek_sec = -10 if data == "seek_m10" else 10
            new_time = max(0, current_time + seek_sec)
            await calls_module.calls.seek_stream(chat_id, new_time)
            playback_start_times[chat_id] = time.time() - new_time
            await query.answer(f"⏩ Seeked to {new_time}s")

        elif data == "skip":
            await query.answer("⏭ Skipping...")
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await query.message.delete()
            
            next_song = await play_next_in_queue(chat_id)
            if next_song:
                await send_now_playing_card(client, chat_id, next_song)
            
        elif data == "stop":
            await calls_module.calls.leave_call(chat_id)
            current_songs.pop(chat_id, None)
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await query.answer("⏹ Stream Stopped")
            await query.message.delete()
            
        elif data == "shuffle":
            state["shuffle"] = not state.get("shuffle", False)
            await query.answer(f"🔀 Shuffle {'ON' if state['shuffle'] else 'OFF'}")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
            
        elif data == "loop":
            state["loop"] = not state.get("loop", False)
            await query.answer(f"🔁 Loop {'ON' if state['loop'] else 'OFF'}")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
            
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.answer("❌ Error occurred.", show_alert=True)
