# Multilingual Telegram Group Summarizer — history + live updates

## Groq free-tier setup

Create a Groq account at https://console.groq.com and an API key. Stay on the Free plan. Set `AI_PROVIDER=groq`, `GROQ_API_KEY`, and `GROQ_MODEL=openai/gpt-oss-20b` in Railway Variables or your local `.env`. No OpenAI key is needed in Groq mode, and there is no automatic fallback to a paid provider.

The bot splits text into bounded UTF-8 batches and compresses intermediate notes. Translations have separate request slots from summaries, a smaller output budget for short text, and a 10-minute cache for repeated requests in the same group. There is no fixed delay between translations; backoff follows actual provider rate-limit responses. Large summaries can still take several minutes. Start with `/summary 50`. Account limits and daily limits apply. New messages continue to be collected during summaries. Hosting costs are separate from the free AI API.

To use OpenAI instead, set `AI_PROVIDER=openai`, `OPENAI_API_KEY`, and `OPENAI_MODEL`.

## Reply translations

Anyone can reply to a text message or media caption with `translate` or `/translate` for English. Use `translate to Hindi` or `/translate Hindi` for another language, including `Roman Hindi`. Translation understands casual Romanized Hindi, Hinglish, slang, spelling variations and mixed-language messages. Ambiguous wording can still require context.

Summaries use short natural paragraphs or compact bullets, without titles, emoji headers, provider details or plan notices. They preserve the important names, dates, decisions and unresolved points.

Summarize the latest 1,000 stored text/caption messages in a Telegram group, across languages and mixed-language conversations. The importer uses an authorized Telegram **user** session to access history; the Telegram **bot** continues collecting future messages. Both write to the same SQLite database, deduplicated by group/message ID.

## 1. Create and configure the bot

1. Open [@BotFather](https://t.me/BotFather), run `/newbot`, and save the token.
2. In BotFather, run `/setprivacy` and **Disable** privacy mode for the bot. Remove and re-add the bot if necessary for the change to take effect. Alternatively, grant the bot admin rights with only the permissions it needs.
3. Add the bot to your group. Notify members that chat messages are stored and sent to an AI provider when summaries are requested.
4. Get an OpenAI API key from https://platform.openai.com/api-keys (API usage is billed separately).

## 2. Install

Requires Python 3.10+.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
```

Edit `.env` with `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, and `TELEGRAM_API_ID` / `TELEGRAM_API_HASH`. Obtain the latter two from https://my.telegram.org under **API development tools**. Do not share your API hash, verification codes, session files, or tokens.

## 3. Import the last 1,000 existing messages

Sign in with a Telegram account that is already authorized to view the group history:

```bash
python import_history.py --chat @your_public_group --limit 1000
```

For private groups, use a group ID or accessible `t.me` link. If entity resolution fails, use an accessible group username or inspect your account's dialogs; your account must be a member with permission to see history. On first run Telethon prompts for your phone number, a Telegram login code, and optionally your two-step verification password. These are entered **locally**, never sent to the bot or the AI provider.

The importer scans the latest 1,000 Telegram messages and stores text/captions (non-text-only media is skipped). It imports fewer than 1,000 text messages if the last 1,000 contain media without captions. The importer retains only the latest 1,000 stored text/caption messages per group. Re-running is safe: duplicate message IDs are updated rather than duplicated.

**Important:** A user session can access only history that Telegram exposes to that account. The Telegram Bot API alone cannot fetch historical group messages.

## 4. Keep collecting new messages

```bash
python bot.py
```

Keep the bot process running on your computer or an always-on server. The bot must have privacy mode disabled (or be a suitable group admin) to receive normal group messages. The importer does **not** need to run continuously. If the bot was offline and missed messages, run the importer again to backfill the latest 1,000. Run the importer and bot from the same directory and with the same `DATABASE_PATH` (or use an absolute database path). Do not run multiple polling instances of the same bot token.

## Commands (group admins only)

- `/summary` — latest 1,000 stored messages
- `/summary 100` — latest 100
- `/summary hindi` — summary in Hindi (other language names also supported)
- `/today` — today's messages using `GROUP_TIMEZONE`
- `/decisions` — confirmed decisions
- `/actions` — tasks, owners, and deadlines when explicitly stated
- `/help` — help

## Security, privacy, and limitations

- Keep `.env`, `*.session`, `*.session-journal`, and `*.sqlite3*` private; they contain credentials, account access, or group content. Never commit them to Git. See `.gitignore`.
- Telegram messages are untrusted input; the AI is instructed to ignore any commands embedded in the chat. AI summaries can still contain errors or omit context.
- Only text and media captions are summarized, not voice notes, photo contents, or attachments without captions. Commands are excluded.
- Deleted Telegram messages are not automatically deleted from the local database. To erase stored data, stop the bot and delete the SQLite database and its WAL/SHM files. The latest 1,000 stored messages per group are retained.
- Summaries send stored chat text to the configured AI API. Respect group consent, Telegram terms, and applicable privacy requirements.
- OpenAI API calls incur usage costs. No cloud hosting or production deployment is included.
