# Railway deployment: Amethyst Cute

1. Revoke any Telegram bot token previously exposed; put the replacement in Railway Variables, never Git.
2. Create a Telegram API ID and API hash at https://my.telegram.org. Install dependencies locally with `python -m pip install -r requirements.txt`.
3. Locally, create `.env` from `.env.example` and set `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`. Run `python create_session.py`. Authenticate with your own Telegram account and 2FA if enabled. Keep the printed `TELEGRAM_STRING_SESSION` secret; do not commit it.
4. Create a private GitHub repository and upload the project source, excluding `.env` and session/database files.
5. In https://railway.com/new create a project from that GitHub repository. Set the service name `amethyst-cute`.
6. Attach a Railway volume to the **same service** at `/data`. Keep one replica only. Set `DATABASE_PATH=/data/messages.sqlite3`.
7. Add service variables: `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY`, `OPENAI_MODEL=gpt-4.1-mini`, `GROUP_TIMEZONE=Asia/Kolkata`, `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`, `TELEGRAM_STRING_SESSION`, `TELEGRAM_GROUP` (group @username or numeric peer ID). Never put secrets in code or Git.
8. Deploy. `railway.json` starts `python railway_worker.py`: it imports up to 1,000 recent messages at startup and starts the Bot API polling loop. New text messages are stored by `bot.py`.
9. Add the bot to your group. In BotFather, disable Group Privacy, then remove/re-add the bot if needed. Run `/summary` in the group.

## Caveats
- Telegram account must already be a member of the group and have access to its history. For private groups, use a numeric peer ID the account can resolve; a private invitation link may not resolve directly.
- Text and media captions are imported; image/video/audio content is not transcribed.
- This project keeps at most 1,000 stored text messages per group. Bot API updates may be missed during prolonged downtime; history is refreshed when the service restarts.
- A Telethon StringSession grants account access: protect it like a password. If exposed, revoke the Telegram session in Telegram Settings > Devices.
- The bot's commands work only after a successful deployment. OpenAI API usage and Railway resources may incur charges.
- The SQLite volume is local to one service. Do not run multiple bot replicas or two concurrent polling instances.
