"""The call's execution window (``execution_window``, layer 2): a monotonic deadline described in UTC and a
non-revoking finish notice, moved from ``test_execution_window``.

Only an operational call has a deadline. ``publish`` computes the remaining
time from the monotonic clock value it is given and describes it in UTC from
the given wall time; ``request_finish`` writes the notice once, when the
remaining time first reaches the notice window. Every time value is passed in,
so neither function falls back to the system clock here.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from do_math.canonical import canonical_json
from do_math.execution_window import notice_seconds, publish, request_finish

WALL = datetime(2026, 9, 19, tzinfo=timezone.utc)
NOTICE_AT = '2026-09-19T00:00:17+00:00'


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))

    def test_actual_remaining_time_and_notice_do_not_revoke_authority(self):
        config = {"call_timeout_seconds": 30, "finish_notice_seconds": 60}
        # The notice is a tenth of the call limit when that is shorter than the configured notice.
        self.assertEqual(notice_seconds(config), 3)
        value = publish(self.root, "E", 130, config, clock=lambda: 110, wall_clock=WALL)
        self.assertEqual(value["remaining_ms_at_start"], 20000)
        self.assertEqual(value["deadline_source"], "operational_call")
        self.assertEqual(value["effective_deadline_at"], "2026-09-19T00:00:20+00:00")
        self.assertEqual(value["finish_notice_at"], NOTICE_AT)
        self.assertEqual(json.loads((self.root / ".control" / "execution-window.json").read_text(encoding="utf-8")),
                         value)
        self.assertFalse(request_finish(self.root, 130, config, clock=lambda: 126, now_iso=NOTICE_AT))
        self.assertTrue(request_finish(self.root, 130, config, clock=lambda: 127, now_iso=NOTICE_AT))
        self.assertFalse(request_finish(self.root, 130, config, clock=lambda: 128, now_iso=NOTICE_AT))
        self.assertFalse((self.root / "stop-request.json").exists())
        self.assertFalse((self.root / "finish-request.json").exists())
        self.assertTrue((self.root / ".control" / "execution-window.json").is_file())
        notice = json.loads((self.root / ".control" / "finish-request.json").read_text(encoding="utf-8"))
        self.assertFalse(notice["revokes_authority"])
        self.assertEqual((notice["kind"], notice["requested_at"]), ("finish_notice", NOTICE_AT))

    def test_work_without_deadline_has_no_finish_notice_after_long_elapsed_time(self):
        config = {"call_timeout_seconds": 30, "finish_notice_seconds": 60}
        value = publish(self.root, "E", None, config)
        self.assertIsNone(value["effective_deadline_at"])
        self.assertEqual(value["deadline_source"], "none")
        self.assertIsNone(value["remaining_ms_at_start"])
        self.assertIsNone(value["finish_notice_at"])
        self.assertFalse(request_finish(self.root, None, config, clock=lambda: 1000000, now_iso=NOTICE_AT))
        self.assertFalse((self.root / ".control" / "finish-request.json").exists())

    def test_fractional_clock_is_serialized_as_integer_milliseconds(self):
        config = {"call_timeout_seconds": 3, "finish_notice_seconds": 1}
        value = publish(self.root, "E", 3.375, config, clock=lambda: 1.125, wall_clock=WALL)
        self.assertEqual(value["remaining_ms_at_start"], 2250)
        self.assertEqual(value["effective_notice_ms"], 300)
        # The storage encoding refuses a float anywhere in the value, so the round trip proves integers only.
        self.assertEqual(json.loads(canonical_json(value)), value)


if __name__ == "__main__":
    unittest.main()
