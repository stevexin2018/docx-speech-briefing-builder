import asyncio,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import clean_speech_text as t
class RateLimit(Exception):
    status=429
    headers={'Retry-After':'2'}
class TTSControls(unittest.IsolatedAsyncioTestCase):
    async def test_authorization_error_stops_without_alternate_voice(self):
        class Forbidden(Exception):
            status = 403
        with patch('edge_tts.Communicate', side_effect=Forbidden()) as request:
            with self.assertRaisesRegex(RuntimeError, 'HTTP 403'):
                await t._synthesize_one_chunk('test', 'zh-CN-XiaoxiaoNeural', '+0%', None)
        self.assertEqual(request.call_count, 1)

    async def test_failed_publish_preserves_previous_asset_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.mp3'
            output.write_bytes(b'previous')
            with patch.object(t, '_synthesize_one_chunk', new=AsyncMock(return_value=b'new-audio')):
                with patch.object(t.os, 'replace', side_effect=PermissionError('locked')):
                    with self.assertRaises(PermissionError):
                        await t.synthesize_speech_async('test', output, proxy='http://unused')
            self.assertEqual(output.read_bytes(), b'previous')
            self.assertEqual([p.name for p in Path(folder).iterdir()], ['report.mp3'])

    async def test_retry_after_and_fixed_voice(self):
        calls=[]
        class Communicate:
            def __init__(self,*a,**kw):calls.append(kw)
            async def stream(self):
                if len(calls)==1:raise RateLimit()
                yield {'type':'audio','data':b'fake-audio'}
        with patch('edge_tts.Communicate',Communicate),patch('asyncio.sleep',new=AsyncMock()) as sleep:
            r=await t._synthesize_one_chunk('test','zh-CN-XiaoxiaoNeural','+0%',None,max_retries=2)
        self.assertEqual(r,b'fake-audio');sleep.assert_awaited_once_with(2.0)
        self.assertTrue(all(c['voice']=='zh-CN-XiaoxiaoNeural' for c in calls))
        self.assertEqual(calls[0]['connect_timeout'],15);self.assertEqual(calls[0]['receive_timeout'],60)
    async def test_parallel_failure_cancels_other_chunk_without_replay(self):
        started=[];cancelled=asyncio.Event()
        async def chunk(text,*a):
            started.append(text)
            if text.startswith('first'):
                await asyncio.sleep(.01);raise RuntimeError('fixture')
            try:await asyncio.sleep(5)
            except asyncio.CancelledError:cancelled.set();raise
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'r.mp3'
            with patch.object(t,'_synthesize_one_chunk',side_effect=chunk):
                with self.assertRaises(RuntimeError):await t.synthesize_speech_async('first。second。',str(out),proxy='http://unused',max_chunk_chars=7)
            self.assertFalse(out.exists())
        self.assertEqual(len(started),2);self.assertTrue(cancelled.is_set())
    async def test_hard_timeout_does_not_replace_previous_asset(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.mp3';p.write_bytes(b'previous')
            async def hang(*a):await asyncio.sleep(5)
            with patch.object(t,'_synthesize_one_chunk',side_effect=hang):
                with self.assertRaises(asyncio.TimeoutError):await asyncio.wait_for(t.synthesize_speech_async('text',str(p),proxy='http://unused'),timeout=.02)
            self.assertEqual(p.read_bytes(),b'previous')
