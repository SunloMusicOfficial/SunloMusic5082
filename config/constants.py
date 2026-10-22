from config.settings import settings

class Constants:
    VERSION = "1.0.0"
    
    # Default image agar env mein nahi hai
    START_IMG = settings.START_IMG_URL if settings.START_IMG_URL else "https://files.catbox.moe/sunlo_start.jpg"
    
    START_TEXT = (
        "👋 <b>Welcome to Sunlo Music!</b>\n\n"
        "I am the fastest and most advanced music bot.\n\n"
        "✨ <b>Why choose me?</b>\n"
        "▸ Lightning fast 1-3s playback\n"
        "▸ High-quality audio streaming\n"
        "▸ Ad-free, premium experience\n\n"
        "Add me to your group and use /play to start!"
    )
    
    HELP_TEXT = (
        "📚 <b>Sunlo Music Commands</b>\n\n"
        "🎵 <b>Playback:</b>\n"
        "▸ /play <song> - Play a song\n"
        "▸ /pause - Pause the stream\n"
        "▸ /resume - Resume the stream\n"
        "▸ /skip - Skip to next track\n"
        "▸ /stop - Stop and leave VC\n\n"
        "🛠 <b>Other:</b>\n"
        "▸ /song <name> - Download audio\n"
        "▸ /stats - Bot statistics"
    )

constants = Constants()
