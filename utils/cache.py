import os
import shutil
from utils.logger import get_logger
from config.settings import settings

logger = get_logger("CacheManager")

class CacheManager:
    def __init__(self):
        self.cache_dir = settings.CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get_cached_file(self, video_id: str, ext: str = "mp3"):
        file_path = os.path.join(self.cache_dir, f"{video_id}.{ext}")
        return file_path if os.path.exists(file_path) else None

    def add_to_cache(self, source_path: str, video_id: str, ext: str = "mp3") -> str:
        dest_path = os.path.join(self.cache_dir, f"{video_id}.{ext}")
        try:
            shutil.move(source_path, dest_path)
            self.clean_cache_if_needed()
            return dest_path
        except Exception:
            return source_path

    def clean_cache_if_needed(self):
        total_size = 0
        files = []
        for f in os.listdir(self.cache_dir):
            fp = os.path.join(self.cache_dir, f)
            if os.path.isfile(fp) and f != ".gitkeep":
                total_size += os.path.getsize(fp)
                files.append((fp, os.path.getmtime(fp)))
        max_bytes = settings.MAX_CACHE_SIZE_MB * 1024 * 1024
        if total_size > max_bytes:
            files.sort(key=lambda x: x[1])
            while total_size > max_bytes and files:
                oldest_file, _ = files.pop(0)
                total_size -= os.path.getsize(oldest_file)
                os.remove(oldest_file)

cache_manager = CacheManager()
