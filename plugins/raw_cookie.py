import json
import re
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from database.cookies import add_cookie
from utils.logger import get_logger

logger = get_logger("RawCookie")

def json_to_netscape(json_data):
    lines = ["# Netscape HTTP Cookie File"]
    cookies_list = json_data.get("cookies", []) if isinstance(json_data, dict) else json_data
    
    for cookie in cookies_list:
        domain = cookie.get("domain", ".youtube.com")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path = cookie.get("path", "/")
        secure = "TRUE" if cookie.get("secure") else "FALSE"
        expiration = int(cookie.get("expirationDate", 0)) if cookie.get("expirationDate") else 0
        name = cookie.get("name", "")
        value = cookie.get("value", "")
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}")
    return "\n".join(lines)

@app.on_message(filters.command("setjsoncookie") & filters.user(settings.OWNER_ID))
async def set_json_cookie(client, message):
    # Reply se data uthao ya direct command se
    if message.reply_to_message and message.reply_to_message.text:
        raw_text = message.reply_to_message.text
    elif len(message.command) > 2:
        raw_text = message.text.split(None, 2)[2]
    else:
        return await message.reply_text(
            "🍪 **Usage:** Kisi JSON message par reply karke `/setjsoncookie <name>` likhein.\n"
            "Ya direct: `/setjsoncookie <name> {json_here}`"
        )

    # Account name nikaalo
    name = message.command[1].lower() if len(message.command) > 1 else "acc1"
    
    m = await message.reply_text(f"⏳ **Parsing JSON & saving cookies for `{name}`...**")

    try:
        # JSON fix karo (kabhi kabhi mobile copy mein extra characters aate hain)
        raw_text = raw_text.strip()
        if not raw_text.startswith("{"):
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)

        data = json.loads(raw_text)
        netscape_data = json_to_netscape(data)
        await add_cookie(name, netscape_data)
        
        await m.edit_text(f"✅ **Cookies for `{name}` saved successfully!**\n\nAb aap `/play` chala kar test kar sakte ho.")
    except json.JSONDecodeError:
        await m.edit_text("❌ **Invalid JSON format!** Make sure you copied the full JSON string.")
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")
