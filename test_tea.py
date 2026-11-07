import os
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch

os.environ['TELEGRAM_BOT_TOKEN'] = '123456:test'
os.environ['AI_PROVIDER'] = 'groq'
os.environ.pop('GROQ_API_KEY', None)
import bot


class Tea(unittest.IsolatedAsyncioTestCase):
    async def test_tea_pipeline_retains_speakers_and_corrections_in_all_stages(self):
        rows = [(i, 'Mira' if i % 2 else 'Dev', ('Dinner cancelled? ' if i % 2 else 'Correction: dinner is still on. ') + 'extra chat ' * 12) for i in range(80)]
        calls = []
        async def ai(system, content, **kwargs):
            calls.append((system, content))
            return 'Mira misread Dev; he clarified dinner is still on.'
        with patch.object(bot, 'ai', ai):
            result = await bot.summarize(rows, mode='tea', language='English')
        self.assertGreater(len(calls), 2)
        for system, _ in calls:
            self.assertIn('correction', system.lower())
            self.assertIn('who', system.lower())
        self.assertIn('Give the group tea', calls[-1][0])
        self.assertIn('nothing juicy happened', calls[-1][0])
        self.assertIn('Do not infer cheating', calls[-1][0])
        self.assertIn('Write the final answer in English', calls[-1][0])
        self.assertEqual(result, 'Mira misread Dev; he clarified dinner is still on.')

    async def test_tea_defaults_and_explicit_count_use_durable_job(self):
        for args, expected_count, language in [([], 100, None), (['50', 'English'], 50, 'English')]:
            message = NS(message_id=10, reply_text=AsyncMock(return_value=NS(message_id=11)))
            update = NS(effective_message=message, effective_chat=NS(id=-1))
            context = NS(args=args, bot=object())
            with patch.object(bot, 'client', object()), patch.object(bot, 'get_messages', return_value=[(1, 'Mira', 'hello')]) as get, patch.object(bot, 'load_summary_job', return_value=None), patch.object(bot, 'save_summary_job') as save, patch.object(bot, 'launch_summary_job') as launch:
                await bot._run_summary(update, context, mode='tea')
            get.assert_called_once_with(-1, expected_count, None)
            job = save.call_args.args[1]
            self.assertEqual(job['mode'], 'tea')
            self.assertEqual(job['language'], language)
            self.assertEqual(job['options']['count'], expected_count)
            self.assertEqual(launch.call_args.args[2], job)
            message.reply_text.assert_awaited_once_with('Reading the tea…')

    async def test_tea_handler_keeps_summary_permission_check(self):
        with patch.object(bot, 'allowed', AsyncMock(return_value=False)) as allowed, patch.object(bot, '_run_summary', AsyncMock()) as run:
            await bot.tea(NS(), NS())
        allowed.assert_awaited_once()
        run.assert_not_awaited()


if __name__ == '__main__':
    unittest.main()
