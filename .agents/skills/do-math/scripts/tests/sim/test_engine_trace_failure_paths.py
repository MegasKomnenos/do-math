"""실제 파일 실패와 종결 후 기록 경로. 제품의 추적 sink나 시계를 패치하지 않는다."""
import json
from pathlib import Path
import tempfile
import unittest

from do_math.operation_trace import OperationTrace, child_environment, engine_operation, phase, tracing


class TraceFailureTests(unittest.TestCase):
    def test_engine_operation_factory_preserves_body_and_binds_trace_to_instance(self):
        from types import SimpleNamespace
        token, failure = object(), ValueError('original engine failure')
        def work(receiver, value, *, fail=False):
            self.assertIs(receiver, engine)
            if fail:
                raise failure
            return value
        wrapped = engine_operation('direct_engine')(work)
        with tempfile.TemporaryDirectory() as directory:
            engine = SimpleNamespace(instance={'workspace': directory, 'id': 'IN-direct'})
            self.assertIs(wrapped(engine, token), token)
            with self.assertRaisesRegex(ValueError, '^original engine failure$') as caught:
                wrapped(engine, token, fail=True)
            self.assertIs(caught.exception, failure)
            traces = [[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
                      for path in (Path(directory) / 'operations').glob('*.jsonl')]
            self.assertEqual(len(traces), 2)
            self.assertEqual(sorted([row['event'] for row in rows] for rows in traces),
                             [['started', 'completed'], ['started', 'interrupted']])
            self.assertEqual({(row['phase'], row['instance_id']) for rows in traces for row in rows},
                             {('direct_engine', 'IN-direct')})
            self.assertTrue(all(rows[0]['span_id'] == rows[1]['span_id'] for rows in traces))
            self.assertEqual(list((Path(directory) / 'operations/live').glob('*.json')), [])
        self.assertEqual(child_environment({}), {})

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


class LiveTraceFailureTests(unittest.TestCase):
    def test_live_append_failure_keeps_progress_and_bounded_diagnostic(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            self.addCleanup(sink.close)
            sink.path.mkdir()
            # Failure to write its separate diagnostic must not mask the body.
            (Path(directory) / 'errors').write_bytes(b'occupied')
            with self.assertWarnsRegex(RuntimeWarning, 'operation telemetry append_trace failed'):
                sink.emit({'event': 'completed', 'phase': 'spanless'})
            live = json.loads(sink.live.read_bytes())
            self.assertEqual((live['phase'], live['active_spans']), ('spanless', []))
            self.assertEqual((sink.errors, sink.failure['operation'], sink.stream), (1, 'append_trace', None))
            self.assertEqual((Path(directory) / 'errors').read_bytes(), b'occupied')

    def test_cleanup_failure_preserves_body_and_resets_trace_context(self):
        from do_math.operation_trace import child_environment
        with tempfile.TemporaryDirectory() as directory:
            with tracing(directory) as sink:
                # A real directory cannot be unlinked as a live JSON file.
                sink.live.mkdir()
                self.assertEqual(child_environment({})['DO_MATH_PARENT_OPERATION_ID'], sink.id)
            self.assertEqual(child_environment({}), {})
            self.assertTrue(sink.closed)
            self.assertTrue(sink.live.is_dir())

    def test_stream_close_failure_is_bounded_and_handle_is_forgotten(self):
        import io
        from unittest.mock import patch
        real_open = io.open
        closed = []
        class CloseFailure:
            def __init__(self, stream): self.stream = stream
            def write(self, raw): return self.stream.write(raw)
            def flush(self): return self.stream.flush()
            def close(self):
                self.stream.close()
                closed.append(self.stream.closed)
                raise OSError('close diagnostic')
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            def opened(path, *args, **kwargs):
                stream = real_open(path, *args, **kwargs)
                return CloseFailure(stream) if Path(path) == sink.path else stream
            # Only the external file stream's close fails; tracing stays real.
            with patch('io.open', side_effect=opened):
                sink.emit({'event': 'completed', 'phase': 'close'})
                sink.close()
            self.assertEqual(closed, [True])
            self.assertEqual((sink.stream, sink.closed), (None, True))
            self.assertEqual(json.loads(sink.path.read_text().splitlines()[0])['phase'], 'close')
