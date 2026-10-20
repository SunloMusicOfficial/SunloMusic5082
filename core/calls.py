import asyncio
from pytgcalls import PyTgCalls
from utils.logger import get_logger

logger = get_logger("CallsEngine")
calls = None

def create_calls(userbot_client):
    global calls
    calls = PyTgCalls(userbot_client)
    return calls
