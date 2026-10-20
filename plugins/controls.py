import time
from ftmgram import filters
from ftmgram.types import CallbackQuery
from core.bot import app
import core.calls as calls_module
from plugins.queue import play_next_in_queue, get_player_state, current_songs
from utils.decorators import register_user
from utils.logger import get_logger
from plugins.play import playback_start_times, live_timer_tasks, get_player_buttons
from pytgcalls.types import MediaStream

logger = get_logger("Controls")

@app.on_message(filters.command("pitch") & filters.group)
@register_user
async def pitch_handler(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2: return await message.reply_text("🎵 **Usage:** `/pitch 1.2` (0.5 to 2.0)")
    try:
        pitch = float(message.command[1])
        if not 0.5 <= pitch <= 2.0: raise ValueError
        
        if chat_id in current_songs:
            song = current_songs[chat_id]
            stream_url = song.get("stream_url") or song.get("file_path")
            ffmpeg_args = f"-af atempo={pitch},asetrate=48000*{pitch}"
            await calls_module.calls.play(chat_id, MediaStream(stream_url, ffmpeg_parameters=ffmpeg_args))
            await message.reply_text(f"🎛 Pitch set to **{pitch}x**")
        else: await message.reply_text("❌ No song playing to apply pitch.")
    except: await message.reply_text("❌ Invalid pitch. Use `0.5` to `2.0`")

# (Baaki controls_callback code waisa hi rahega jo pichli baar tha)
@app.on_callback_query(filters.regex("^(pause_resume|shuffle|loop|skip|stop|seek_m10|seek_p10)$"))
async def controls_callback(client, query: CallbackQuery):
    data, chat_id = query.data, query.message.chat.id
    state = get_player_state(chat_id)

    try:
        if data == "pause_resume":
            if state.get("is_paused", False):
                await calls_module.calls.resume(chat_id)
                state["is_paused"] = False
                await query.answer("▶️ ꜱᴛʀᴇᴀᴍ ʀᴇꜱᴜᴍᴇᴅ")
                playback_start_times[chat_id] = time.time() - state.get("paused_time", 0)
            else:
                await calls_module.calls.pause(chat_id)
                state["is_paused"] = True
                if chat_id in playback_start_times: state["paused_time"] = time.time() - playback_start_times[chat_id]
                await query.answer("⏸️ ꜱᴛʀᴇᴀᴍ ᴘᴀᴜꜱᴇᴅ")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
        elif data in ["seek_m10", "seek_p10"]:
            if chat_id not in playback_start_times: return await query.answer("❌ No active stream.", show_alert=True)
            current_time = int(time.time() - playback_start_times[chat_id])
            seek_sec = -10 if data == "seek_m10" else 10
            new_time = max(0, current_time + seek_sec)
            await calls_module.calls.seek_stream(chat_id, new_time)
            playback_start_times[chat_id] = time.time() - new_time
            await query.answer(f"⏩ ꜱᴇᴇᴋᴇᴅ ᴛᴏ {new_time}s")
        elif data == "skip":
            await query.answer("⏭ ꜱᴋɪᴘᴘɪɴɢ...")
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await query.message.delete()
            await play_next_in_queue(chat_id)
        elif data == "stop":
            await calls_module.calls.leave_call(chat_id)
            playback_start_times.pop(chat_id, None)
            if chat_id in live_timer_tasks: live_timer_tasks[chat_id].cancel()
            await query.answer("⏹ ꜱᴛʀᴇᴀᴍ ꜱᴛᴏᴘᴘᴇᴅ")
            await query.message.delete()
        elif data == "shuffle":
            state["shuffle"] = not state.get("shuffle", False)
            await query.answer(f"🔀 ꜱʜᴜꜰꜰʟᴇ {'ᴏɴ' if state['shuffle'] else 'ᴏꜰꜰ'}")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
        elif data == "loop":
            state["loop"] = not state.get("loop", False)
            await query.answer(f"🔁 ʟᴏᴏᴘ {'ᴏɴ' if state['loop'] else 'ᴏꜰꜰ'}")
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))
    except: pass
