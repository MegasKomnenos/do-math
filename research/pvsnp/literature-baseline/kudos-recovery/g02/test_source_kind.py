import unittest
from pathlib import Path
from source_kind import assess
BASE=Path(__file__).resolve().parents[2]
class SourceKindTests(unittest.TestCase):
 def test_actual_degruyter_initial_navigation_is_not_article_content(self):
  body=(BASE/'intake/kudos-recovery/g02/VER-010fc459824818ec8e6bf762/source-2b06cf9bd926dc42-41341e76469061ea.txt').read_text(encoding='utf-8')
  self.assertEqual(assess(body,202),'retry')
 def test_loading_wrapper_is_not_completed_content(self):self.assertEqual(assess('Loading...',200),'retry')
 def test_actual_cpe_is_provider_failure_not_subscription_rejection(self):
  import json
  proof=json.loads((BASE/'intake/kudos-recovery/operator/sciencedirect-after-renewal.json').read_text(encoding='utf-8'))
  self.assertEqual(assess(proof['body'],200),'provider_failure')
 def test_actual_handle_not_found_is_specific_to_link(self):
  text=(BASE/'intake/kudos-recovery/g02/VER-00108c1d6fee2df17ddd9c9d/source-62384b739ceb55ac.txt').read_text(encoding='utf-8')
  self.assertEqual(assess(text,500),'link_not_found')
 def test_generic_server_failure_remains_retry(self):self.assertEqual(assess('Service temporarily unavailable',500),'retry')
 def test_actual_empty_ams_body_is_not_completed_visit(self):
  text=(BASE/'intake/kudos-recovery/g02/VER-0035cae79b9bac8b129cb9d6/source-a802a3ec4675082d.txt').read_text(encoding='utf-8')
  self.assertEqual(assess(text,200),'retry')
if __name__=='__main__':unittest.main()
