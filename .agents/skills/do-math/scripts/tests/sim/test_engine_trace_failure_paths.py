"""실제 파일 실패와 종결 후 기록 경로. 제품의 추적 sink나 시계를 패치하지 않는다."""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.operation_trace import OperationTrace, phase, tracing


class TraceFailureTests(unittest.TestCase):
    def test_unavailable_directory_yields_no_trace_but_preserves_body_result(self):
        with tempfile.TemporaryDirectory() as directory:
            occupied = Path(directory) / 'file'
            occupied.write_bytes('기존 경로'.encode('utf-8'))
            with self.assertWarnsRegex(RuntimeWarning, 'operation telemetry unavailable'):
                with tracing(occupied) as sink:
                    self.assertIsNone(sink)
                    with phase('without_sink') as counters:
                        counters.update(rows=7)
                        self.assertEqual(counters, {'rows': 7})
            self.assertEqual(occupied.read_bytes(), '기존 경로'.encode('utf-8'))

    def test_closed_trace_appends_without_resurrecting_live_sidecar(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            sink.close()
            sink.emit({'event': 'completed', 'span_id': 'SP-late', 'phase': 'late'})
            rows = [json.loads(line) for line in sink.path.read_text(encoding='utf-8').splitlines()]
            self.assertEqual([(row['operation_id'], row['span_id'], row['event']) for row in rows],
                             [(sink.id, 'SP-late', 'completed')])
            self.assertFalse(sink.live.exists())
            self.assertEqual((sink.stream, sink.pending, sink.timer, sink.active), (None, None, None, {}))

    def test_append_failure_records_one_bounded_diagnostic_and_keeps_closed_state(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            sink.close()
            sink.path.mkdir()
            with self.assertWarnsRegex(RuntimeWarning, 'operation telemetry append_trace failed'):
                sink.emit({'event': 'completed', 'span_id': 'SP-one'})
            sink.emit({'event': 'completed', 'span_id': 'SP-two'})
            failure = json.loads((Path(directory) / 'errors' / (sink.id + '.json')).read_bytes())
            self.assertEqual((failure['operation_id'], failure['operation'], failure['count']),
                             (sink.id, 'append_trace', 2))
            self.assertEqual(failure['relative_path'], sink.path.name)
            self.assertNotIn('message', failure)
            self.assertEqual((sink.errors, sink.closed, sink.stream), (2, True, None))
