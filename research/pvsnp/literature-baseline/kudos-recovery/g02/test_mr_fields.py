import json,unittest
from pathlib import Path
import mr_fields
BASE=Path(__file__).resolve().parents[2]
PAPERS=[json.loads(l) for l in (BASE/'catalog/abstract-format-partition/groups/02-needs-source-mathscinet-fields-json/members.jsonl').read_text(encoding='utf-8').splitlines()]
class MrFieldsTests(unittest.TestCase):
 def test_actual_grouped_detail_selects_volume_five(self):
  p=PAPERS[5];body=(BASE/'intake/kudos-recovery/g02'/p['paper_id']/'mathscinet.txt').read_text(encoding='utf-8')
  section=mr_fields.bibliography(p,body)
  self.assertIn('Vol. V.',section);self.assertNotIn('Vol. IV.',section);self.assertNotIn('These five volumes',section)
 def test_actual_cyrillic_title_is_used_for_additional_query(self):
  p=PAPERS[6];body=(BASE/'intake/kudos-recovery/g02'/p['paper_id']/'mathscinet.txt').read_text(encoding='utf-8')
  self.assertIn('Теория рядов',mr_fields.source_title(p,body));self.assertNotIn('cyr',mr_fields.source_title(p,body))
if __name__=='__main__':unittest.main()
