import os
import tempfile
import unittest
from unittest.mock import patch

os.environ['TELEGRAM_BOT_TOKEN'] = '123456:test'
os.environ['AI_PROVIDER'] = 'groq'
os.environ.pop('GROQ_API_KEY', None)
import bot


class RecapOrder(unittest.IsolatedAsyncioTestCase):
    def test_selection_is_oldest_to_newest_and_frozen_at_command(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(bot, 'DB', directory + '/messages.sqlite3'):
            # Insert out of order, including conflicting timestamps and another group.
            for mid, timestamp in [(5, 500), (2, 800), (7, 700), (1, 100), (4, 900), (3, 300), (8, 1000)]:
                bot.save_message(-1, mid, timestamp, 'A', f'm{mid}')
            bot.save_message(-2, 3, 300, 'B', 'other group')
            self.assertEqual([r[2] for r in bot.get_messages(-1, 3, before_id=6)], ['m3', 'm4', 'm5'])
            bot.save_message(-1, 9, 1100, 'A', 'arrived after command')
            self.assertEqual([r[2] for r in bot.get_messages(-1, 3, before_id=6)], ['m3', 'm4', 'm5'])
            self.assertEqual([r[2] for r in bot.get_messages(-1, 10, since=500, before_id=6)], ['m2', 'm4', 'm5'])

    async def test_summary_and_tea_prompts_preserve_event_order(self):
        for mode in ('summary', 'tea'):
            calls = []
            async def ai(system, content, **kwargs):
                calls.append((system, content))
                return 'first topic followed by later topic'
            rows = [(i, 'A', f'event{i:03d} ' + 'detail ' * 30) for i in range(50)]
            with patch.object(bot, 'ai', ai):
                await bot.summarize(rows, mode=mode)
            for system, _ in calls:
                self.assertIn('oldest to newest', system)
            supplied = '\n'.join(content for _, content in calls[:-1])
            self.assertLess(supplied.index('event000'), supplied.index('event049'))
            final = calls[-1][0]
            self.assertNotIn('Lead with the main update', final)
            self.assertNotIn('Lead with the most interesting', final)
            self.assertIn('No forced humour', final)
            if mode == 'tea':
                self.assertNotIn('Be witty', final)
                self.assertNotIn('sharp, playful', final)


if __name__ == '__main__':
    unittest.main()
