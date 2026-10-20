import random, aiohttp
from ftmgram import filters
from core.bot import app
from utils.decorators import register_user

@app.on_message(filters.command("dice"))
async def dice(client, message): await message.reply_dice(emoji="🎲")
@app.on_message(filters.command("dart"))
async def dart(client, message): await message.reply_dice(emoji="🎯")
@app.on_message(filters.command("slot"))
async def slot(client, message): await message.reply_dice(emoji="🎰")

@app.on_message(filters.command("8ball"))
async def eightball(client, message):
    if len(message.command) < 2: return await message.reply_text("🎱 Ask a question!")
    answers = ["Yes.", "No.", "Maybe.", "Definitely!", "Never.", "I don't know."]
    await message.reply_text(f"🎱 {random.choice(answers)}")

@app.on_message(filters.command("truth"))
async def truth(client, message):
    truths = ["What is your biggest fear?", "Who was your first crush?", "Have you ever lied to your best friend?"]
    await message.reply_text(f"🟢 **TRUTH:** {random.choice(truths)}")

@app.on_message(filters.command("dare"))
async def dare(client, message):
    dares = ["Send a selfie.", "Text your crush 'Hi'.", "Do 10 pushups.", "Sing a song in voice note."]
    await message.reply_text(f"🔴 **DARE:** {random.choice(dares)}")

@app.on_message(filters.command("joke"))
async def joke(client, message):
    jokes = ["Why did the music teacher need a ladder? To reach the high notes!", "What do you call a fake noodle? An impasta!"]
    await message.reply_text(f"😂 {random.choice(jokes)}")

@app.on_message(filters.command("meme"))
async def meme(client, message):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            if resp.status == 200:
                data = await resp.json()
                await message.reply_photo(data['url'], caption=f"😂 **{data['title']}**")
