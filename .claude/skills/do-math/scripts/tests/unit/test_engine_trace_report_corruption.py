"""잘린 JSON과 읽을 수 없는 경로를 완료 증거로 바꾸지 않는다."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from do_math.trace_report import phase_rows, progress, trace_rows
from support.fakes.clock import FakeClock


class TraceCorruptionTests(unittest.TestCase):
    def test_invalid_rows_and_unreadable_paths_keep_exact_source_and_no_completion(self):
        clock = FakeClock()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'a.jsonl').mkdir()
            raw = b'[]\n{"event":"completed"\n'
            (root / 'b.jsonl').write_bytes(raw)
            start = {'event': 'started', 'operation_id': 'OP-one', 'span_id': 'SP-one',
                     'phase': 'publish', 'observed_at': clock.now()}
            content = (json.dumps(start) + '\n').encode()
            (root / 'c.jsonl').write_bytes(content)
            clock.advance(11)
            rows = trace_rows(root, clock=clock)
            self.assertEqual(rows[:3], [{'event': 'unreadable_trace', 'file': 'a.jsonl'},
                {'event': 'incomplete_trace', 'file': 'b.jsonl'}, {'event': 'incomplete_trace', 'file': 'b.jsonl'}])
            self.assertEqual(rows[3], {**start, '_trace_source': {'path': str(root / 'c.jsonl'),
                'sha256': hashlib.sha256(content).hexdigest(), 'observed_at': clock.now()}})
            phases = phase_rows(root, clock=clock)
            self.assertEqual(len(phases), 1)
            self.assertEqual((phases[0]['created_at_utc'], phases[0]['ended_at_utc'], phases[0]['elapsed_ns']),
                             (start['observed_at'], None, None))
            self.assertNotIn('outcome', phases[0])

    def test_unreadable_error_sidecar_has_bounded_explicit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'errors').mkdir()
            (root / 'live').mkdir()
            for index in range(18):
                (root / 'errors' / f'{index:02}.json').write_bytes(b'{broken')
            clock = FakeClock()
            result = progress(root, clock=clock)
            self.assertEqual(result['telemetry_errors'], [
                {'operation_id': f'{index:02}', 'status': 'unreadable_error_record'} for index in range(2, 18)])
            self.assertEqual(result['rows'], [])
            self.assertEqual(result['observed_at'], clock.now())
