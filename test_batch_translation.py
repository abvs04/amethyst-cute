import asyncio
import json
import os
import tempfile
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch

os.environ['TELEGRAM_BOT_TOKEN'] = '123456:test'
os.environ['AI_PROVIDER'] = 'groq'
os.environ.pop('GROQ_API_KEY', None)
import bot


class BatchTranslations(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_db = bot.DB
        bot.DB = self.directory.name + '/messages.sqlite3'
        for i in range(1, 11):
            bot.save_message(-1, i, i, f'Person {i}', f'message {i}')
            bot.save_message(-2, i, i, 'Other group', 'private')

    async def asyncTearDown(self):
        bot.DB = self.old_db
        self.directory.cleanup()

    def test_command_parser_and_single_reply_unchanged(self):
        for command in ['/translate 5', '/translate@AmethystTranslator_bot 5', '/ Translate 5', 'translate 5']:
            self.assertEqual(bot.batch_translation_request(NS(text=command)), (5, 'English'))
        self.assertEqual(bot.batch_translation_request(NS(text='/translate 5 to Hindi')), (5, 'Hindi'))
        self.assertIsNone(bot.batch_translation_request(NS(text='/translate yeh kya scene hai')))
        m = NS(text='/translate Hindi', reply_to_message=NS(text='hello', message_id=3))
        self.assertEqual(bot.translation_request(m, -1)[:2], ('hello', 'Hindi'))

    def test_latest_and_reply_anchors_do_not_cross_groups(self):
        m = NS(text='/translate 5', message_id=10)
        rows = bot.batch_translation_rows(m, -1, 5)
        self.assertEqual([row[0] for row in rows], [5, 6, 7, 8, 9])
        m.reply_to_message = NS(message_id=6, text='full original', from_user=NS(full_name='Person 6'))
        m.quote = NS(text='selected fragment')
        rows = bot.batch_translation_rows(m, -1, 5)
        self.assertEqual([row[0] for row in rows], [2, 3, 4, 5, 6])
        self.assertEqual(rows[-1][2], 'full original')
        self.assertNotIn('private', str(rows))
        self.assertEqual(len(bot.batch_translation_rows(NS(message_id=3), -1, 5)), 2)

    async def test_normal_batch_one_call_all_messages_output(self):
        rows = bot.batch_translation_rows(NS(message_id=7), -1, 5)
        raw = json.dumps([{'id': str(mid), 'text': f'translated {mid}'} for mid, _, _ in rows])
        with patch.object(bot, 'cached_translation', AsyncMock(return_value=raw)) as api:
            out = await bot.translate_message_batch(-1, rows, 'English')
        self.assertEqual(out, [f'translated {i}' for i in range(2, 7)])
        self.assertEqual(api.await_count, 1)

    async def test_incomplete_response_falls_back_without_losing_messages(self):
        rows = [(1, 'A', 'hello'), (2, 'B', 'bye')]
        with patch.object(bot, 'cached_translation', AsyncMock(side_effect=['[]', 'Hello', 'Goodbye'])) as api:
            self.assertEqual(await bot.translate_message_batch(-1, rows, 'English'), ['Hello', 'Goodbye'])
        self.assertEqual(api.await_count, 3)

    async def test_handler_limits_and_missing_history(self):
        chat = NS(id=-1, type='supergroup')
        m = NS(message_id=2, reply_text=AsyncMock())
        with patch.object(bot, 'client', object()), patch.object(bot, 'translate_message_batch', AsyncMock(return_value=['translated'])):
            await bot.translate_recent(m, chat, 5, 'English')
        self.assertIn('Found 1 of the 5', m.reply_text.call_args.args[0])
        m.reply_text.reset_mock()
        await bot.translate_recent(m, chat, 21, 'English')
        self.assertIn('1–20', m.reply_text.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
