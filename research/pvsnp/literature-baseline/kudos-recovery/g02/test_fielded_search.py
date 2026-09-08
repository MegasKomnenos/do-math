import json,unittest
from pathlib import Path
from fielded_search import title_author
BASE=Path(__file__).resolve().parents[2]
class FieldedSearchTests(unittest.TestCase):
 def test_matches_observed_advanced_dialog_expression(self):
  e=json.loads((BASE/'intake/kudos-recovery/operator/summon-advanced-observation.json').read_text(encoding='utf-8'))
  self.assertEqual(title_author('Gradient Flows','Ambrosio'),e['query']['original_query'])
 def test_parentheses_in_values_cannot_break_field_scope(self):
  q=title_author('A (survey): methods','Smith (editor)')
  self.assertEqual(q.count('('),4);self.assertIn('A survey methods',q)
if __name__=='__main__':unittest.main()
