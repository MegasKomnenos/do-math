"""The known-defect ledger and the @known_defect marks must name each other exactly."""
import io
import textwrap
from pathlib import Path
import tempfile
import unittest

from support.known_defects import find_marks, known_defect, ledger_issues


def _entry(identifier, test, status='open'):
    return {'id': identifier, 'summary': 's', 'category': 1, 'reproduction': test,
            'found_by': 'f', 'missed_kind': 'k', 'status': status}


class LedgerRuleTests(unittest.TestCase):
    def test_open_entry_matching_its_marked_reproduction_has_no_issue(self):
        marks = {'KD-0001': ['unit.test_a.A.test_x']}
        self.assertEqual(ledger_issues([_entry('KD-0001', 'unit.test_a.A.test_x')], marks), [])

    def test_mark_without_a_ledger_entry_is_reported(self):
        issues = ledger_issues([], {'KD-0002': ['unit.test_a.A.test_x']})
        self.assertEqual([issue['rule'] for issue in issues], ['mark_without_entry'])

    def test_open_entry_without_its_marked_reproduction_is_reported(self):
        issues = ledger_issues([_entry('KD-0003', 'unit.test_a.A.test_x')], {})
        self.assertEqual([issue['rule'] for issue in issues], ['open_entry_without_mark'])

    def test_mark_on_a_different_test_than_the_entry_names_is_reported(self):
        issues = ledger_issues([_entry('KD-0004', 'unit.test_a.A.test_x')], {'KD-0004': ['unit.test_a.A.test_y']})
        self.assertEqual([issue['rule'] for issue in issues], ['reproduction_mismatch'])

    def test_moved_legacy_tests_the_dispositions_name_may_carry_the_mark_too(self):
        """설계 9.1, A28: a moved old test that the defect breaks on the real path keeps the entry's mark."""
        marks = {'KD-0009': ['unit.test_a.A.test_x', 'sim.test_b.B.test_moved']}
        moved = {'KD-0009': {'sim.test_b.B.test_moved'}}
        self.assertEqual(ledger_issues([_entry('KD-0009', 'unit.test_a.A.test_x')], marks, moved), [])

    def test_an_extra_mark_no_disposition_names_is_reported(self):
        marks = {'KD-0010': ['unit.test_a.A.test_x', 'sim.test_b.B.test_other']}
        moved = {'KD-0010': {'sim.test_b.B.test_moved'}}
        issues = ledger_issues([_entry('KD-0010', 'unit.test_a.A.test_x')], marks, moved)
        self.assertEqual([issue['rule'] for issue in issues], ['reproduction_mismatch'])

    def test_closed_entry_must_not_keep_its_mark(self):
        issues = ledger_issues([_entry('KD-0005', 'unit.test_a.A.test_x', 'closed')],
                               {'KD-0005': ['unit.test_a.A.test_x']})
        self.assertEqual([issue['rule'] for issue in issues], ['closed_entry_still_marked'])

    def test_entry_missing_a_required_field_is_reported(self):
        entry = _entry('KD-0006', 'unit.test_a.A.test_x')
        del entry['missed_kind']
        issues = ledger_issues([entry], {'KD-0006': ['unit.test_a.A.test_x']})
        self.assertEqual([issue['rule'] for issue in issues], ['entry_shape'])


class MarkDiscoveryTests(unittest.TestCase):
    def test_marks_are_found_with_their_full_test_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'unit').mkdir()
            (root / 'unit' / 'test_sample.py').write_text(textwrap.dedent('''
                from support.known_defects import known_defect
                class Sample:
                    @known_defect('KD-0007')
                    def test_bug(self): pass
                    def test_plain(self): pass
            '''), encoding='utf-8')
            self.assertEqual(find_marks(root), {'KD-0007': ['unit.test_sample.Sample.test_bug']})


class MarkBehaviourTests(unittest.TestCase):
    def _run(self, body):
        case = type('Case', (unittest.TestCase,), {'test_it': known_defect('KD-0008')(body)})
        result = unittest.TextTestRunner(stream=io.StringIO()).run(case('test_it'))
        return result

    def test_a_marked_failure_counts_as_the_known_defect(self):
        result = self._run(lambda self: self.fail('defect reproduces'))
        self.assertEqual(len(result.expectedFailures), 1)
        self.assertTrue(result.wasSuccessful())

    def test_a_marked_test_that_passes_fails_the_run(self):
        result = self._run(lambda self: None)
        self.assertEqual(len(result.unexpectedSuccesses), 1)
        self.assertFalse(result.wasSuccessful())


if __name__ == '__main__':
    unittest.main()
