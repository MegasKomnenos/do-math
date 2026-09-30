"""Operation traces: phase rows, live snapshots and telemetry failures (``operation_trace``, layer 3; ``trace_report``).

The trace sink is a layer-3 module (a lock and a ``threading.Timer``), called
here without an engine, so these tests live with the Sim tests. Nothing in the
product is replaced. The legacy tests replaced ``operation_trace.atomic_replace``
to fail the live replace or to record each snapshot; here a real replace fails
(the snapshot's name is taken by a directory, which Windows refuses to replace
with a file) and ``sys.monitoring`` records each replace the sink starts, with
the snapshot bytes it is about to publish (``support.provider_probes.ObservedCalls``).
The legacy tests polled the snapshot with ``time.sleep``; here the test joins
the sink's own pending timer, the thread that writes the late snapshot.
"""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from do_math import file_io
from do_math.operation_trace import LIVE_INTERVAL, OperationTrace, child_environment, phase, tracing, workspace_operation
from do_math.trace_report import phase_rows, progress
from support.provider_probes import ObservedCalls

CALLER = 'do_math.operation_trace'


def settle_timer(sink):
    """Join the sink's pending live-snapshot timers until none is pending; each join is bounded."""
    for _ in range(5):
        timer = sink.timer
        if timer is None:
            return
        timer.join(5 * LIVE_INTERVAL)
        if timer.is_alive():
            raise AssertionError('the pending live-snapshot timer did not fire within five intervals')
    raise AssertionError('the sink kept scheduling live-snapshot timers')


def snapshot_bytes(arguments):
    """What the sink is about to publish: the temporary snapshot a replace receives, read as the call starts."""
    return json.loads(Path(arguments['source']).read_text(encoding='utf-8'))


class OperationTraceTests(unittest.TestCase):
    def directory(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        return directory.name

    @unittest.skipUnless(os.name == 'nt', 'Windows refuses to replace a directory with a file; the failure is its own')
    def test_telemetry_failure_identifies_operation_without_leaking_exception_text(self):
        directory = self.directory()
        sink = OperationTrace(directory)
        sink.live.mkdir()  # the snapshot's name is a directory: the live replace fails with access denied
        # The exact error the product meets: the same replace of a temporary file onto that directory.
        probe = Path(directory) / 'probe.tmp'
        probe.write_text('{}', encoding='utf-8')
        with self.assertRaises(PermissionError) as refused:
            file_io.atomic_replace(probe, sink.live)
        message = str(refused.exception)
        self.assertEqual((refused.exception.errno, refused.exception.winerror), (13, 5))
        with self.assertWarnsRegex(RuntimeWarning, r'^operation telemetry replace_live failed \(PermissionError, '
                                                   r'errno=13, winerror=5\); execution authority is unchanged$'):
            sink.emit({'event': 'started', 'span_id': 'span', 'phase': 'unit'})
        sink.close()
        (observed,) = progress(directory)['telemetry_errors']
        self.assertEqual({key: value for key, value in observed.items() if key not in ('first_at', 'last_at')},
                         {'operation_id': sink.id, 'operation': 'replace_live', 'exception_type': 'PermissionError',
                          'errno': 13, 'winerror': 5, 'count': 1, 'relative_path': 'live/' + sink.id + '.json'})
        self.assertEqual(observed['first_at'], observed['last_at'])
        recorded = json.dumps(observed, ensure_ascii=False)
        self.assertNotIn(message, recorded)
        self.assertNotIn(refused.exception.strerror, recorded)
        self.assertTrue(sink.path.is_file())
        self.assertEqual([json.loads(line)['span_id'] for line in sink.path.read_text(encoding='utf-8').splitlines()],
                         ['span'], 'the trace row was appended although the live replace failed')

    def test_launcher_trace_correlation_is_separate_from_child_authority(self):
        directory = self.directory()

        @workspace_operation('launcher')
        def launcher(workspace):
            return child_environment()['DO_MATH_PARENT_OPERATION_ID']
        parent = launcher(directory)
        # A child process starts with the launcher's environment; its sink reads the correlation at creation.
        with patch.dict('os.environ', {'DO_MATH_PARENT_OPERATION_ID': parent}):
            with tracing(directory), phase('child'):
                pass
        child = next(row for row in phase_rows(directory) if row['phase'] == 'child')
        self.assertEqual(child['parent_operation_id'], parent)

    def test_live_snapshot_is_throttled_but_never_more_than_one_interval_behind(self):
        directory = self.directory()
        sink = OperationTrace(directory)
        with ObservedCalls(replace=file_io.atomic_replace, capture={'replace': snapshot_bytes}) as calls:
            for index in range(20):
                sink.emit({'event': 'started', 'span_id': f's{index}', 'phase': 'unit'})
            self.assertEqual(calls.count('replace', caller=CALLER), 1, 'rows inside one interval share one pending write')
            settle_timer(sink)
            writes = calls.captured('replace', caller=CALLER)
            self.assertEqual(len(writes), 2, 'the pending write ran once within the interval')
            self.assertEqual([row['span_id'] for row in writes[-1]['active_spans']], [f's{index}' for index in range(20)])
            sink.emit({'event': 'completed', 'span_id': 's0', 'phase': 'unit'})
            sink.close()
        self.assertIsNone(sink.timer)
        self.assertEqual(len(sink.path.read_text(encoding='utf-8').splitlines()), 21)

    def test_a_timer_that_fires_after_close_does_not_recreate_the_removed_snapshot(self):
        directory = self.directory()
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
        directory = self.directory()
        with tracing(directory) as sink:
            with phase('parent'):
                with phase('child') as counters:
                    counters.update(completed_files=2, read_bytes=20)
                # The snapshot may lag by LIVE_INTERVAL: its pending timer writes the state after the child ended.
                settle_timer(sink)
                live = progress(directory)['rows']
                self.assertEqual([row['phase'] for row in live[0]['active_spans']], ['parent'])
        rows = phase_rows(directory)
        self.assertEqual(len(rows), 2)
        child = next(r for r in rows if r['phase'] == 'child')
        parent = next(r for r in rows if r['phase'] == 'parent')
        self.assertEqual(child['parent_span_id'], parent['span_id'])
        self.assertEqual(child['trace_write_errors'], 0)
        self.assertGreaterEqual(parent['elapsed_ns'], child['elapsed_ns'])
        self.assertEqual(progress(directory)['rows'], [])
        (Path(directory) / 'interrupted.jsonl').write_bytes(b'{"event": "started"}\n\xff')
        self.assertEqual(len(phase_rows(directory)), 2)


if __name__ == '__main__':
    unittest.main()
