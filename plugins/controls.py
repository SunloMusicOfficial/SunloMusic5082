import time
from ftmgram import filters
from ftmgram.types import CallbackQuery
from core.bot import app
import core.calls as calls_module
from plugins.queue import play_next_in_queue
from utils.logger import get_logger
from plugins.play import playback_start_times, live_timer_tasks, chat_states, get_player_buttons

logger = get_logger("Controls")

# SIRF MUSIC BUTTONS KO PAKADNE KE LIYE FILTER
@app.on_callback_query(filters.regex("^(pause_resume|shuffle|loop|skip|stop)$"))
async def controls_callback(client, query: CallbackQuery):
    data = query.data
    chat_id = query.message.chat.id
    state = chat_states.get(chat_id, {"is_paused": False, "loop": False, "shuffle": False})

    try:
        if data == "pause_resume":
            if state.get("is_paused", False):
                await calls_module.calls.resume(chat_id)
                state["is_paused"] = False
                await query.answer("▶️ ꜱᴛʀᴇᴀᴍ ʀᴇꜱᴜᴍᴇᴅ", show_alert=False)
                playback_start_times[chat_id] = time.time() - state.get("paused_time", 0)
            else:
                await calls_module.calls.pause(chat_id)
                state["is_paused"] = True
                if chat_id in playback_start_times:
                    state["paused_time"] = time.time() - playback_start_times[chat_id]
                await query.answer("⏸️ ꜱᴛʀᴇᴀᴍ ᴘᴀᴜꜱᴇᴅ", show_alert=False)
            
            chat_states[chat_id] = state
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))

        elif data == "shuffle":
            state["shuffle"] = not state.get("shuffle", False)
            chat_states[chat_id] = state
            status = "ᴇɴᴀʙʟᴇᴅ" if state["shuffle"] else "ᴅɪꜱᴀʙʟᴇᴅ"
            await query.answer(f"🔀 ꜱʜᴜꜰꜰʟᴇ {status}", show_alert=False)
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))

        elif data == "loop":
            state["loop"] = not state.get("loop", False)
            chat_states[chat_id] = state
            status = "ᴇɴᴀʙʟᴇᴅ" if state["loop"] else "ᴅɪꜱᴀʙʟᴇᴅ"
            await query.answer(f"🔁 ʟᴏᴏᴘ {status}", show_alert=False)
            await query.message.edit_reply_markup(reply_markup=get_player_buttons(chat_id))

        elif data == "skip":
            await query.answer("⏭ ꜱᴋɪᴘᴘɪɴɢ...", show_alert=False)
            playback_start_times.pop(chat_id, None)
            chat_states.pop(chat_id, None)
            if chat_id in live_timer_tasks:
                live_timer_tasks[chat_id].cancel()
            await query.message.delete()
            await play_next_in_queue(chat_id)

        elif data == "stop":
            await calls_module.calls.leave_call(chat_id)
            playback_start_times.pop(chat_id, None)
            chat_states.pop(chat_id, None)
            if chat_id in live_timer_tasks:
                live_timer_tasks[chat_id].cancel()
            await query.answer("⏹ ꜱᴛʀᴇᴀᴍ ꜱᴛᴏᴘᴘᴇᴅ", show_alert=False)
            await query.message.delete()

    except Exception as e:
        logger.error(f"Callback Error: {e}")
        await query.answer("❌ ᴇʀʀᴏʀ: ɴᴏ ᴀᴄᴛɪᴠᴇ ꜱᴛʀᴇᴀᴍ.", show_alert=False)
