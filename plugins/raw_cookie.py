import json
import re
import os
from ftmgram import filters, enums
from core.bot import app
from config.settings import settings
from database.cookies import add_cookie

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
    # Check if replied to a text or document
    reply = message.reply_to_message
    
    if not reply or (not reply.text and not reply.document):
        return await message.reply_text(
            "🍪 **Usage:**\n"
            "1. Ek `.json` ya `.txt` file bhejo jisme cookies ho.\n"
            "2. Us file par reply karke `/setjsoncookie <name>` likho.\n"
            "Example: `/setjsoncookie account1`"
        )

    name = message.command[1].lower() if len(message.command) > 1 else "acc1"
    m = await message.reply_text(f"⏳ **Processing cookies for `{name}`...**")

    try:
        raw_text = ""
        # If it's a document (file)
        if reply.document:
            file_path = await client.download_media(reply.document)
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            os.remove(file_path)
        # If it's text
        else:
            raw_text = reply.text

        # Clean JSON if extra characters exist
        raw_text = raw_text.strip()
        if not raw_text.startswith("{") and not raw_text.startswith("["):
            match = re.search(r'(\{.*\}|\[.*\])', raw_text, re.DOTALL)
            if match:
                raw_text = match.group(0)

        data = json.loads(raw_text)
        netscape_data = json_to_netscape(data)
        await add_cookie(name, netscape_data)
        
        await m.edit_text(f"✅ **Cookies for `{name}` saved successfully!**\nAb aap `/play` chala kar test kar sakte ho.")
    except json.JSONDecodeError:
        await m.edit_text("❌ **Invalid JSON format!** File ke andar valid JSON hona chahiye.")
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")
