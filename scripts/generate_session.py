import asyncio
import sys
from ftmgram import Client
from config.settings import settings

print("""
╔══════════════════════════════════════════════╗
║       🎵 SUNLO MUSIC - SESSION GENERATOR     ║
╚══════════════════════════════════════════════╝
Yeh session string aapke Assistant Account (Userbot) ke liye hai.
Jo account Voice Chat join karega.

⚠️  IMPORTANT: 
- Apna Phone Number country code ke saath daalein (e.g., +919876543210)
- Telegram par aane wala OTP daalein
- 2-Step Verification on hai toh password daalein
""")

async def main():
    try:
        # Validate API details before starting
        if not settings.API_ID or not settings.API_HASH:
            print("❌ Error: API_ID ya API_HASH .env file mein nahi mila!")
            print("Pehle .env file mein apni details daalein.")
            return

        # Create Client in memory
        async with Client(
            name=":memory:",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
            in_memory=True
        ) as app:
            # Export the session string
            session_string = await app.export_session_string()
            
            print("\n" + "="*50)
            print("✅ SESSION STRING GENERATED SUCCESSFULLY!")
            print("="*50)
            print("\nNeeche diya gaya lamba code copy karein aur apni .env file mein SESSION_STRING= ke aage paste karein:\n")
            
            # Print in green color for visibility
            print(f"\033[92m{session_string}\033[0m\n")
            
            print("="*50)
            print("⚠️  WARNING: Yeh string aapke account ka access hai. Kisi ko na dein!")
            print("="*50)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure your internet is working and API details are correct.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(0)
