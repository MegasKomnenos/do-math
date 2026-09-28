"""The real ledger and the real @known_defect marks correspond one to one."""
import unittest

from support.known_defects import find_marks, ledger_issues, read_ledger


class KnownDefectLedgerTests(unittest.TestCase):
    def test_ledger_and_marks_correspond(self):
        self.assertEqual(ledger_issues(read_ledger(), find_marks()), [])


if __name__ == '__main__':
    unittest.main()
