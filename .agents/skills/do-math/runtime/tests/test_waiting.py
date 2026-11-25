"""How a client waits for a job or build of the Lean broker (lean_broker.await_record).

The broker's state file grows with the jobs of the instance, so a waiting client does not read the
whole of it at every look. It looks for the job's result file and reads the whole record only at the
start, when that file has appeared, every WAIT_STATE seconds and once when the timeout has passed.
These tests fix what callers rely on: what is returned, that a job which ends is
seen, that the timeout is kept exactly, and how seldom the state is read. They run on a stand-in clock,
so they take no real time and do not depend on the load of the machine; no broker is started.
"""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import canon
import lean_broker
from runtime_support import write_json

JOB = "j" + "1" * 32
OTHER = "j" + "2" * 32
BUILD = "b" + "3" * 32


class Clock:
    """Stands in for the `time` module inside lean_broker: sleeping only moves the clock forward."""

    def __init__(self):
        self.now, self.sleeps, self.after_sleep = 1000.0, [], {}

    def monotonic(self):
        return self.now

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds
        action = self.after_sleep.pop(len(self.sleeps), None)
        if action:
            action()


class AwaitRecord(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.instance = Path(folder.name)
        self.paths = lean_broker.Paths(self.instance)
        self.paths.ensure()
        self.clock = Clock()
        self.reads = 0
        real = lean_broker.job_record

        def counted(paths, job_id):
            self.reads += 1
            return real(paths, job_id)

        for target, name, value in ((lean_broker, "time", self.clock), (lean_broker, "job_record", counted)):
            patcher = patch.object(target, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.asked = 0

        def asked(paths):
            self.asked += 1
            return {}

        patcher = patch.object(lean_broker, "ensure_broker", asked)
        patcher.start()
        self.addCleanup(patcher.stop)

    def running(self, *jobs, builds=()):
        write_json(self.paths.state, {"jobs": {job: {"id": job, "status": "running"} for job in jobs},
                                      "builds": {build: {"id": build, "status": "running", "modules": {}}
                                                 for build in builds}})

    def end(self, job, **fields):
        folder = self.paths.build(job) if lean_broker.BUILD_ID.match(job) else self.paths.job(job)
        folder.mkdir(parents=True, exist_ok=True)
        write_json(folder / "result.json", {"id": job, "status": "finished", "exit_code": 0, **fields})

    def test_the_state_is_read_rarely_while_the_job_runs(self):
        self.running(JOB)
        job, record, ended = lean_broker.await_record(self.paths, JOB, timeout=60)
        self.assertEqual((job, record["status"], ended), (JOB, "running", False))
        # At the start, every WAIT_STATE seconds, and once at the timeout: 8 reads in a minute, where
        # a read at each of four looks a second would have been 240.
        self.assertLessEqual(self.reads, 2 + int(60 / lean_broker.WAIT_STATE))
        self.assertGreaterEqual(self.reads, 2)
        self.assertEqual(self.clock.sleeps[0], lean_broker.WAIT_FIRST)
        self.assertLessEqual(max(self.clock.sleeps), lean_broker.WAIT_CAP)
        self.assertAlmostEqual(sum(self.clock.sleeps), 60, places=6)

    def test_a_job_that_ends_is_returned_at_the_next_look(self):
        self.running(JOB)
        self.clock.after_sleep[5] = lambda: self.end(JOB)
        started = self.clock.now
        job, record, ended = lean_broker.await_record(self.paths, JOB)
        self.assertEqual((job, record["status"], record["exit_code"], ended), (JOB, "finished", 0, True))
        self.assertEqual(len(self.clock.sleeps), 5)
        self.assertLess(self.clock.now - started, 5 * lean_broker.WAIT_CAP)
        self.assertEqual(self.reads, 2)  # at the start, and when the result file had appeared

    def test_a_job_that_ends_during_the_last_pause_is_returned_as_ended(self):
        self.running(JOB)
        last = []

        def end_once_the_deadline_is_reached():
            # Called after every pause; acts only on the pause that reaches the deadline.
            if self.clock.now >= 1002.0 and not last:
                last.append(True)
                self.end(JOB)

        for number in range(1, 40):
            self.clock.after_sleep[number] = end_once_the_deadline_is_reached
        job, record, ended = lean_broker.await_record(self.paths, JOB, timeout=2)
        self.assertTrue(last)
        self.assertEqual((record["status"], ended), ("finished", True))

    def test_the_pauses_never_run_past_the_timeout(self):
        self.running(JOB)
        job, record, ended = lean_broker.await_record(self.paths, JOB, timeout=0.6)
        self.assertFalse(ended)
        self.assertAlmostEqual(sum(self.clock.sleeps), 0.6, places=9)
        self.assertAlmostEqual(self.clock.now, 1000.6, places=9)

    def test_a_duplicate_is_followed_to_the_job_it_names(self):
        self.running(OTHER)
        folder = self.paths.job(JOB)
        folder.mkdir(parents=True)
        write_json(folder / "result.json", {"id": JOB, "status": "duplicate", "duplicate_of": OTHER})
        self.clock.after_sleep[3] = lambda: self.end(OTHER, exit_code=1)
        job, record, ended = lean_broker.await_record(self.paths, JOB)
        self.assertEqual((job, record["id"], record["exit_code"], ended), (OTHER, OTHER, 1, True))

    def test_an_unknown_job_is_refused_at_once(self):
        with self.assertRaisesRegex(ValueError, "unknown job"):
            lean_broker.await_record(self.paths, JOB, timeout=30)
        self.assertEqual(self.clock.sleeps, [])

    def test_a_submitted_request_not_yet_recorded_is_waited_for(self):
        write_json(self.paths.queue / (JOB + ".json"), {"id": JOB})
        self.clock.after_sleep[2] = lambda: self.end(JOB)
        job, record, ended = lean_broker.await_record(self.paths, JOB)
        self.assertEqual((record["status"], ended), ("finished", True))

    def test_the_broker_is_asked_for_at_once_or_after_two_seconds(self):
        self.running(JOB)
        lean_broker.await_record(self.paths, JOB, timeout=0, broker_first=True)
        self.assertEqual(self.asked, 1)
        self.asked = 0
        lean_broker.await_record(self.paths, JOB, timeout=0)
        self.assertEqual(self.asked, 0)
        lean_broker.await_record(self.paths, JOB, timeout=20)
        # Every two seconds, measured at looks that are at most WAIT_CAP apart.
        self.assertGreaterEqual(self.asked, 20 // 3 - 1)
        self.assertLessEqual(self.asked, 10)

    def test_a_missing_broker_is_raised_and_not_waited_out(self):
        self.running(JOB)

        def absent(paths):
            raise RuntimeError("No Lean broker is alive")

        with patch.object(lean_broker, "ensure_broker", absent), self.assertRaisesRegex(RuntimeError, "No Lean broker"):
            lean_broker.await_record(self.paths, JOB, timeout=600)
        self.assertLess(sum(self.clock.sleeps), 4)

    def test_wait_reports_the_timeout_and_then_the_ended_job(self):
        import contextlib
        import io
        self.running(JOB)
        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            self.assertEqual(lean_broker.wait(self.paths, JOB, timeout=1), 124)
        self.assertIn('"timeout": true', errors.getvalue())
        self.assertIn(f"run wait {JOB} again", errors.getvalue())
        self.end(JOB, exit_code=7)
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(lean_broker.wait(self.paths, JOB, timeout=1), 7)

    def test_wait_build_refuses_an_unknown_build_times_out_and_returns_the_outcome(self):
        with self.assertRaisesRegex(canon.CanonError, "unknown build"):
            canon.wait_build(self.instance, BUILD, timeout=1)
        self.running(builds=(BUILD,))
        self.assertIsNone(canon.wait_build(self.instance, BUILD, timeout=3))
        self.assertAlmostEqual(sum(self.clock.sleeps), 3, places=6)
        self.clock.after_sleep[len(self.clock.sleeps) + 2] = lambda: self.end(BUILD, modules={}, targets=[])
        outcome = canon.wait_build(self.instance, BUILD)
        self.assertEqual((outcome["ok"], outcome["build"]), (True, BUILD))


if __name__ == "__main__":
    unittest.main()
