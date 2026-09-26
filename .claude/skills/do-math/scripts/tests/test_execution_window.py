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
        config = {"call_timeout_seconds": 30, "finish_notice_seconds": 60}
        self.assertEqual(notice_seconds(config), 3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = publish(root, "E", 130, config, deadline_source="operational_call", clock=lambda: 110,
                            wall_clock=datetime(2026, 9, 19, tzinfo=timezone.utc))
            self.assertEqual(value["remaining_ms_at_start"], 20000)
            self.assertEqual(value["effective_deadline_at"], "2026-09-19T00:00:20+00:00")
            self.assertEqual(value["finish_notice_at"], "2026-09-19T00:00:17+00:00")
            self.assertFalse(request_finish(root, 130, config, clock=lambda: 126))
            self.assertTrue(request_finish(root, 130, config, clock=lambda: 127))
            self.assertFalse(request_finish(root, 130, config, clock=lambda: 128))
            self.assertFalse((root / "stop-request.json").exists())
            self.assertFalse((root / "finish-request.json").exists())
            self.assertTrue((root / ".control" / "execution-window.json").is_file())
            self.assertFalse(json.loads((root / ".control" / "finish-request.json").read_text())["revokes_authority"])


    def test_work_without_deadline_has_no_finish_notice_after_long_elapsed_time(self):
        config = { "call_timeout_seconds": 30, "finish_notice_seconds": 60}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            value = publish(root, "E", None, config, deadline_source="none")
            self.assertIsNone(value["effective_deadline_at"])
            self.assertIsNone(value["remaining_ms_at_start"])
            self.assertIsNone(value["finish_notice_at"])
            self.assertFalse(request_finish(root, None, config, clock=lambda: 1000000))
            self.assertFalse((root / ".control" / "finish-request.json").exists())

    def test_fractional_clock_is_serialized_as_integer_milliseconds(self):
        from do_math.repository import canonical_json
        config = {"call_timeout_seconds": 3, "finish_notice_seconds": 1}
        with tempfile.TemporaryDirectory() as directory:
            value = publish(Path(directory), "E", 3.375, config, deadline_source="operational_call", clock=lambda: 1.125)
            self.assertEqual(value["remaining_ms_at_start"], 2250)
            self.assertEqual(value["effective_notice_ms"], 300)
            canonical_json(value)


if __name__ == "__main__":
    unittest.main()
