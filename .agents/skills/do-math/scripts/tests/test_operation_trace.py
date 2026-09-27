"""Operation traces: phase rows, live snapshots and telemetry failures (``do_math.operation_trace``)."""
import json
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.operation_trace import LIVE_INTERVAL, OperationTrace, phase, phase_rows, progress, tracing


class OperationTraceTests(unittest.TestCase):
    def test_telemetry_failure_identifies_operation_without_leaking_exception_text(self):
        from do_math.operation_trace import OperationTrace
        with tempfile.TemporaryDirectory() as directory:
            sink=OperationTrace(directory)
            with patch('do_math.operation_trace.atomic_replace',side_effect=PermissionError(13,'private request value')):
                with self.assertWarns(RuntimeWarning):
                    sink.emit({'event':'started','span_id':'span','phase':'unit'})
            sink.close()
            observed=progress(directory)['telemetry_errors'][0]
            self.assertEqual(observed['operation'],'replace_live')
            self.assertEqual(observed['errno'],13)
            self.assertNotIn('private request value',json.dumps(observed))
            self.assertTrue(sink.path.is_file())

    def test_launcher_trace_correlation_is_separate_from_child_authority(self):
        from do_math.operation_trace import workspace_operation, child_environment
        with tempfile.TemporaryDirectory() as directory:
            @workspace_operation('launcher')
            def launcher(workspace):
                return child_environment()['DO_MATH_PARENT_OPERATION_ID']
            parent = launcher(directory)
            with patch.dict('os.environ', {'DO_MATH_PARENT_OPERATION_ID':parent}):
                with tracing(directory), phase('child'):
                    pass
            child = next(row for row in phase_rows(directory) if row['phase']=='child')
            self.assertEqual(child['parent_operation_id'], parent)

    def test_live_snapshot_is_throttled_but_never_more_than_one_interval_behind(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            writes = []
            with patch('do_math.operation_trace.atomic_replace', side_effect=lambda source, target: (
                    writes.append(json.loads(Path(source).read_text(encoding='utf-8'))), Path(source).replace(target))):
                for index in range(20):
                    sink.emit({'event': 'started', 'span_id': f's{index}', 'phase': 'unit'})
                self.assertEqual(len(writes), 1, 'rows inside one interval share one pending write')
                deadline = time.monotonic() + 5 * LIVE_INTERVAL
                while len(writes) < 2 and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertEqual(len(writes[-1]['active_spans']), 20)
                sink.emit({'event': 'completed', 'span_id': 's0', 'phase': 'unit'})
                sink.close()
                self.assertIsNone(sink.timer)
                self.assertEqual(len(sink.path.read_text(encoding='utf-8').splitlines()), 21)

    def test_a_timer_that_fires_after_close_does_not_recreate_the_removed_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            sink = OperationTrace(directory)
            sink.emit({'event': 'started', 'span_id': 'a', 'phase': 'unit'})
            sink.emit({'event': 'started', 'span_id': 'b', 'phase': 'unit'})
            self.assertIsNotNone(sink.timer, 'the second row inside the interval is pending')
            sink.close()
            sink.live.unlink()
            sink._write_pending()  # the timer had already fired and waited for the lock
            sink.emit({'event': 'completed', 'span_id': 'a', 'phase': 'unit'})
            self.assertFalse(sink.live.exists())
            self.assertEqual(len(sink.path.read_text(encoding='utf-8').splitlines()), 3)

    def test_phase_timings_preserve_overlap_and_incomplete_work(self):
        with tempfile.TemporaryDirectory() as directory:
            with tracing(directory):
                with phase('parent'):
                    with phase('child') as counters:
                        counters.update(completed_files=2,read_bytes=20)
                    # The snapshot may lag by LIVE_INTERVAL; poll for it, bounded.
                    deadline = time.monotonic() + 5 * LIVE_INTERVAL
                    while True:
                        live = progress(directory)['rows']
                        phases = [r['phase'] for r in live[0]['active_spans']] if live else None
                        if phases == ['parent'] or time.monotonic() > deadline:
                            break
                        time.sleep(0.02)
                    self.assertEqual(phases, ['parent'])
            rows=phase_rows(directory)
            self.assertEqual(len(rows),2)
            child=next(r for r in rows if r['phase']=='child')
            parent=next(r for r in rows if r['phase']=='parent')
            self.assertEqual(child['parent_span_id'],parent['span_id'])
            self.assertEqual(child['trace_write_errors'],0)
            self.assertGreaterEqual(parent['elapsed_ns'],child['elapsed_ns'])
            self.assertEqual(progress(directory)['rows'],[])
            (Path(directory)/'interrupted.jsonl').write_bytes(b'{"event": "started"}\n\xff')
            self.assertEqual(len(phase_rows(directory)), 2)


if __name__ == "__main__":
    unittest.main()
