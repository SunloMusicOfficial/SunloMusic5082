from ftmgram import Client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("BotClient")
app = None

def create_bot():
    global app
    app = Client(
        name="SunloMusicBot",
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        bot_token=settings.BOT_TOKEN,
        workers=settings.DOWNLOAD_WORKERS,
        in_memory=True
    )
    return app
