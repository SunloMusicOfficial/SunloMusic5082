from ftmgram import Client
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("BotClient")

# FTMGram Client initialize
app = Client(
    name="SunloMusicBot",
    api_id=settings.API_ID,
    api_hash=settings.API_HASH,
    bot_token=settings.BOT_TOKEN,
    workers=settings.DOWNLOAD_WORKERS, # Turbo workers for speed
    in_memory=True
)
