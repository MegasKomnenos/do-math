import json
from pathlib import Path
import unittest
from reconcile import reconcile

ROOT=Path(__file__).parent
BASE=ROOT.parents[1]
FIXTURE=BASE/'intake/kudos-recovery/g08/interface'
PAPERS={p['paper_id']:p for p in (json.loads(x) for x in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines())}

class ReconcileTests(unittest.TestCase):
    def test_real_subscription_preview_is_unavailable(self):
        r=json.loads((FIXTURE/'quillen-result-before-status-repair.json').read_text(encoding='utf-8'))
        fixed=reconcile(r,PAPERS[r['paper_id']],BASE)
        self.assertEqual(fixed['fulltext']['status'],'unavailable')
    def test_real_polish_heading_is_identified(self):
        r=json.loads((FIXTURE/'ploski-result-before-binding-repair.json').read_text(encoding='utf-8'))
        fixed=reconcile(r,PAPERS[r['paper_id']],BASE)
        self.assertEqual(fixed['identity']['status'],'confirmed')
        self.assertFalse(fixed['required_sources_complete'])
        self.assertEqual(fixed['fulltext']['status'],'unresolved')

if __name__=='__main__':
    unittest.main()
