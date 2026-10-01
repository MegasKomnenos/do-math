"""The canonical fingerprint rule accepts observed wall time and racy window values."""
import unittest

from do_math.file_io import fingerprint_settled


class FingerprintFoundationTests(unittest.TestCase):
    def test_foundation_explicit_clock_and_window_keep_strict_age_and_both_file_times(self):
        for modified, born in ((100, 200), (200, 100)):
            with self.subTest(modified=modified, born=born):
                fingerprint = (10, modified, born)
                self.assertFalse(fingerprint_settled(fingerprint, now_ns=210, racy_ns=10))
                self.assertTrue(fingerprint_settled(fingerprint, now_ns=211, racy_ns=10))
                self.assertFalse(fingerprint_settled(fingerprint, now_ns=199, racy_ns=0))
                self.assertFalse(fingerprint_settled(fingerprint, now_ns=200, racy_ns=0))
                self.assertTrue(fingerprint_settled(fingerprint, now_ns=201, racy_ns=0))
