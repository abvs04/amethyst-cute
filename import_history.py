"""Import the most recent Telegram group history using an authorized user session."""
import argparse
import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.utils import get_peer_id

from bot import connection, save_message

load_dotenv()


def arguments():
    parser = argparse.ArgumentParser(description='Import existing group messages into the bot database')
    parser.add_argument('--chat', required=True, help='Group @username, t.me link, or numeric chat ID accessible to your account')
    parser.add_argument('--limit', type=int, default=1000, help='Number of recent Telegram messages to scan (1–1000)')
    return parser.parse_args()


async def main():
    args = arguments()
    if not 1 <= args.limit <= 1000:
        raise SystemExit('--limit must be between 1 and 1000')
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    if not api_id or not api_hash:
        raise SystemExit('Set TELEGRAM_API_ID and TELEGRAM_API_HASH in .env (from https://my.telegram.org)')
    session = os.getenv('TELEGRAM_SESSION_PATH', 'telegram_user')
    Path(session).parent.mkdir(parents=True, exist_ok=True)
    with connection():
        pass
    async with TelegramClient(session, int(api_id), api_hash) as client:
        entity = await client.get_entity(int(args.chat) if args.chat.lstrip('-').isdigit() else args.chat)
        if not getattr(entity, 'megagroup', False) and entity.__class__.__name__ != 'Chat':
            raise SystemExit('The selected chat is not a Telegram group or supergroup.')
        chat_id = get_peer_id(entity)
        imported = 0
        scanned = 0
        async for message in client.iter_messages(entity, limit=args.limit, reverse=False):
            scanned += 1
            content = message.message or ''
            if not content.strip() or content.startswith('/'):
                continue
            author = 'Unknown'
            try:
                sender = await message.get_sender()
                if sender:
                    author = ' '.join(filter(None, [getattr(sender, 'first_name', None), getattr(sender, 'last_name', None)])) or getattr(sender, 'title', None) or 'Unknown'
            except Exception:
                pass
            save_message(chat_id, message.id, int(message.date.timestamp()), author[:100], content[:8000])
            imported += 1
        print(f'Scanned {scanned} most recent Telegram messages; imported {imported} text/caption messages.')
        print(f'Group: {getattr(entity, "title", args.chat)} | Bot chat ID: {chat_id}')
        print('Start bot.py and run /summary in this group. New messages are collected by the bot.')


if __name__ == '__main__':
    asyncio.run(main())
