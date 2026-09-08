import unittest
import run
from pathlib import Path
import json
class IdentityTests(unittest.TestCase):
 def test_real_wrong_doi_binding(self):
  fx=Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/fixtures'
  p=json.loads((fx/'wrong-doi-candidate.json').read_text(encoding='utf-8'))
  self.assertFalse(run.modal_matches(p,(fx/'wrong-doi-detail.txt').read_text(encoding='utf-8')))
 def test_real_first_positive(self):
  base=Path(__file__).resolve().parents[2]
  p=json.loads((base/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()[0])
  self.assertTrue(run.modal_matches(p,(base/'intake/kudos-recovery/g02/VER-00076a8018bfd0fedd6121ad/summon-detail.txt').read_text(encoding='utf-8')))
 def test_doi_suffix_not_same_version(self):
  self.assertFalse(run.modal_matches({'title':'A','identifiers':{'doi':['10.1000/a']}}, 'DOI\n10.1000/a2'))
 def test_doi_alone_insufficient(self):
  self.assertFalse(run.modal_matches({'title':'A','identifiers':{'doi':['10.1000/a']}}, 'DOI\n10.1000/A'))
if __name__=='__main__': unittest.main()
