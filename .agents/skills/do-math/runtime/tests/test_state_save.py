"""How and when the Lean broker saves its state (runtime_support.write_json_compact, lean_broker.Broker.save).

How: the broker writes its whole state each time, without indentation and encoded in one call. The
first two classes fix what readers rely on: the file parses to the same value, it is replaced as a
whole, and the broker's own readers (job_record, broker_status) read what the broker saved.

When: the state of an instance that has run for days is tens of megabytes, so the broker writes it at
most every STATE_SECONDS, and at once only when it starts or exits, before a compile starts, after one
has ended, and when a client asks. The third class fixes that cadence and what clients rely on under
it: a change waits for the interval, a request is answered with the state as it is, a waiting client
learns of a compile's end from the result file, and a request that the broker has registered and not
written stays in the queue. Every test sets the interval; none waits ten seconds.
"""
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import canon
import lean_broker
import runtime_support
from broker_fixture import BrokerFixture

INTERVAL = lean_broker.STATE_SECONDS  # as the broker serves with it; the tests below set their own

VALUE = {"jobs": {"j1": {"id": "j1", "status": "finished", "exit_code": 0, "measured": {"peak_mb": 1466.25, "seconds": None}},
                  "j2": {"id": "j2", "status": "queued", "passed": 0, "reason": "경로 é — \"quoted\" \\ back\nslash"}},
         "builds": {}, "config": {"memory_budget_mb": 8192, "priority": "below_normal"}, "version": None,
         "flags": [True, False, None, 0, -1, 1.5, "", []]}


class CompactWriter(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.path = self.folder / "state é.json"

    def test_it_holds_the_same_data_as_the_indented_writer_in_fewer_bytes(self):
        other = self.folder / "indented.json"
        runtime_support.write_json(other, VALUE)
        runtime_support.write_json_compact(self.path, VALUE)
        self.assertEqual(runtime_support.read_json(self.path), VALUE)
        self.assertEqual(runtime_support.read_json(self.path), runtime_support.read_json(other))
        self.assertLess(self.path.stat().st_size, other.stat().st_size)
        text = self.path.read_text(encoding="utf-8")
        self.assertEqual(json.loads(text), VALUE)
        self.assertTrue(text.endswith("\n"))
        self.assertEqual(text.count("\n"), 1)  # one line: nothing is indented
        self.assertIn("경로 é", text)  # written as text, not as escapes, like the indented form

    def test_the_file_is_replaced_as_a_whole_and_nothing_is_left_beside_it(self):
        runtime_support.write_json_compact(self.path, {"old": "x" * 5000})
        runtime_support.write_json_compact(self.path, VALUE)
        self.assertEqual(runtime_support.read_json(self.path), VALUE)
        self.assertEqual([p.name for p in self.folder.iterdir()], [self.path.name])

    def test_a_document_larger_than_the_write_buffer_is_written_complete(self):
        big = {"builds": {f"b{n:032x}": {"id": f"b{n:032x}", "status": "finished",
                                         "modules": {f"M.N{k}": {"status": "cached", "key": "k" * 64} for k in range(12)}}
                          for n in range(300)}}
        runtime_support.write_json_compact(self.path, big)
        self.assertGreater(self.path.stat().st_size, 4 * runtime_support.WRITE_BUFFER_BYTES)
        self.assertEqual(runtime_support.read_json(self.path), big)

    def test_a_value_that_cannot_be_written_leaves_the_old_file_and_nothing_beside_it(self):
        runtime_support.write_json_compact(self.path, VALUE)
        # An object fails while it is encoded, before any file is opened. A lone surrogate is encoded and fails
        # when its text is turned into bytes, after the file beside the state was opened; that file is removed again.
        for bad, error in ((object(), TypeError), ("\ud800", UnicodeEncodeError)):
            with self.subTest(error=error.__name__):
                with self.assertRaises(error):
                    runtime_support.write_json_compact(self.path, {"bad": bad})
                self.assertEqual(runtime_support.read_json(self.path), VALUE)
                self.assertEqual([p.name for p in self.folder.iterdir()], [self.path.name])


class BrokerSavesItsState(BrokerFixture):
    def test_the_broker_writes_its_state_compactly_and_its_readers_read_it(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", marker="SAVED"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.broker.save(now=True)
        text = self.paths.state.read_text(encoding="utf-8")
        self.assertEqual(text.count("\n"), 1)
        self.assertEqual(runtime_support.read_json(self.paths.state), self.broker.state)
        self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "finished")
        with patch.object(lean_broker, "broker_alive", return_value={}):
            status = lean_broker.broker_status(self.paths)
        self.assertIn(job_id, [job["id"] for job in status["finished"]])
        # The next broker is a reader as well: it starts from the state its predecessor saved.
        saved = self.on_disk()
        self.start_broker()
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "finished")
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], saved["jobs"][job_id]["exit_code"])

    def test_a_state_left_indented_by_an_earlier_broker_is_read_and_then_saved_compactly(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", marker="OLD"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.broker.save(now=True)
        runtime_support.write_json(self.paths.state, runtime_support.read_json(self.paths.state))
        self.assertGreater(self.paths.state.read_text(encoding="utf-8").count("\n"), 1)
        self.start_broker()
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "finished")
        self.assertEqual(self.paths.state.read_text(encoding="utf-8").count("\n"), 1)


class WhenTheStateIsWritten(BrokerFixture):
    threads_budget = 1  # one compile at a time: while one runs, every later one stays queued

    def setUp(self):
        super().setUp()
        self.writes = []  # the moment of each write of the state file, on the monotonic clock
        write = lean_broker.write_json_compact

        def counted(path, value):
            if Path(path) == self.paths.state:
                self.writes.append(time.monotonic())
            return write(path, value)

        # An interval no test outlasts: within it the state is written only for the reasons under test.
        for name, value in (("write_json_compact", counted), ("STATE_SECONDS", 3600)):
            patcher = patch.object(lean_broker, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def requests(self):
        return list(self.paths.queue.glob("*" + lean_broker.STATE_REQUEST))

    def blocked(self):
        """A broker with one long compile running, so that whatever is submitted next is registered and waits."""
        self.start_broker()
        blocker = self.submit(self.session_file("s1", "Blocker.lean", sleep=60), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][blocker]["status"] == "running"
                   and self.broker.state["jobs"][blocker].get("pid"))
        self.broker.save(now=True)
        del self.writes[:]
        return blocker

    def waiting(self, name):
        """A compile submitted behind the running one and taken up by the broker."""
        job_id = self.submit(self.session_file("s1", name), expect_mb=40)
        self.broker.tick()
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "queued")
        return job_id

    def test_the_broker_serves_with_an_interval_of_ten_seconds(self):
        self.assertEqual(INTERVAL, 10.0)

    def test_changes_wait_for_the_interval_and_are_written_once_it_has_passed(self):
        self.blocked()
        before = self.on_disk()
        queued = []
        for number in range(4):  # each poll finds a new request and a changed settings file
            self.write_settings(memory_budget_mb=1000 + number)
            queued.append(self.waiting(f"Q{number}.lean"))
        self.assertEqual(self.broker.config["memory_budget_mb"], 1003)
        self.assertEqual(self.writes, [])
        behind = self.on_disk()
        self.assertEqual(behind["config"], before["config"])
        self.assertFalse(set(queued) & set(behind["jobs"]))
        # What the file does not hold yet is still in the queue, so no client takes a registered job for unknown.
        self.assertTrue(all((self.paths.queue / (job_id + ".json")).exists() for job_id in queued))
        self.assertEqual(lean_broker.job_record(self.paths, queued[0]), {"id": queued[0], "status": "submitted"})
        self.broker.written_at -= lean_broker.STATE_SECONDS  # the interval has passed
        self.broker.tick()
        self.assertEqual(len(self.writes), 1)
        written = self.on_disk()
        self.assertEqual(written["config"]["memory_budget_mb"], 1003)
        self.assertEqual([written["jobs"][job_id]["status"] for job_id in queued], ["queued"] * 4)
        self.assertFalse(any((self.paths.queue / (job_id + ".json")).exists() for job_id in queued))
        self.assertEqual(lean_broker.job_record(self.paths, queued[0])["status"], "queued")
        self.waiting("Later.lean")  # the next interval has begun
        self.assertEqual(len(self.writes), 1)

    def test_the_writes_of_a_state_that_keeps_changing_are_an_interval_apart(self):
        # On the real clock, with an interval short enough to see three writes.
        with patch.object(lean_broker, "STATE_SECONDS", 0.4):
            self.start_broker()
            del self.writes[:]
            polls, deadline = 0, time.monotonic() + 60
            while len(self.writes) < 3 and time.monotonic() < deadline:
                polls += 1
                self.write_settings(memory_budget_mb=1000 + polls)
                self.broker.tick()
                time.sleep(0.02)
        self.assertEqual(len(self.writes), 3)
        self.assertGreater(polls, 3)  # the state changed at every poll and was written at three of them
        gaps = [later - earlier for earlier, later in zip(self.writes, self.writes[1:])]
        self.assertTrue(all(gap >= 0.4 for gap in gaps), gaps)

    def test_a_request_is_answered_with_the_state_as_it_is_now(self):
        self.blocked()
        job_id = self.waiting("Asked.lean")
        self.assertEqual(self.writes, [])
        # Read without asking, as when no broker is alive: the file as it was last written.
        self.assertNotIn(job_id, [job["id"] for job in lean_broker.broker_status(self.paths)["queued"]])
        asked_at = time.time()
        status = self.status()
        self.assertIn(job_id, [job["id"] for job in status["queued"]])
        self.assertEqual(len(self.writes), 1)
        self.assertEqual(self.requests(), [])
        self.assertGreaterEqual(status["state_written_at"], asked_at - 2)  # written for this request; 2 s for a coarse file clock
        # `result` asks in the same way, where the record it shows comes from the state.
        second = self.waiting("Result.lean")
        self.assertEqual(lean_broker.job_record(self.paths, second), {"id": second, "status": "submitted"})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(self.asking(lambda: lean_broker.main(["result", str(self.instance), second])), 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "queued")
        self.assertEqual(len(self.writes), 2)
        self.assertEqual(self.requests(), [])

    def test_a_request_while_nothing_has_changed_is_answered_without_a_write(self):
        self.start_broker()
        del self.writes[:]
        status = self.status()
        self.assertIn("4.0.0-fake", status["version"])
        self.assertEqual(self.writes, [])
        self.assertEqual(self.requests(), [])

    def test_an_earlier_broker_is_not_asked_and_its_file_is_read_as_it_is(self):
        # After an installation the broker that is running can be of the version before this one. It
        # writes its state at each change and knows no request, and its receipt has no `state_seconds`.
        self.start_broker()
        receipt = {"process": runtime_support.process_identity(os.getpid()), "started_at": time.time()}
        started = time.monotonic()
        with patch.object(lean_broker, "broker_alive", return_value=receipt), \
                patch.object(Path, "touch", side_effect=AssertionError("a request was put into the queue")):
            status = lean_broker.broker_status(self.paths)
        self.assertLess(time.monotonic() - started, 5)
        self.assertTrue(status["broker_alive"])
        self.assertIn("4.0.0-fake", status["version"])

    def test_a_broker_that_does_not_answer_never_holds_the_client(self):
        self.blocked()
        job_id = self.waiting("Unanswered.lean")
        receipt = {"process": runtime_support.process_identity(os.getpid()), "state_seconds": INTERVAL}
        # Alive and silent: the client waits READY_SECONDS, withdraws its request and reports the file as it is.
        started = time.monotonic()
        with patch.object(lean_broker, "broker_alive", return_value=receipt), patch.object(lean_broker, "READY_SECONDS", 0.4):
            status = lean_broker.broker_status(self.paths)
        waited = time.monotonic() - started
        self.assertGreaterEqual(waited, 0.4)
        self.assertLess(waited, 10)
        self.assertEqual(self.requests(), [])
        self.assertNotIn(job_id, [job["id"] for job in status["queued"]])
        self.assertEqual(status["state_written_at"], self.paths.state.stat().st_mtime)  # how old the report is
        # Dead before it answered: the client stops waiting at its next look for the broker.
        looks = iter([receipt, receipt])  # by broker_status and by saved_state before it asks; none afterwards
        started = time.monotonic()
        with patch.object(lean_broker, "broker_alive", side_effect=lambda paths: next(looks, None)):
            lean_broker.broker_status(self.paths)
        self.assertLess(time.monotonic() - started, 5)
        self.assertEqual(self.requests(), [])
        self.assertEqual(self.writes, [])

    def test_a_client_that_cannot_write_into_the_queue_reads_the_file_as_it_is(self):
        # `status` only reads the instance where it may not write: it then shows the file without asking.
        self.start_broker()
        receipt = {"process": runtime_support.process_identity(os.getpid()), "state_seconds": INTERVAL}
        with patch.object(lean_broker, "broker_alive", return_value=receipt), \
                patch.object(Path, "touch", side_effect=PermissionError("the instance is read-only")):
            status = lean_broker.broker_status(self.paths)
        self.assertIn("4.0.0-fake", status["version"])
        self.assertEqual(self.requests(), [])

    def test_a_request_left_in_the_queue_is_removed_at_the_next_poll(self):
        # A client that died while it waited leaves its request; the next poll answers it like any other.
        self.start_broker()
        left = self.paths.queue / ("0" * 32 + lean_broker.STATE_REQUEST)
        left.touch()
        self.broker.tick()
        self.assertEqual(self.requests(), [])

    def test_a_waiting_client_learns_of_the_end_while_the_state_file_is_behind(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", sleep=1, exit=3), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id]["status"] == "running")
        ended = []

        def client():
            with patch.object(lean_broker, "ensure_broker", return_value={}):
                ended.append((lean_broker.await_record(self.paths, job_id), time.monotonic()))

        thread = threading.Thread(target=client)
        thread.start()
        with patch.object(lean_broker, "write_json_compact"):  # no state is written from here on, as within an interval
            self.until(lambda: self.finished(job_id))
            finished_at = time.monotonic()
            thread.join(timeout=30)
        self.assertFalse(thread.is_alive())
        (_, record, has_ended), returned_at = ended[0]
        self.assertEqual((record["status"], record["exit_code"], has_ended), ("finished", 3, True))
        # The client looks for the result file at most WAIT_CAP apart; the interval of the state is ten seconds.
        self.assertLess(returned_at - finished_at, lean_broker.WAIT_CAP + 3)
        self.assertLess(lean_broker.WAIT_CAP + 3, INTERVAL)
        self.assertEqual(self.on_disk()["jobs"][job_id]["status"], "running")
        with patch.object(lean_broker, "ensure_broker", return_value={}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lean_broker.wait(self.paths, job_id, timeout=0), 3)

    def test_the_end_of_a_build_is_read_by_the_runner_and_by_a_session_while_the_state_file_is_behind(self):
        # canon.build_outcome is what the runner asks at each of its own passes over a publication, and canon.wait_build
        # what a session's build command waits in.
        self.start_broker()
        root = self.tree()
        build_id = self.build(root, [root / "D.lean"])
        self.until(lambda: self.build_record(build_id)["status"] == "running")
        self.assertIsNone(canon.build_outcome(self.instance, build_id))
        with patch.object(lean_broker, "write_json_compact"):
            self.until(lambda: self.build_record(build_id)["status"] in lean_broker.FINISHED)
        self.assertEqual(self.on_disk()["builds"][build_id]["status"], "running")
        self.assertTrue(canon.build_outcome(self.instance, build_id)["ok"])
        self.assertTrue(canon.wait_build(self.instance, build_id, timeout=0)["ok"])

    def test_a_compile_starts_only_once_the_state_holds_its_host(self):
        # Kept at once: a Lean that ran with no record of its host could not be followed by the next broker.
        self.start_broker()
        seen = {}
        write_bytes = Path.write_bytes

        def at_go(path, data):
            if path.name == "GO":
                seen[path.parent.name] = self.on_disk()["jobs"].get(path.parent.name)
            return write_bytes(path, data)

        with patch.object(Path, "write_bytes", at_go):
            job = self.compiled(self.session_file("s1", marker="STARTED"))
        record = seen[job["id"]]
        self.assertEqual((record["status"], record["host"]), ("running", job["host"]))
        self.assertTrue(all(record and record["status"] == "running" for record in seen.values()), seen)

    def test_a_compile_that_ended_is_in_the_state_at_the_end_of_that_pass(self):
        # Kept at once: a broker starting from a file that still called the compile running would end it
        # again from the memory last written, and record that as its cost.
        self.start_broker()
        job = self.compiled(self.session_file("s1", alloc_mb=60, sleep=1))
        written = self.on_disk()["jobs"][job["id"]]
        self.assertEqual((written["status"], written["exit_code"], written["measured"]),
                         ("finished", 0, job["measured"]))
        self.assertGreater(written["measured"]["peak_mb"], 60)

        def samples():
            return runtime_support.read_json(self.paths.calibration)["entries"][job["closure"]]["excess_mb"]

        self.assertEqual(samples(), [job["measured"]["excess_mb"]])
        self.start_broker()
        self.broker.tick()
        self.assertEqual(samples(), [job["measured"]["excess_mb"]])
        self.assertEqual(self.broker.state["jobs"][job["id"]]["measured"], job["measured"])

    def test_a_broker_that_exits_on_its_own_writes_what_it_had_not_written(self):
        broker = lean_broker.Broker(self.instance, log_path=self.paths.log)
        looks = []

        def exits_at_the_second_look(served):
            looks.append(len(self.writes))
            if len(looks) == 1:
                self.write_settings(memory_budget_mb=4321)  # the next poll applies it and writes nothing
                return False
            return True

        try:
            with patch.object(lean_broker.Broker, "should_exit", exits_at_the_second_look), \
                    contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(broker.serve(), 0)
            self.assertEqual(runtime_support.read_json(self.paths.process)["state_seconds"], lean_broker.STATE_SECONDS)
        finally:
            self.paths.process.unlink(missing_ok=True)  # this process is no broker for tearDown to stop
        self.assertEqual(broker.config["memory_budget_mb"], 4321)
        self.assertEqual(looks[1], looks[0])  # the poll that applied the change did not write
        self.assertEqual(len(self.writes), looks[1] + 1)
        self.assertEqual(self.on_disk()["config"]["memory_budget_mb"], 4321)


if __name__ == "__main__":
    unittest.main()
