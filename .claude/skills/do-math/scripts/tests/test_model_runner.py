from __future__ import annotations
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import do_math.model_runner as runner
from provider_fixtures import Adapter, runner_with


class Tests(unittest.TestCase):
 def run_with(self, collected):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; r=runner_with(Adapter(collected))
   return r.run(prompt='x',output_schema={'type':'object','required':['x']},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1)
 def test_completed_only_after_schema(self):
  # The collector's parsed stream lists one usage row per report (codex_adapter._parse_jsonl).
  x=self.run_with({'result':'output_collected','final':{'raw':b'{"x":1}'},'jsonl':{'usage':[{'input_tokens':1}]}})
  self.assertEqual(x['status'],'completed')
  self.assertEqual(x['usage'],{'input_tokens':1})
 def test_invalid_output_keeps_parsed_value_and_actionable_schema_error(self):
  x=self.run_with({'result':'output_collected','final':{'raw':b'{}'},'jsonl':{'usage':{}}})
  self.assertEqual(x['status'],'failed')
  self.assertEqual(x.get('error_kind'),'output_validation')
  self.assertEqual(x['output'],{})
  self.assertIn('x',x['error'])
 def test_incomplete_fails(self):
  x=self.run_with({'result':'incomplete','reasons':['tail'],'jsonl':{}})
  self.assertEqual(x['status'],'failed')
 def test_callback_failure_does_not_resume(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; a=Adapter({}); r=runner_with(a)
   with self.assertRaises(RuntimeError): r.run(prompt='x',output_schema={},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,on_started=lambda _:(_ for _ in ()).throw(RuntimeError()))
   self.assertTrue(a.stopped)
   self.assertFalse(getattr(a,'resumed',False), 'a failed start record must not resume the root')
 def test_pre_start_stop_does_not_resume(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; a=Adapter({'result':'incomplete','jsonl':{}}); r=runner_with(a)
   x=r.run(prompt='x',output_schema={},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,should_stop=lambda:True)
   self.assertEqual(x['status'],'stopped'); self.assertTrue(a.stopped); self.assertFalse(getattr(a,'resumed',False))
 def test_scholarly_server_is_written_to_the_immutable_worker_request(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); ws=root/'ws'; ws.mkdir(); ev=root/'e'; a=Adapter({'result':'output_collected','final':{'raw':b'{}'},'jsonl':{'usage':{}}}); r=runner_with(a)
   r.run(prompt='x',output_schema={'type':'object'},workspace=ws,evidence_dir=ev,model='m',effort='low',timeout_seconds=1,scholarly_server={'command':'python','args':['C:/server.py']})
   self.assertEqual(a.request['scholarly_server'],{'command':'python','args':['C:/server.py']})
class WithoutDeadlineTests(unittest.TestCase):
    def run_observed(self, *, timeout=None, stop=False):
        from unittest.mock import patch
        clock = [0.0]
        class LiveAdapter(Adapter):
            polls = 0
            def wait_for_termination(self, *args):
                self.polls += 1
                clock[0] += 10000
                return self.stopped or self.polls >= 9
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            adapter = LiveAdapter({'result': 'output_collected', 'final': {'raw': b'{}'}, 'jsonl': {}})
            worker = runner_with(adapter)
            with patch.object(runner.time, 'monotonic', side_effect=lambda: clock[0]), patch.object(runner.time, 'sleep'):
                result = worker.run(prompt='x', output_schema={}, workspace=root, evidence_dir=root / 'evidence',
                    model='m', effort='low', timeout_seconds=timeout,
                    should_stop=lambda: stop and adapter.polls >= 4)
            return result, adapter

    def test_observation_burst_preserves_order_and_split_utf8_tail(self):
        import json
        from unittest.mock import patch
        expected = [{"type": "item.updated", "index": index, "text": "x" * 960}
                    for index in range(2000)]
        last = {"type": "item.updated", "index": 2000, "text": "가"}
        encoded = json.dumps(last, ensure_ascii=False).encode("utf-8")
        cut = encoded.index("가".encode("utf-8")) + 1
        first = b"".join(json.dumps(row).encode("utf-8") + b"\r\n" for row in expected) + b"\r\n" + encoded[:cut]
        second = encoded[cut:] + b"\r\nnot-json\r\n" + b'{"type":'

        class BurstAdapter(Adapter):
            polls = 0
            def wait_for_termination(self, *args):
                self.polls += 1
                path = Path(self.request["stdout_path"])
                if self.polls == 1:
                    path.write_bytes(first)
                elif self.polls == 2:
                    with path.open("ab") as stream:
                        stream.write(second)
                return self.polls >= 4

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            worker = runner_with(BurstAdapter({"result": "output_collected", "final": {"raw": b"{}"}, "jsonl": {}}))
            observed = []
            with patch.object(runner.time, "sleep"):
                result = worker.run(prompt="fixture", output_schema={}, workspace=root, evidence_dir=root / "evidence",
                    model="fixture", effort="low", timeout_seconds=None, on_observation=observed.append)
        self.assertEqual(result["status"], "completed")
        events = [row for batch in observed for row in batch.events]
        self.assertEqual([row for row in events if row.get("type") == "item.updated"], [*expected, last])
        # After the Job ends, the runner also delivers the unterminated last row.
        self.assertEqual([row for row in events if row.get("type") == "unparsed_observation"],
                         [{"type": "unparsed_observation", "bytes": len(b"not-json\r")},
                          {"type": "unparsed_observation", "bytes": len(b'{"type":')}])
        self.assertEqual(observed[-1].end_offset, len(first) + len(second))
        rows = [row for batch in observed for row in batch.rows]
        self.assertEqual(b"".join(rows), (first + second).replace(b"\r\n\r\n", b"\r\n"))
        numbers = [batch.first_row + index for batch in observed for index in range(len(batch.rows))]
        self.assertEqual(numbers, list(range(len(rows))))
        for batch in observed:
            for (start, end), row in zip(batch.offsets, batch.rows):
                self.assertEqual((first + second)[start:end], row)

    def test_long_running_work_keeps_running_until_its_normal_return(self):
        result, adapter = self.run_observed()
        self.assertEqual(result['status'], 'completed')
        self.assertFalse(adapter.stopped)
        self.assertIsNone(adapter.request['max_runtime_seconds'])

    def test_work_without_a_deadline_still_obeys_stop(self):
        result, adapter = self.run_observed(stop=True)
        self.assertEqual(result['status'], 'stopped')
        self.assertTrue(adapter.stopped)

    def test_a_finite_call_deadline_still_stops_the_runner(self):
        result, adapter = self.run_observed(timeout=1)
        self.assertEqual(result['status'], 'stopped')
        self.assertTrue(adapter.stopped)


if __name__=='__main__': unittest.main()
