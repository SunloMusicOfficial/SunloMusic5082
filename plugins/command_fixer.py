from ftmgram import filters
from core.bot import app
from config.settings import settings

@app.on_message(filters.group & filters.text, group=-1) # Group -1 means it runs before other plugins
async def command_fixer(client, message):
    """
    Yeh function /command@BotName ko /command mein convert karta hai
    taaki baaki saare plugins usko samajh sakein.
    """
    if not message.text or not message.text.startswith("/"):
        return
        
    bot_username = settings.BOT_USERNAME.replace("@", "")
    
    # Agar message mein @SunloMusicBot hai
    if f"@{bot_username}" in message.text:
        # Command ko split karo (jaise /play@SunloMusicBot song -> ['/play', 'song'])
        parts = message.text.split()
        if len(parts) > 0:
            # Pehle word se @BotName hatao
            first_word = parts[0].replace(f"@{bot_username}", "")
            
            # Agar pehla word ab bhi / se start ho raha hai (matlab valid command tha)
            if first_word.startswith("/"):
                # Naya text banao jisme @BotName na ho
                parts[0] = first_word
                new_text = " ".join(parts)
                
                # Message object ko modify karo
                message.text = new_text
                message.command = parts
                
                # Ab isko aage badhne do taaki baaki plugins isko handle kar sakein
                return
