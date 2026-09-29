"""The stage-1f ledgers stay true to the tests as legacy tests move (설계 9.1, 1f; 보존 지식 처분표).

``tests/migration/legacy_ids.txt`` is every legacy test (``tests/test_*.py``) at
the start of 1f, and ``preserved_knowledge.json`` lists the required rules of
the 조사 3부 list. Both stay as they are. ``regions.json`` gives every legacy
test module and every layer 1-3 product module one region. Each batch of a
region that migrates writes its own ``dispositions/<region>.json`` or
``dispositions/<region>.<batch>.json``, so parallel workers never edit the same
file, and it disposes of only its region's legacy tests:

* ``legacy``: one entry per removed legacy test, ``moved`` to new test IDs that
  exist, or ``retired`` with the reason its property is checked elsewhere or no
  longer exists. A legacy test that fixed a defect's behaviour as its
  expectation moves as it is (설계 9.1); on real storage it then reproduces an
  open known defect, carries its mark, and its entry names it in
  ``known_defect`` so stage 2 corrects the test with the defect (과정 결함 P2).
* ``knowledge``: the rules whose legacy tests the region held, each ``moved``
  or ``kept`` (``where``) or ``retired`` (``reason``). A rule without an entry
  is pending, which is allowed only while legacy tests remain.

Across all region files a legacy test or a rule is disposed of at most once.
"""
import json
from pathlib import Path
import unittest

from support.known_defects import read_ledger

MIGRATION = Path(__file__).resolve().parents[1] / 'migration'
DISPOSITIONS = {'moved', 'retired'}
KNOWLEDGE = {'moved', 'retired', 'kept'}


def _discovered():
    """``(legacy test IDs, new-system test IDs)`` the runner discovers now."""
    import run_tests
    legacy, new = set(), set()
    for test in run_tests.discover():
        (new if run_tests.folder_of(test) else legacy).add(test.id())
    return legacy, new


def _region_entries(key):
    """``[(region file name, entry)]`` of ``key`` over every region file."""
    return [(path.name, entry) for path in sorted((MIGRATION / 'dispositions').glob('*.json'))
            for entry in json.loads(path.read_text(encoding='utf-8')).get(key, [])]


class MigrationLedgerTests(unittest.TestCase):
    def test_every_legacy_test_is_still_present_or_disposed_of(self):
        baseline = set((MIGRATION / 'legacy_ids.txt').read_text(encoding='utf-8').split())
        entries = _region_entries('legacy')
        legacy, new = _discovered()
        open_defects = {row['id'] for row in read_ledger() if row['status'] == 'open'}
        disposed = [entry['legacy_id'] for _, entry in entries]
        self.assertEqual(sorted({d for d in disposed if disposed.count(d) > 1}), [], 'a legacy test disposed of twice')
        self.assertEqual(sorted(legacy - baseline), [], 'legacy tests added after the baseline; write new tests instead')
        self.assertEqual(sorted(baseline - legacy - set(disposed)), [], 'removed legacy tests without a disposition')
        for region, entry in entries:
            with self.subTest(region=region, legacy=entry['legacy_id']):
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

    def test_every_legacy_module_and_gate_module_belongs_to_exactly_one_region(self):
        from do_math.layers import LAYERS
        regions = json.loads((MIGRATION / 'regions.json').read_text(encoding='utf-8'))['regions']
        baseline = {test_id.split('.')[0] for test_id in (MIGRATION / 'legacy_ids.txt').read_text(encoding='utf-8').split()}
        for key, universe in (('legacy_modules', baseline),
                              ('product_modules', {m for m, layer in LAYERS.items() if layer in ('1', '2', '3')})):
            listed = [module for region in regions.values() for module in region[key]]
            with self.subTest(key=key):
                self.assertEqual(sorted({m for m in listed if listed.count(m) > 1}), [], 'a module in two regions')
                self.assertEqual(sorted(universe - set(listed)), [], 'modules no region holds')
                self.assertEqual(sorted(set(listed) - universe), [], 'modules the region table names that do not exist')

    def test_a_region_file_disposes_of_only_its_own_legacy_tests(self):
        regions = json.loads((MIGRATION / 'regions.json').read_text(encoding='utf-8'))['regions']
        for path in sorted((MIGRATION / 'dispositions').glob('*.json')):
            region = path.stem.split('.')[0]
            with self.subTest(file=path.name):
                self.assertIn(region, regions)
                own = set(regions[region]['legacy_modules'])
                foreign = [entry['legacy_id'] for entry in json.loads(path.read_text(encoding='utf-8')).get('legacy', [])
                           if entry['legacy_id'].split('.')[0] not in own]
                self.assertEqual(foreign, [], 'legacy tests of another region')

    def test_every_required_rule_has_a_disposition_before_the_legacy_tests_retire(self):
        rules = json.loads((MIGRATION / 'preserved_knowledge.json').read_text(encoding='utf-8'))['rules']
        ids = [rule['id'] for rule in rules]
        self.assertEqual((len(ids), len(set(ids))), (61, 61))
        entries = _region_entries('knowledge')
        disposed = [entry['id'] for _, entry in entries]
        self.assertEqual(sorted({d for d in disposed if disposed.count(d) > 1}), [], 'a rule disposed of twice')
        for region, entry in entries:
            with self.subTest(region=region, rule=entry['id']):
                self.assertIn(entry['id'], ids)
                self.assertIn(entry['disposition'], KNOWLEDGE)
                self.assertTrue(entry['reason' if entry['disposition'] == 'retired' else 'where'].strip())
        legacy, _ = _discovered()
        if not legacy:
            self.assertEqual(sorted(set(ids) - set(disposed)), [], 'required rules still pending after the legacy tests retired')


if __name__ == '__main__':
    unittest.main()
