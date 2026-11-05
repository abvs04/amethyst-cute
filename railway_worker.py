"""Import history at startup, then run the Telegram Bot API polling worker."""
import asyncio
import os
import logging
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.utils import get_peer_id


def import_history():
    from bot import connection, save_message
    target = os.getenv('TELEGRAM_GROUP', '').strip()
    session = os.getenv('TELEGRAM_STRING_SESSION', '').strip()
    if not target or not session:
        logging.warning('Skipping history import: TELEGRAM_GROUP or TELEGRAM_STRING_SESSION not set')
        return

    async def run():
        api_id = int(os.environ['TELEGRAM_API_ID'])
        api_hash = os.environ['TELEGRAM_API_HASH']
        client = TelegramClient(StringSession(session), api_id, api_hash)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                raise ValueError('Telegram session is not authorized; generate a new session locally')
            entity = await client.get_entity(int(target) if target.lstrip('-').isdigit() else target)
            if not getattr(entity, 'megagroup', False) and entity.__class__.__name__ != 'Chat':
                raise ValueError('TELEGRAM_GROUP must refer to a group or supergroup')
            chat_id = get_peer_id(entity)
            count = 0
            async for message in client.iter_messages(entity, limit=1000):
                body = message.message or ''
                if not body.strip() or body.startswith('/'):
                    continue
                sender = await message.get_sender()
                author = (' '.join(filter(None, [getattr(sender, 'first_name', None), getattr(sender, 'last_name', None)])) or getattr(sender, 'title', None) or 'Unknown') if sender else 'Unknown'
                save_message(chat_id, message.id, int(message.date.timestamp()), author[:100], body[:8000])
                count += 1
            logging.info('Imported %s messages into group %s', count, chat_id)
        finally:
            await client.disconnect()

    with connection():
        pass
    asyncio.run(run())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        import_history()
    except Exception:
        logging.exception('History import failed; starting bot anyway')
    from bot import main
    # History import uses asyncio.run(), which closes its event loop.
    # Polling needs its own current loop on Python 3.12 and later.
    asyncio.set_event_loop(asyncio.new_event_loop())
    main()
