import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    OWNER_ID = int(os.getenv("OWNER_ID", 0))
    SUDO_USERS = [int(x) for x in os.getenv("SUDO_USERS", "").split() if x]
    MONGO_URI = os.getenv("MONGO_URI", "")
    DB_NAME = os.getenv("DB_NAME", "SunloMusic")
    BOT_NAME = os.getenv("BOT_NAME", "Sunlo Music")
    BOT_USERNAME = os.getenv("BOT_USERNAME", "@SunloMusicBot")
    SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", "")
    SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "")
    LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", 0))
    LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", 0))
    
    # 🔥 AAPKI API KEY (FallenApi)
    SUNLO_API_KEY = os.getenv("SUNLO_API_KEY", "").strip()
    AUDD_API_KEY = os.getenv("AUDD_API_KEY", "").strip()
    RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()

    CACHE_DIR = os.getenv("CACHE_DIR", "cache")
    MAX_CACHE_SIZE_MB = int(os.getenv("MAX_CACHE_SIZE_MB", 2048))
    PRELOAD_NEXT = os.getenv("PRELOAD_NEXT", "True").lower() == "true"
    DOWNLOAD_WORKERS = int(os.getenv("DOWNLOAD_WORKERS", 4))
    START_IMG_URL = os.getenv("START_IMG_URL", "")
    DEFAULT_VOLUME = int(os.getenv("DEFAULT_VOLUME", 100))
    MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", 50))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        required = ["API_ID", "API_HASH", "BOT_TOKEN", "SESSION_STRING", "OWNER_ID", "MONGO_URI"]
        missing = [k for k in required if not getattr(cls, k)]
        if missing:
            raise ValueError(f"❌ Missing required env vars: {', '.join(missing)}")
        return True

settings = Settings()
