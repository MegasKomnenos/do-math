import unittest
import recover as r
import native_source

class NativeSourceTests(unittest.TestCase):
    def test_actual_pdf_control_hydrates_and_reference_pdfs_are_excluded(self):
        import json
        lines=(r.ROOT.parent/'g05/tdd/restart-native-pdf-click-2.log').read_text(encoding='utf-8-sig').splitlines()
        actual=json.loads(lines[1]);target=actual[0]['href'];other=actual[1]['href']
        with r.sync_playwright() as pw:
            browser=pw.firefox.launch(headless=True);page=browser.new_page()
            page.set_content('<a id="pdf" aria-disabled="true">View PDF</a><a id="dup">View PDF</a><a id="ref">View PDF</a>')
            page.evaluate('([target,other])=>{document.querySelector("#ref").href=other;setTimeout(()=>{let e=document.querySelector("#pdf");e.href=target;e.removeAttribute("aria-disabled");document.querySelector("#dup").href=target},500)}',[target,other])
            result=native_source.wait_pdf_links(page,target.rsplit('/',1)[0],timeout=3000)
            self.assertEqual([x['url'] for x in result['links']],[target]);self.assertFalse(result['pending'])
            page.set_content('<a aria-disabled="true">View PDF</a>')
            self.assertTrue(native_source.wait_pdf_links(page,target.rsplit('/',1)[0],timeout=100)['pending'])
            browser.close()
    def test_actual_sciencedirect_byline_without_author_meta(self):
        import json
        x=json.loads((r.ROOT/'results/VER-22d09f2a0e9222a1ac184678.json').read_text(encoding='utf-8'))
        a=next(a for a in x['evidence'] if a.get('kind')=='publisher-metadata')
        meta=json.loads((r.BASE/a['path']).read_text(encoding='utf-8'))
        body=json.loads((r.BASE/'intake/kudos-recovery/g08/VER-22d09f2a0e9222a1ac184678/firefox-source-links-b9d1c06c1e708311.json').read_text(encoding='utf-8'))['text']
        self.assertEqual(native_source.observed_byline(meta,body),'Peter Tolksdorf ∗')
        self.assertTrue(native_source.provider_identity(x['metadata'],meta,body,'https://www.sciencedirect.com'))
        changed=[dict(v,value='10.1016/other') if v['name']=='citation_doi' else v for v in meta]
        self.assertFalse(native_source.provider_identity(x['metadata'],changed,body,'https://www.sciencedirect.com'))
        wrong=body.replace('Peter Tolksdorf','Other Author')+'\nCited by Peter Tolksdorf'
        self.assertFalse(native_source.provider_identity(x['metadata'],meta,wrong,'https://www.sciencedirect.com'))
    def test_actual_provider_mathml_is_preserved(self):
        source=(r.BASE/'intake/kudos-recovery/g05/VER-44b62514b8f18a8d525b1228/firefox-abstract-original.html').read_text(encoding='utf-8')
        value=native_source.abstract_html(source,'Target')
        self.assertEqual(value.count('<msup'),source.count('<msup'))
        self.assertEqual(value.count('<msub'),source.count('<msub'))
        self.assertIn('charset="utf-8"',value)

    def test_native_browser_body_timeout_is_observation_not_zero_results(self):
        from unittest.mock import Mock
        from playwright.sync_api import TimeoutError
        page=Mock();page.goto.side_effect=TimeoutError('timeout');page.locator.return_value.inner_text.return_value='Are you a robot?'
        body,timed_out=native_source.visit_body(page,'https://www.sciencedirect.com/science/article/pii/observed')
        self.assertTrue(timed_out);self.assertIn('robot',body)

if __name__=='__main__':unittest.main()
