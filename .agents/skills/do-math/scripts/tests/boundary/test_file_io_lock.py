"""file_io.os_lock on the real Windows file system (a boundary that is not a port, 설계 8)."""
import os
from pathlib import Path
import tempfile
import threading
import unittest

from do_math.file_io import os_lock


@unittest.skipUnless(os.name == 'nt', 'msvcrt byte-range locks exist only on Windows')
class OsLockTests(unittest.TestCase):
    def test_a_blocking_lock_waits_for_a_holder_who_locked_the_empty_file_first(self):
        import msvcrt
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / '.acceptance.lock'
            path.touch()
            holder = os.open(path, os.O_RDWR)
            # The first opener has locked byte 0 but not yet written it; a second
            # opener that already saw size 0 reaches this state.
            msvcrt.locking(holder, msvcrt.LK_NBLCK, 1)
            release = threading.Timer(0.5, lambda: (os.lseek(holder, 0, os.SEEK_SET),
                                                    msvcrt.locking(holder, msvcrt.LK_UNLCK, 1)))
            release.start()
            try:
                with os_lock(path, blocking=True):
                    acquired = True
            finally:
                release.join()
                os.close(holder)
            self.assertTrue(acquired)
            self.assertEqual(path.read_bytes(), b'\0')
            with os_lock(path, blocking=False):
                reacquired = True
            self.assertTrue(reacquired)


if __name__ == '__main__':
    unittest.main()
