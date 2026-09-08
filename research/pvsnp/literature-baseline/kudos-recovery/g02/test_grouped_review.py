import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError
import recovery
class GroupedReviewTests(unittest.TestCase):
 def test_requested_mr_owns_bibliography_and_link(self):
  with sync_playwright() as p:
   b=p.chromium.launch();page=b.new_page();page.route('**/*',lambda route:route.abort())
   html=(Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/fixtures/mathscinet-shared-review.html').read_text(encoding='utf-8')
   page.set_content('<main>'+html+'</main>')
   section=recovery.mathscinet_section(page,'MR1868930')
   self.assertTrue(section.inner_text().startswith('MR1868930'))
   self.assertIn('Chepyzhov, Vladimir V.; Vishik, Mark I.',section.inner_text())
   self.assertNotIn('Robinson, James',section.inner_text())
   self.assertEqual(section.locator('a[name="Article button"]').count(),1)
   self.assertEqual(section.locator('a[name="Article button"]').get_attribute('href'),'https://doi-org.libproxy.knu.ac.kr/10.1051/cocv:2002056')
   b.close()
 def test_normal_record_without_shared_article_wrapper(self):
  with sync_playwright() as p:
   b=p.chromium.launch();page=b.new_page();page.set_default_timeout(500);page.route('**/*',lambda route:route.abort())
   html=(Path(__file__).resolve().parents[2]/'intake/kudos-recovery/g02/fixtures/mathscinet-single.html').read_text(encoding='utf-8')
   page.set_content('<main>'+html+'</main>')
   try:section=recovery.mathscinet_section(page,'MR771843')
   except TimeoutError:section=None
   self.assertIsNotNone(section,'Normal single-record view must not require shared-review div.article wrapper')
   self.assertTrue(section.inner_text().startswith('MR0771843'))
   b.close()
if __name__=='__main__':unittest.main()
