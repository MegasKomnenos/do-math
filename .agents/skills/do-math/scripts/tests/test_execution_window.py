from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.execution_window import publish, request_finish, notice_seconds


class WindowTests(unittest.TestCase):
    def test_actual_remaining_time_and_notice_do_not_revoke_authority(self):
        config = {"run_timeout_seconds": 30, "call_timeout_seconds": 600, "finish_notice_seconds": 60}
        self.assertEqual(notice_seconds(config), 3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = publish(root, "E", 130, config, "work", deadline_source="run", clock=lambda: 110,
                            wall_clock=datetime(2026, 9, 19, tzinfo=timezone.utc))
            self.assertEqual(value["remaining_seconds_at_start"], 20)
            self.assertEqual(value["effective_deadline_at"], "2026-09-19T00:00:20+00:00")
            self.assertEqual(value["finish_notice_at"], "2026-09-19T00:00:17+00:00")
            self.assertFalse(request_finish(root, 130, config, "work", clock=lambda: 126))
            self.assertTrue(request_finish(root, 130, config, "work", clock=lambda: 127))
            self.assertFalse(request_finish(root, 130, config, "work", clock=lambda: 128))
            self.assertFalse((root / "stop-request.json").exists())
            self.assertFalse(json.loads((root / "finish-request.json").read_text())["revokes_authority"])

    def test_operational_window_obeys_both_run_and_call_bounds(self):
        config = {"run_timeout_seconds": 7200, "call_timeout_seconds": 30, "finish_notice_seconds": 60}
        self.assertEqual(notice_seconds(config, "work"), 60)
        self.assertEqual(notice_seconds(config, "operations"), 3)


if __name__ == "__main__":
    unittest.main()
