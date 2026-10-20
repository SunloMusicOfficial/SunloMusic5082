import os
from PIL import Image, ImageDraw, ImageFont
from config.settings import settings

def generate_thumbnail(title: str, duration: str) -> str:
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, height-150), (width, height)], fill=(30, 30, 30))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    except IOError:
        font = ImageFont.load_default()
    text = f"🎵 {title[:50]}..."
    draw.text((50, height-110), text, fill=(255, 255, 255), font=font)
    draw.text((width-250, height-90), duration, fill=(200, 200, 200), font=font)
    thumb_path = os.path.join(settings.CACHE_DIR, f"thumb_{int(os.urandom(2).hex(), 16)}.jpg")
    img.save(thumb_path)
    return thumb_path
