import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
import recovery
class SummonTests(unittest.TestCase):
 def test_full_abstract_boundary(self):
  with sync_playwright() as p:
   b=p.chromium.launch(); page=b.new_page(); page.route("**/*",lambda route:route.abort()); page.set_content((Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/summon-modal.html').read_text(encoding='utf-8'))
   got=recovery.summon_abstract(page)
   self.assertTrue(got.startswith('Robust stability and control'))
   self.assertTrue(got.endswith('vast and multifaceted.'))
   self.assertNotIn('Citations',got)
   b.close()
 def test_observed_fulltext_links(self):
  with sync_playwright() as p:
   b=p.chromium.launch();page=b.new_page();page.route("**/*",lambda route:route.abort());page.set_content((Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/summon-modal.html').read_text(encoding='utf-8'))
   links=recovery.source_links(page)
   self.assertTrue(any('/2.0.0/link/' in v['url'] for v in links))
   self.assertTrue(any('doi.org/10.1109/MCS.2008.931718' in v['url'] for v in links))
   b.close()
 def test_zero_results(self):
  self.assertTrue(recovery.zero_results((Path(__file__).parent.parent.parent/'intake/kudos-recovery/g02/fixtures/summon-zero.txt').read_text(encoding='utf-8')))
if __name__=='__main__': unittest.main()
