"""The stage-1f ledgers stay true to the tests as legacy tests move (설계 9.1, 1f; 보존 지식 처분표).

``tests/migration/legacy_ids.txt`` is every legacy test (``tests/test_*.py``) at
the start of 1f. When a legacy test is removed, ``legacy_dispositions.json``
records where it went: ``moved`` to new test IDs that exist, or ``retired``
with the reason its property is checked elsewhere or no longer exists. A legacy
test that fixed a defect's behaviour as its expectation moves as it is (설계
9.1); on real storage it then reproduces an open known defect, carries its mark,
and its entry names it in ``known_defect`` so stage 2 corrects the test with the
defect (과정 결함 P2).
``preserved_knowledge.json`` gives each required rule of the 조사 3부 list its
disposition: ``moved`` or ``kept`` (``where``), or ``retired`` (``reason``);
``pending`` is allowed only while legacy tests remain.
"""
import json
from pathlib import Path
import unittest

from support.known_defects import read_ledger

MIGRATION = Path(__file__).resolve().parents[1] / 'migration'
DISPOSITIONS = {'moved', 'retired'}
KNOWLEDGE = {'pending', 'moved', 'retired', 'kept'}


def _discovered():
    """``(legacy test IDs, new-system test IDs)`` the runner discovers now."""
    import run_tests
    legacy, new = set(), set()
    for test in run_tests.discover():
        (new if run_tests.folder_of(test) else legacy).add(test.id())
    return legacy, new


class MigrationLedgerTests(unittest.TestCase):
    def test_every_legacy_test_is_still_present_or_disposed_of(self):
        baseline = set((MIGRATION / 'legacy_ids.txt').read_text(encoding='utf-8').split())
        entries = json.loads((MIGRATION / 'legacy_dispositions.json').read_text(encoding='utf-8'))['entries']
        legacy, new = _discovered()
        open_defects = {row['id'] for row in read_ledger() if row['status'] == 'open'}
        disposed = [entry['legacy_id'] for entry in entries]
        self.assertEqual(len(disposed), len(set(disposed)), 'a legacy test disposed of twice')
        self.assertEqual(sorted(legacy - baseline), [], 'legacy tests added after the baseline; write new tests instead')
        self.assertEqual(sorted(baseline - legacy - set(disposed)), [], 'removed legacy tests without a disposition')
        for entry in entries:
            with self.subTest(legacy=entry['legacy_id']):
                self.assertIn(entry['legacy_id'], baseline)
                self.assertNotIn(entry['legacy_id'], legacy, 'a disposed legacy test is still present')
                self.assertIn(entry['disposition'], DISPOSITIONS)
                if entry['disposition'] == 'moved':
                    self.assertTrue(entry['new_ids'])
                    self.assertEqual(sorted(set(entry['new_ids']) - new), [], 'moved to tests that do not exist')
                else:
                    self.assertTrue(entry['reason'].strip())
                if 'known_defect' in entry:
                    self.assertIn(entry['known_defect'], open_defects)

    def test_every_required_rule_has_a_disposition_before_the_legacy_tests_retire(self):
        entries = json.loads((MIGRATION / 'preserved_knowledge.json').read_text(encoding='utf-8'))['entries']
        self.assertEqual(len(entries), 61)
        self.assertEqual(len({entry['id'] for entry in entries}), 61)
        legacy, _ = _discovered()
        for entry in entries:
            with self.subTest(rule=entry['id']):
                self.assertIn(entry['disposition'], KNOWLEDGE)
                if entry['disposition'] in {'moved', 'kept'}:
                    self.assertTrue(entry['where'].strip())
                elif entry['disposition'] == 'retired':
                    self.assertTrue(entry['reason'].strip())
                elif not legacy:
                    self.fail('a required rule is still pending after the legacy tests retired')


if __name__ == '__main__':
    unittest.main()
