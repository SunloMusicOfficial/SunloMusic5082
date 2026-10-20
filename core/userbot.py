from pyrogram import Client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("UserbotClient")
userbot = None

def create_userbot():
    global userbot
    userbot = Client(
        name="SunloMusicAssistant",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        session_string=settings.SESSION_STRING,
        workers=settings.DOWNLOAD_WORKERS,
        in_memory=True
    )
    return userbot
