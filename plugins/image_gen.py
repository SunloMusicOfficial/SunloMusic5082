import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from ftmgram import filters
from ftmgram.types import Message
from core.bot import app
from config.settings import settings
from utils.decorators import register_user
from utils.logger import get_logger

logger = get_logger("ImageGen")

def get_font(size, bold=True):
    try:
        # Default Ubuntu/Termux font path
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(font_path, size)
    except IOError:
        return ImageFont.load_default()

@app.on_message(filters.command("makestart"))
@register_user
async def make_start_handler(client, message: Message):
    m = await message.reply_text("🎨 **Generating Ultra-Premium Start Image...**")

    photo_path = None
    # Agar user ne kisi photo par reply kiya hai
    if message.reply_to_message and message.reply_to_message.photo:
        await m.edit_text("🖼 **Downloading your photo for background...**")
        photo_path = await client.download_media(message.reply_to_message.photo.file_id)

    width, height = 1280, 720

    # Background Setup
    if photo_path and os.path.exists(photo_path):
        # User's photo use karo aur blur karo
        bg = Image.open(photo_path).convert("RGB")
        bg = bg.resize((width, height), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(20)) # Premium Blur effect
        
        # Dark overlay taaki text chamke
        overlay = Image.new('RGB', (width, height), (0, 0, 0))
        bg = Image.blend(bg, overlay, 0.7)
        os.remove(photo_path)
    else:
        # Default Premium Dark Gradient (Agar koi photo nahi di)
        bg = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(bg)
        for y in range(height):
            r = int(15 + (30 - 15) * (y / height))
            g = int(15 + (10 - 15) * (y / height))
            b = int(25 + (60 - 25) * (y / height))
            draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw = ImageDraw.Draw(bg)
    
    # Glass Panel (Card)
    panel_w, panel_h = 1000, 400
    panel_x, panel_y = (width - panel_w) // 2, (height - panel_h) // 2
    draw.rounded_rectangle(
        [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)], 
        radius=30, fill=(255, 255, 255, 15), outline=(255, 255, 255, 40), width=3
    )
    
    # Fonts
    font_big = get_font(85, bold=True)
    font_small = get_font(40, bold=False)

    # Text to display
    bot_name = settings.BOT_NAME.upper()
    text2 = "Premium Telegram Music Bot"

    # Center align function
    def draw_center_text(y, text, font, color):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(((width - text_w) / 2, y), text, font=font, fill=color)

    # Draw Text
    draw_center_text(panel_y + 80, bot_name, font_big, (0, 255, 255)) # Cyan Neon color
    draw_center_text(panel_y + 200, text2, font_small, (200, 200, 200)) # Light grey
    
    # Save image
    save_dir = "assets/images"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "start.jpg")
    
    bg.save(save_path, quality=95)

    await m.delete()
    await message.reply_photo(
        photo=save_path,
        caption=(
            "✅ **Premium Start Image Generated!**\n\n"
            "Yeh image aapke folder mein save ho gayi hai.\n\n"
            "Ab apni `.env` file mein ye set karein:\n"
            f"`START_IMG_URL={save_path}`\n\n"
            "Bot restart karte hi `/start` par ye premium image dikhne lagegi!"
        )
    )
