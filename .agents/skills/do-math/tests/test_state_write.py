"""Windows state publication while a reader briefly holds the old file."""

import os
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner


class StreamingWriteTests(unittest.TestCase):
    def test_unicode_and_escaping_match_existing_format(self):
        value = {"한글😀": ["\"\\\n\t" * 20000, "끝", True, None, 1.5]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            expected = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            # The publication path must not materialize the full JSON via dumps.
            with patch.object(runner.json, "dumps", side_effect=AssertionError("whole-document allocation")):
                runner.write_json(path, value)
            self.assertEqual(path.read_bytes(), expected)

    def test_interrupted_encoding_preserves_old_file_and_cleans_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            runner.write_json(path, {"old": True})
            def broken(value):
                yield " " * 200000
                raise MemoryError("injected after partial write")
            with patch.object(runner.JSON_ENCODER, "iterencode", broken):
                with self.assertRaises(MemoryError):
                    runner.write_json(path, {"new": True})
            self.assertEqual(runner.read_json(path), {"old": True})
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def test_save_releases_reserve_and_retries_once(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = object.__new__(runner.Runner)
            engine.state_path = Path(directory) / "state.json"
            engine.state = {"generation": 2}
            engine.reserve = runner.EmergencyMemory(1024 * 1024)
            real_write = runner.write_json
            calls = []
            def failing_once(path, value):
                calls.append(engine.reserve.buffer is None)
                if len(calls) == 1:
                    raise MemoryError("injected")
                real_write(path, value)
            with patch.object(runner, "write_json", failing_once):
                engine.save()
            self.assertEqual(calls, [False, True])
            self.assertEqual(runner.read_json(engine.state_path), engine.state)
            self.assertIsNone(engine.reserve.buffer)
            engine.reserve.restore()
            self.assertEqual(len(engine.reserve.buffer), 1024 * 1024)


@unittest.skipUnless(os.name == "nt", "Windows file sharing behavior")
class StateWriteTests(unittest.TestCase):
    def test_reader_releases_old_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            runner.write_json(path, {"generation": 1})
            reader = path.open("rb")
            release = threading.Timer(1.15, reader.close)
            try:
                # Reproduce the exact OS failure before exercising the fix.
                probe = path.with_name("probe.json")
                probe.write_text("{}", encoding="utf-8")
                with self.assertRaises(OSError) as caught:
                    os.replace(probe, path)
                self.assertIn(caught.exception.winerror, (5, 32, 33))
                self.assertEqual(runner.read_json(path), {"generation": 1})
                release.start()
                runner.write_json(path, {"generation": 2})
            finally:
                release.join() if release.ident is not None else None
                reader.close()
            self.assertEqual(runner.read_json(path), {"generation": 2})

    def test_persistent_denial_remains_an_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            runner.write_json(path, {"generation": 1})
            with path.open("rb"), patch.object(
                runner.time, "monotonic", side_effect=[0, 2, 59.95, 60]
            ), patch.object(runner.time, "sleep") as sleep:
                with self.assertRaises(OSError):
                    runner.write_json(path, {"generation": 2})
            self.assertEqual(sleep.call_count, 2)
            self.assertEqual(runner.read_json(path), {"generation": 1})


if __name__ == "__main__":
    unittest.main()
