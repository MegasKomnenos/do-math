"""The real ledger and the real @known_defect marks name each other: each open entry its reproduction, plus the moved old tests its dispositions name."""
import unittest

from support.known_defects import find_marks, ledger_issues, moved_marks, read_ledger


class KnownDefectLedgerTests(unittest.TestCase):
    def test_ledger_and_marks_correspond(self):
        self.assertEqual(ledger_issues(read_ledger(), find_marks(), moved_marks()), [])


if __name__ == '__main__':
    unittest.main()
