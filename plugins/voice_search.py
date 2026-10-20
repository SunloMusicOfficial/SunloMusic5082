import os
from ftmgram import filters
from core.bot import app
from utils.logger import get_logger
from plugins.play import play_handler

logger = get_logger("VoiceSearch")

@app.on_message(filters.voice & filters.group)
async def voice_search_handler(client, message):
    m = await message.reply_text("🎙 **Listening... Please wait.**")
    file_path = await client.download_media(message.voice.file_id)
    
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
            text = r.recognize_google(audio)
        
        await m.edit_text(f"🔍 **Searching for:** `{text}`")
        
        # Fake a command and call play handler
        message.command = ["/play", text]
        message.text = f"/play {text}"
        await play_handler(client, message)
        
    except sr.UnknownValueError:
        await m.edit_text("❌ **Sorry, main aawaz samajh nahi paya.** Please clear bolo.")
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
