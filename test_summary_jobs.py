import asyncio
import os
import re
import tempfile
import unittest
from collections import Counter
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch

os.environ['TELEGRAM_BOT_TOKEN'] = '123456:test'
os.environ['AI_PROVIDER'] = 'groq'
os.environ.pop('GROQ_API_KEY', None)

import httpx
import bot
from openai import RateLimitError


class SummaryJobs(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.old_db = bot.DB
        bot.DB = self.directory.name + '/messages.sqlite3'
        bot.summary_next_request = 0
        bot.summary_slots = asyncio.Semaphore(1)
        bot.translation_slots = asyncio.Semaphore(2)
        bot.active_summaries.clear()
        bot.summary_tasks.clear()

    async def asyncTearDown(self):
        await bot.stop_summary_jobs(None)
        bot.DB = self.old_db
        self.directory.cleanup()

    async def test_1000_messages_checkpoint_through_rate_limit_and_restart(self):
        calls = Counter()
        covered = set()
        state = {'successes': 0, 'limited': True}
        response = httpx.Response(429, headers={'retry-after': '0.1'}, request=httpx.Request('POST', 'https://api.groq.com/openai/v1/chat/completions'))
        error = RateLimitError('tokens per minute', response=response, body={'code': 'rate_limit_exceeded'})

        async def create(**kwargs):
            payload = kwargs['messages'][1]['content']
            if state['limited'] and state['successes'] >= 3:
                raise error
            calls[payload] += 1
            markers = re.findall(r'm\d{4}', payload)
            if payload.startswith('Chunk '):
                covered.update(markers)
            state['successes'] += 1
            text = f'{markers[0]} through {markers[-1]}' if markers else 'Brief notes'
            return NS(choices=[NS(message=NS(content=text))], usage=NS(total_tokens=50))

        bot.client = NS(chat=NS(completions=NS(create=create)))
        rows = [(1700000000 + i, 'A', f'message m{i:04d} agreed') for i in range(1000)]
        job = {'id': 'resume-test', 'rows': rows, 'mode': 'summary', 'language': 'English',
               'count': 1000, 'options': {}, 'command_id': 9, 'progress_id': 10,
               'status': 'running', 'next_retry': 0}
        bot.save_summary_job(-1, job)
        telegram = NS(edit_message_text=AsyncMock(), send_message=AsyncMock())
        original_sleep = asyncio.sleep

        async def sleep(_delay):
            if bot.load_summary_job(-1)['status'] == 'waiting':
                raise asyncio.CancelledError()
            await original_sleep(0)

        with patch.object(bot.asyncio, 'sleep', sleep):
            with self.assertRaises(asyncio.CancelledError):
                await bot.execute_summary_job(telegram, -1, job)
        saved = bot.load_summary_job(-1)
        self.assertEqual(saved['status'], 'waiting')
        self.assertEqual(len(saved['rows']), 1000)
        with bot.connection() as con:
            self.assertEqual(con.execute('SELECT COUNT(*) FROM summary_steps').fetchone()[0], 3)
        completed_payloads = set(calls)
        state['limited'] = False
        saved['next_retry'] = 0
        bot.save_summary_job(-1, saved)
        with patch.object(bot.asyncio, 'sleep', AsyncMock()):
            await bot.resume_summary_jobs(NS(bot=telegram))
            await asyncio.gather(*list(bot.summary_tasks.values()))
        final = bot.load_summary_job(-1)
        self.assertEqual(final['status'], 'done')
        self.assertEqual(final['count'], 1000)
        self.assertEqual(covered, {f'm{i:04d}' for i in range(1000)})
        self.assertTrue(all(calls[payload] == 1 for payload in completed_payloads))
        self.assertIn('m0000', final['result'])
        self.assertIn('m0999', final['result'])
        self.assertEqual(final['rows'], [])

    async def test_translation_is_not_blocked_by_summary_wait(self):
        entered, release = asyncio.Event(), asyncio.Event()

        async def create(**kwargs):
            if kwargs['messages'][0]['content'] == 'SUMMARY':
                entered.set()
                await release.wait()
            return NS(choices=[NS(message=NS(content='Translated'))], usage=NS(total_tokens=10))

        bot.client = NS(chat=NS(completions=NS(create=create)))
        task = asyncio.create_task(bot.ai('SUMMARY', 'long'))
        await entered.wait()
        self.assertEqual(await asyncio.wait_for(bot.ai('TRANSLATE', 'short', translation=True, max_output_tokens=1024), 0.5), 'Translated')
        self.assertFalse(task.done())
        release.set()
        await task

    def test_slang_boundaries_and_context_hints(self):
        for text in ('abe dalle idhar aa', 'dalley mat ban', 'ye banda bhadwa hai', 'aand mat kha', 'nalle ka lafda'):
            self.assertIn('Relevant Hindi slang meanings', bot.translation_instructions(text))
        hints = bot.translation_instructions('and then we met')
        self.assertNotIn('aand/tatte:', hints)
        self.assertIn('not abuse', bot.translation_instructions('Use DALL-E for AI images'))
        self.assertIn('broker', bot.translation_instructions('property dalal'))

    def test_chunks_preserve_all_text_and_normal_message_boundaries(self):
        lines = ['हेलो 🌏 message ' + str(i) for i in range(1000)]
        parts = bot.chunks(lines)
        self.assertEqual(''.join(parts), ''.join(line + '\n' for line in lines))
        self.assertTrue(all(len(part.encode()) <= bot.CHUNK_CHARS for part in parts))
        self.assertTrue(all(part.endswith('\n') for part in parts))


if __name__ == '__main__':
    unittest.main()
