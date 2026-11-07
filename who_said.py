"""Native Telegram quiz built only from the requesting group's saved messages."""
import random
import re
import time


def select_round(rows, recent):
    authors = sorted({name for mid, ts, name, body in rows if name and name != 'Unknown' and len(name) <= 80})
    if len(authors) < 3:
        return None
    owners = {}
    for mid, ts, name, body in rows:
        owners.setdefault(body.strip().casefold(), set()).add(name)
    choices = [(mid, name, body) for mid, ts, name, body in rows
               if name in authors and ts <= time.time() - 600 and 20 <= len(body) <= 220
               and len(body.split()) >= 4 and not body.startswith('/')
               and not re.search(r'https?://|www\.|@|\d{7,}', body)
               and len(owners[body.strip().casefold()]) == 1]
    fresh = [row for row in choices if row[0] not in recent]
    if not fresh:
        return None
    mid, author, quote = random.choice(fresh)
    options = random.sample([name for name in authors if name != author], min(3, len(authors) - 1)) + [author]
    random.shuffle(options)
    return mid, quote, options, options.index(author)


async def start_game(update, context, connection):
    chat, message = update.effective_chat, update.effective_message
    if not chat or chat.type not in ('group', 'supergroup'):
        await message.reply_text('Use /whosaidthis in your group.')
        return
    now = time.time()
    with connection() as con:
        con.execute('CREATE TABLE IF NOT EXISTS quote_rounds (chat_id INTEGER PRIMARY KEY, started REAL NOT NULL, recent TEXT NOT NULL)')
        con.execute('BEGIN IMMEDIATE')
        previous = con.execute('SELECT started,recent FROM quote_rounds WHERE chat_id=?', (chat.id,)).fetchone()
        if previous and now - previous[0] < 60:
            status, selection = 'busy', None
        else:
            recent = [int(v) for v in previous[1].split(',') if v] if previous else []
            rows = con.execute('SELECT message_id,timestamp,author,content FROM messages WHERE chat_id=? AND message_id<? ORDER BY message_id DESC LIMIT 1000', (chat.id, message.message_id)).fetchall()
            selection = select_round(rows, recent)
            status = 'ready' if selection else 'empty'
            if selection:
                mid = selection[0]
                con.execute('INSERT OR REPLACE INTO quote_rounds VALUES (?,?,?)', (chat.id, now, ','.join(map(str, (recent + [mid])[-20:]))))
    if status == 'busy':
        await message.reply_text('A round just started. Try again in a minute.')
        return
    if status == 'empty':
        await message.reply_text('I need more older messages from at least three different names to make a fresh round. Try again after the chat has been active for a while.')
        return
    mid, quote, options, answer = selection
    try:
        await context.bot.send_poll(
            chat_id=chat.id, question='Who said this?\n\n“' + quote + '”', options=options,
            type='quiz', correct_option_id=answer, is_anonymous=False,
            open_period=45, explanation=f'{options[answer]} said this.',
            message_thread_id=getattr(message, 'message_thread_id', None))
    except Exception:
        # Restore the previous cooldown/history so a failed send can be retried.
        with connection() as con:
            if previous:
                con.execute('UPDATE quote_rounds SET started=?,recent=? WHERE chat_id=? AND started=?', (*previous, chat.id, now))
            else:
                con.execute('DELETE FROM quote_rounds WHERE chat_id=? AND started=?', (chat.id, now))
        raise
