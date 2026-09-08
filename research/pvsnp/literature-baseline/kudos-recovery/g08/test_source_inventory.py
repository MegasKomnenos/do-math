import importlib.util
import json
import unittest
import inspect
import recover as r

class SourceInventoryTests(unittest.TestCase):
    def test_observed_loading_placeholder_waits_for_real_content(self):
        m=self.module()
        with r.sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True);page=browser.new_page()
            page.set_content('<main>불러오는 중...</main><script>setTimeout(()=>document.querySelector("main").innerText="Complete publisher content",1200)</script>')
            self.assertEqual(m.capture_ready(page),'Complete publisher content')
            browser.close()
    def test_expansion_records_actual_before_after_observation(self):
        m=self.module()
        self.assertIn('expand_label',inspect.signature(m.capture_ready).parameters)
        with r.sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page()
            page.set_content('<main>Abstract: first paragraph.<span id="tail" style="display:none"> Complete remainder.</span><button onclick="document.querySelector(\'#tail\').style.display=\'inline\';this.remove()">Show more</button></main>')
            observed={}
            body=m.capture_ready(page,expand_label='Show more',observation=observed)
            self.assertIn('Complete remainder.',body)
            self.assertTrue(observed['clicked'])
            self.assertNotEqual(observed['before_text'],observed['after_text'])
            browser.close()
    def test_dynamic_empty_main_has_readiness_wait(self):
        m=self.module()
        self.assertTrue(callable(getattr(m,'capture_ready',None)))
        with r.sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page()
            page.set_content('<main></main><script>setTimeout(()=>document.querySelector("main").innerText="Una introduccio a la teoria de Arakelov. Burgos Gil. Resum: complete repository metadata and description are loaded.",1800)</script>')
            self.assertIn('Arakelov',m.capture_ready(page))
            browser.close()
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('source_inventory'))
        import source_inventory
        return source_inventory

    def test_real_resolver_query_mentions_summon_but_host_is_resolver(self):
        m=self.module()
        payload=json.loads((r.BASE/'intake/kudos-recovery/g08/VER-03ffef9bcb026605ecb23809/source-links-c568a9efb7bd28de.json').read_text(encoding='utf-8'))
        links=m.followups(payload)
        self.assertEqual(len(links),1)
        self.assertIn('books.google.com',links[0]['url'])

    def test_real_resolver_same_host_edition_choices_are_followups(self):
        m=self.module()
        payload=json.loads((r.BASE/'intake/kudos-recovery/g08/VER-0d3a9385786c55b39e507084/source-links-5d9370d2c2da3549.json').read_text(encoding='utf-8'))
        links=m.followups(payload)
        self.assertEqual(len(links),2)
        self.assertTrue(all('PP=true' in x['url'] for x in links))

if __name__=='__main__':unittest.main()
