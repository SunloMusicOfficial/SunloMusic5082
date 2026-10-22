import asyncio
import os
import PIL.Image
from google import genai
from google.genai import types
from ftmgram import filters, enums
from ftmgram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.bot import app
from config.settings import settings
from utils.decorators import register_user
from utils.logger import get_logger
from database.chats import set_chat_setting, get_chat_setting

logger = get_logger("SunloMusicOfficialAi")

# 🔥 NEW SUNLO AI ENGINE (google-genai)
if settings.SUNLO_AI_KEY:
    ai_client = genai.Client(api_key=settings.SUNLO_AI_KEY)
else:
    logger.warning("⚠️ SUNLO_AI_KEY is missing. Assistant won't work.")
    ai_client = None

chat_sessions = {}

# 🔥 CUSTOM PERSONA PROMPT (Bilingual + No AI vibes)
SYSTEM_PROMPT = (
    "You are 'Sunlo', a highly intelligent and premium human-like assistant for the Telegram bot 'Sunlo Music'. "
    "You are NOT an AI, a language model, or Gemini. You are a virtual member of the Sunlo Music Team. "
    "If anyone asks who you are, or if you are an AI/ChatGPT/Gemini, you must deny it and say: "
    "'I am Sunlo, the assistant for Sunlo Music. I am here to help you with music and anything else you need.' "
    "IMPORTANT: You must be bilingual. Automatically detect the user's language. "
    "If the user speaks in English, reply in English. "
    "If the user speaks in Hindi or Hinglish (Hindi written in English alphabets), reply in friendly Hinglish. "
    "Your tone should be friendly, slightly witty, and very helpful. You love music. "
    "Keep your answers concise (under 100 words), natural, and use emojis occasionally. "
    "Do NOT use any markdown formatting like bolding or italics, just plain text with emojis."
)

def get_assistant_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", callback_data="ai_regen"),
         InlineKeyboardButton("🧹 ʀᴇꜱᴇᴛ ᴄʜᴀᴛ", callback_data="ai_clear")]
    ])

async def get_ai_response(chat_id, text, image_path=None):
    if chat_id not in chat_sessions:
        # Create new chat session with context
        chat_sessions[chat_id] = {
            "chat": ai_client.chats.create(model="gemini-1.5-flash"),
            "last_query": "",
            "last_img": None
        }
        # Send system prompt silently
        await asyncio.to_thread(chat_sessions[chat_id]["chat"].send_message, SYSTEM_PROMPT)
    
    chat = chat_sessions[chat_id]["chat"]
    
    if image_path and os.path.exists(image_path):
        img = PIL.Image.open(image_path)
        response = await asyncio.to_thread(chat.send_message, [text, img])
        os.remove(image_path)
    else:
        response = await asyncio.to_thread(chat.send_message, text)
        
    chat_sessions[chat_id]["last_query"] = text
    chat_sessions[chat_id]["last_img"] = image_path
        
    return response.text

@app.on_message(filters.command(["ask", "sunlo"]) & filters.group)
@register_user
async def ask_ai(client, message):
    if not ai_client:
        return await message.reply_text("⚠️ Sunlo is currently offline for maintenance.")

    if len(message.command) < 2 and not (message.reply_to_message and message.reply_to_message.photo):
        return await message.reply_text("✨ **Usage:** `/ask <question>`\nYa kisi image ko reply karke `/ask <question>` likhein.")

    query = " ".join(message.command[1:]) if len(message.command) > 1 else "What is in this image?"
    
    image_path = None
    if message.reply_to_message and message.reply_to_message.photo:
        m = await message.reply_text("🖼️ **Checking image...**")
        image_path = await client.download_media(message.reply_to_message.photo)
        try: await m.delete()
        except: pass
    else:
        m = await message.reply_text("✨ **Sunlo is typing...**")

    try:
        await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
        reply_text = await get_ai_response(message.chat.id, query, image_path)
        
        final_text = (
            f"<blockquote>✨ <b>𝐒𝐮𝐧𝐥𝐨</b>\n\n"
            f"{reply_text}</blockquote>"
        )
        await m.edit_text(final_text, reply_markup=get_assistant_buttons(), parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        logger.error(f"Sunlo Error: {e}")
        await m.edit_text("❌ **Sunlo is taking a short break. Please try again.**")

@app.on_callback_query(filters.regex("^(ai_regen|ai_clear)$"))
async def ai_callbacks(client, query):
    data, chat_id = query.data, query.message.chat.id
    
    if data == "ai_clear":
        if chat_id in chat_sessions:
            del chat_sessions[chat_id]
        await query.answer("🧹 Chat reset! I forgot our previous conversation.", show_alert=True)
        try: await query.message.delete()
        except: pass
        
    elif data == "ai_regen":
        if chat_id not in chat_sessions or not chat_sessions[chat_id]["last_query"]:
            return await query.answer("❌ No previous message found.", show_alert=True)
            
        await query.answer("🔄 Replying again...", show_alert=False)
        await query.message.edit_text("✨ **Sunlo is typing...**", parse_mode=enums.ParseMode.HTML)
        
        try:
            last_query = chat_sessions[chat_id]["last_query"]
            last_img = chat_sessions[chat_id]["last_img"]
            
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            reply_text = await get_ai_response(chat_id, last_query, last_img)
            
            final_text = (
                f"<blockquote>✨ <b>𝐒𝐮𝐧𝐥𝐨</b>\n\n"
                f"{reply_text}</blockquote>"
            )
            await query.message.edit_text(final_text, reply_markup=get_assistant_buttons(), parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            await query.message.edit_text(f"❌ **Error:** Sunlo is resting.")

# ── AUTO-REPLY WATCHER ──
@app.on_message(filters.text & filters.group & ~filters.bot, group=4)
async def ai_auto_reply(client, message):
    if not ai_client: return
    
    chat_id = message.chat.id
    is_enabled = await get_chat_setting(chat_id, "chatbot_enabled", False)
    if not is_enabled: return
    
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.is_self
    is_mention = f"@{settings.BOT_USERNAME.replace('@', '')}" in message.text
    
    if not (is_reply_to_bot or is_mention): return
        
    query = message.text.replace(f"@{settings.BOT_USERNAME}", "").strip()
    if not query: return

    m = await message.reply_text("✨ **Sunlo is typing...**")

    try:
        await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
        reply_text = await get_ai_response(chat_id, query)
        
        final_text = (
            f"<blockquote>✨ <b>𝐒𝐮𝐧𝐥𝐨</b>\n\n"
            f"{reply_text}</blockquote>"
        )
        await m.edit_text(final_text, reply_markup=get_assistant_buttons(), parse_mode=enums.ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Auto Reply Error: {e}")
        await m.edit_text("❌ Sunlo is busy right now.")

@app.on_message(filters.command("setchatbot") & filters.group)
@register_user
async def set_chatbot(client, message):
    if len(message.command) < 2:
        status = await get_chat_setting(message.chat.id, "chatbot_enabled", False)
        return await message.reply_text(f"✨ **Sunlo Auto-Reply is {'ON' if status else 'OFF'}**\n\nUsage: `/setchatbot on` or `off`")
    
    state = message.command[1].lower() == "on"
    await set_chat_setting(message.chat.id, "chatbot_enabled", state)
    
    if state:
        await message.reply_text("✅ **Sunlo is now active in this group!**\nMention karo ya reply karke baat karo.")
    else:
        await message.reply_text("❌ **Sunlo Auto-Reply is now OFF.**")
