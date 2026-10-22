import time
from ftmgram import filters, enums
from ftmgram.types import CallbackQuery
from core.bot import app
import core.calls as calls_module
from plugins.queue import play_next_in_queue, current_songs
from utils.decorators import register_user
from utils.logger import get_logger
from utils.player_state import playback_start_times, live_timer_tasks, get_player_buttons, get_expanded_buttons, get_player_state, send_now_playing_card, delete_active_card

logger = get_logger("Controls")

@app.on_message(filters.command("skip") & filters.group)
@register_user
async def skip_cmd(client, message):
    try: await message.delete()
    except: pass
    chat_id = message.chat.id
    if chat_id not in current_songs: return
    playback_start_times.pop(chat_id, None)
    if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
    await delete_active_card(chat_id)
    m = await client.send_message(chat_id, "⏭ **Skipping...**")
    next_song = await play_next_in_queue(chat_id)
    try: await m.delete()
    except: pass
    if next_song: await send_now_playing_card(client, chat_id, next_song)

@app.on_message(filters.command(["stop", "end"]) & filters.group)
@register_user
async def stop_cmd(client, message):
    try: await message.delete()
    except: pass
    chat_id = message.chat.id
    try: await calls_module.calls.leave_call(chat_id)
    except: pass
    current_songs.pop(chat_id, None)
    playback_start_times.pop(chat_id, None)
    if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
    await delete_active_card(chat_id)

@app.on_message(filters.command("pause") & filters.group)
@register_user
async def pause_cmd(client, message):
    try: await message.delete()
    except: pass
    chat_id = message.chat.id
    try:
        await calls_module.calls.pause(chat_id)
        get_player_state(chat_id)["is_paused"] = True
    except: pass

@app.on_message(filters.command("resume") & filters.group)
@register_user
async def resume_cmd(client, message):
    try: await message.delete()
    except: pass
    chat_id = message.chat.id
    try:
        await calls_module.calls.resume(chat_id)
        get_player_state(chat_id)["is_paused"] = False
    except: pass

@app.on_callback_query(filters.regex("^(pause_resume|shuffle|loop|skip|stop|autoplay|more_controls|back_to_main|seek_m10|seek_p10|ignore)$"))
async def controls_callback(client, query: CallbackQuery):
    data, chat_id = query.data, query.message.chat.id
    state = get_player_state(chat_id)
    
    def refresh_main():
        song = current_songs.get(chat_id, {})
        elapsed = int(time.time() - playback_start_times.get(chat_id, time.time())) if chat_id in playback_start_times else 0
        return get_player_buttons(chat_id, song.get('id', ''), elapsed, song.get('duration', 0))

    try:
        if data == "ignore": return await query.answer()

        if data == "pause_resume":
            if state.get("is_paused", False):
                await calls_module.calls.resume(chat_id)
                state["is_paused"] = False
                await query.answer("▶️ Resumed")
                playback_start_times[chat_id] = time.time() - state.get("paused_time", 0)
            else:
                await calls_module.calls.pause(chat_id)
                state["is_paused"] = True
                if chat_id in playback_start_times:
                    state["paused_time"] = time.time() - playback_start_times[chat_id]
                await query.answer("⏸ Paused")
            await query.message.edit_reply_markup(reply_markup=refresh_main())

        elif data == "autoplay":
            state["autoplay"] = not state.get("autoplay", False)
            await query.answer(f"🔄 Autoplay {'ON' if state['autoplay'] else 'OFF'}")
            await query.message.edit_reply_markup(reply_markup=refresh_main())

        elif data == "more_controls":
            song = current_songs.get(chat_id, {})
            elapsed = int(time.time() - playback_start_times.get(chat_id, time.time())) if chat_id in playback_start_times else 0
            await query.message.edit_reply_markup(reply_markup=get_expanded_buttons(chat_id, elapsed, song.get('duration', 0)))
            await query.answer("✨ More Controls")

        elif data == "back_to_main":
            await query.message.edit_reply_markup(reply_markup=refresh_main())
            await query.answer("🔙 Back")

        elif data == "skip":
            await query.answer("⏭ Skipping...")
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await delete_active_card(chat_id)
            await query.message.delete()
            next_song = await play_next_in_queue(chat_id)
            if next_song: await send_now_playing_card(client, chat_id, next_song)
            
        elif data == "stop":
            await calls_module.calls.leave_call(chat_id)
            current_songs.pop(chat_id, None)
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await query.answer("⏹ Stopped")
            await delete_active_card(chat_id)
            
        elif data == "shuffle":
            state["shuffle"] = not state.get("shuffle", False)
            await query.answer(f"🔀 Shuffle {'ON' if state['shuffle'] else 'OFF'}")
            song = current_songs.get(chat_id, {})
            await query.message.edit_reply_markup(reply_markup=get_expanded_buttons(chat_id, 0, song.get('duration', 0)))
            
        elif data == "loop":
            state["loop"] = not state.get("loop", False)
            await query.answer(f"🔁 Loop {'ON' if state['loop'] else 'OFF'}")
            song = current_songs.get(chat_id, {})
            await query.message.edit_reply_markup(reply_markup=get_expanded_buttons(chat_id, 0, song.get('duration', 0)))

        elif data in ["seek_m10", "seek_p10"]:
            if chat_id not in playback_start_times: return await query.answer("❌ No active stream.")
            current_time = int(time.time() - playback_start_times[chat_id])
            seek_sec = -10 if data == "seek_m10" else 10
            new_time = max(0, current_time + seek_sec)
            
            # 🔥 FIX: PyTgCalls v3 uses .seek() instead of .seek_stream()
            await calls_module.calls.seek(chat_id, new_time)
            
            playback_start_times[chat_id] = time.time() - new_time
            await query.answer(f"⏩ Seeked to {new_time}s")
            song = current_songs.get(chat_id, {})
            await query.message.edit_reply_markup(reply_markup=get_expanded_buttons(chat_id, new_time, song.get('duration', 0)))
            
    except Exception as e:
        logger.error(f"Callback error: {e}")
        await query.answer("❌ Error occurred.", show_alert=True)
