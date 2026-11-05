"""Run locally only. Never share the generated Telegram session string."""
import os
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
load_dotenv()
with TelegramClient(StringSession(), int(os.environ['TELEGRAM_API_ID']), os.environ['TELEGRAM_API_HASH']) as client:
    print('\nTELEGRAM_STRING_SESSION (keep secret):\n' + client.session.save())
