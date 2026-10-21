"""Windows state publication while a reader briefly holds the old file."""

import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import runner


@unittest.skipUnless(os.name == "nt", "Windows file sharing behavior")
class StateWriteTests(unittest.TestCase):
    def test_reader_releases_old_state(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            runner.write_json(path, {"generation": 1})
            reader = path.open("rb")
            release = threading.Timer(0.15, reader.close)
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
            with path.open("rb"), patch.object(runner.time, "monotonic", side_effect=[0, 2]):
                with self.assertRaises(OSError):
                    runner.write_json(path, {"generation": 2})
            self.assertEqual(runner.read_json(path), {"generation": 1})


if __name__ == "__main__":
    unittest.main()
