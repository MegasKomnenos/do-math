"""How the Lean broker saves its state (runtime_support.write_json_compact, lean_broker.Broker.save).

The broker rewrites its whole state at each change and, while a compile runs, once a second. With the
indented writer and a state of a few megabytes that took about 200 ms a write, and it was about half
of what the broker did. The state is now written without indentation, encoded in one call. These tests
fix what readers rely on: the file parses to the same value, it is replaced as a whole, and the
broker's own readers (job_record, broker_status) read what the broker saved.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
import runtime_support
from test_lean_broker import BrokerFixture

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

    def test_the_file_parses_to_the_value_that_was_written(self):
        runtime_support.write_json_compact(self.path, VALUE)
        self.assertEqual(runtime_support.read_json(self.path), VALUE)
        self.assertEqual(json.loads(self.path.read_text(encoding="utf-8")), VALUE)

    def test_it_holds_the_same_data_as_the_indented_writer_in_fewer_bytes(self):
        other = self.folder / "indented.json"
        runtime_support.write_json(other, VALUE)
        runtime_support.write_json_compact(self.path, VALUE)
        self.assertEqual(runtime_support.read_json(self.path), runtime_support.read_json(other))
        self.assertLess(self.path.stat().st_size, other.stat().st_size)
        text = self.path.read_text(encoding="utf-8")
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
        self.assertGreater(self.path.stat().st_size, 4 * len(runtime_support.WRITE_BUFFER))
        self.assertEqual(runtime_support.read_json(self.path), big)

    def test_a_value_that_cannot_be_encoded_leaves_the_old_file(self):
        runtime_support.write_json_compact(self.path, VALUE)
        with self.assertRaises(TypeError):
            runtime_support.write_json_compact(self.path, {"bad": object()})
        self.assertEqual(runtime_support.read_json(self.path), VALUE)
        self.assertEqual([p.name for p in self.folder.iterdir()], [self.path.name])


class BrokerSavesItsState(BrokerFixture):
    def test_the_broker_writes_its_state_compactly_and_its_readers_read_it(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", marker="SAVED"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.broker.dirty = True
        self.broker.save()
        text = self.paths.state.read_text(encoding="utf-8")
        self.assertEqual(text.count("\n"), 1)
        self.assertEqual(runtime_support.read_json(self.paths.state), self.broker.state)
        self.assertEqual(lean_broker.job_record(self.paths, job_id)["status"], "finished")
        with patch.object(lean_broker, "broker_alive", return_value={}):
            status = lean_broker.broker_status(self.paths)
        self.assertIn(job_id, [job["id"] for job in status["finished"]])

    def test_a_new_broker_reads_the_state_its_predecessor_saved(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", marker="KEPT"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.broker.dirty = True
        self.broker.save()
        saved = runtime_support.read_json(self.paths.state)
        self.start_broker()
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "finished")
        self.assertEqual(self.broker.state["jobs"][job_id]["exit_code"], saved["jobs"][job_id]["exit_code"])

    def test_a_state_left_indented_by_an_earlier_broker_is_read_and_then_saved_compactly(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", marker="OLD"), expect_mb=40)
        self.until(lambda: self.finished(job_id))
        self.broker.dirty = True
        self.broker.save()
        runtime_support.write_json(self.paths.state, runtime_support.read_json(self.paths.state))
        self.assertGreater(self.paths.state.read_text(encoding="utf-8").count("\n"), 1)
        self.start_broker()
        self.assertEqual(self.broker.state["jobs"][job_id]["status"], "finished")
        self.assertEqual(self.paths.state.read_text(encoding="utf-8").count("\n"), 1)


if __name__ == "__main__":
    unittest.main()
