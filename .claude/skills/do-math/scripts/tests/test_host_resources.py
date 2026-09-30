"""Local instance reservations and real Windows Job resource enforcement.

All numbers here are disposable test budgets, never product defaults.
"""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from do_math.windows_job import WindowsJob


@unittest.skipUnless(os.name == "nt", "Windows kernel required")
class HostJobTests(unittest.TestCase):
    def test_transient_resource_exhaustion_is_not_a_structural_unsupported_fact(self):
        import ctypes
        from do_math.windows_job import WindowsJobUnsupportedError
        def exhausted(*args):
            ctypes.set_last_error(8)  # ERROR_NOT_ENOUGH_MEMORY; not a capability result.
            return 0
        with patch("do_math.windows_job._kernel32.SetInformationJobObject", side_effect=exhausted):
            with self.assertRaises(OSError) as caught:
                WindowsJob([sys.executable, "-c", "pass"],
                    resource_limits={"memory_bytes": 128*1024**2, "cpu_rate_basis_points": 1000})
        self.assertNotIsInstance(caught.exception, WindowsJobUnsupportedError)


if __name__ == "__main__":
    unittest.main()
