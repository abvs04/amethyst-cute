import os
import tempfile
import time
import unittest
from types import SimpleNamespace as NS
from unittest.mock import AsyncMock, patch
os.environ['TELEGRAM_BOT_TOKEN']='123:test'
os.environ['AI_PROVIDER']='groq'
os.environ.pop('GROQ_API_KEY',None)
import bot
from who_said import select_round, start_game

class Game(unittest.IsolatedAsyncioTestCase):
    async def test_quiz_scope_cooldown_and_failed_send_retry(self):
        with tempfile.TemporaryDirectory() as d, patch.object(bot,'DB', d+'/test.db'):
            for i,name in enumerate(['A','B','C'],1):
                bot.save_message(-1,i,int(time.time()-1000),name,'This was my original message number '+str(i))
            bot.save_message(-2,1,1,'Secret','Do not include another group message')
            message=NS(message_id=10,reply_text=AsyncMock())
            update=NS(effective_chat=NS(id=-1,type='supergroup'),effective_message=message)
            telegram=NS(send_poll=AsyncMock(side_effect=RuntimeError('network')))
            context=NS(bot=telegram)
            with self.assertRaises(RuntimeError): await start_game(update,context,bot.connection)
            telegram.send_poll=AsyncMock()
            await start_game(update,context,bot.connection)
            kwargs=telegram.send_poll.call_args.kwargs
            self.assertEqual(kwargs['open_period'],45)
            self.assertEqual(set(kwargs['options']),{'A','B','C'})
            self.assertIn(kwargs['options'][kwargs['correct_option_id']],kwargs['explanation'])
            self.assertNotIn('another group',kwargs['question'])
            await start_game(update,context,bot.connection)
            self.assertEqual(telegram.send_poll.await_count,1)
            self.assertIn('minute',message.reply_text.call_args.args[0])

    def test_excludes_reused_ambiguous_and_recent_quotes(self):
        now=time.time()
        rows=[(1,now-1000,'A','The same quote from two people'),(2,now-1000,'B','The same quote from two people'),(3,now,'C','This is far too recent'),(4,now-1000,'A','This is the only valid quote here')]
        self.assertEqual(select_round(rows,[])[0],4)
        self.assertIsNone(select_round(rows,[4]))

if __name__=='__main__': unittest.main()
