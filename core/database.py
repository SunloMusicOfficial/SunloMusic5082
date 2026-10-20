from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings
from utils.logger import get_logger

logger = get_logger("Database")

class Database:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(settings.MONGO_URI)
            self.db = self.client[settings.DB_NAME]
            # Ping to verify connection
            await self.client.admin.command('ping')
            logger.info("MongoDB Connected successfully!")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise e

    async def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB Disconnected.")

db = Database()
