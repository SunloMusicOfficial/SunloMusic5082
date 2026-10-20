import os
from utils.logger import get_logger

logger = get_logger("LogCleaner")

def clear_old_logs():
    """Bot start hote waqt purane logs clear karne ke liye."""
    log_file = "logs/bot.log"
    try:
        if os.path.exists(log_file):
            # File ka size 10MB se zyada hai toh delete karo
            if os.path.getsize(log_file) > 10 * 1024 * 1024:
                os.remove(log_file)
                logger.info("🧹 Purane logs clear kar diye gaye hain.")
    except Exception as e:
        logger.error(f"Log clear error: {e}")
