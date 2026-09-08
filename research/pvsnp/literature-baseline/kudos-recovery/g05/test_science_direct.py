import html,importlib.util,json,re,unittest
from pathlib import Path
from collect import BASE,WORK
from playwright.sync_api import sync_playwright

class ScienceDirectTests(unittest.TestCase):
    def module(self):
        if importlib.util.find_spec('science_direct'):
            import science_direct
            return science_direct
        return None
    def test_actual_mathml_abstract_is_kept_as_readable_html(self):
        fragment=(BASE/'intake/kudos-recovery/g05/VER-44b62514b8f18a8d525b1228/firefox-abstract-original.html').read_text()
        module=self.module();value=module.abstract_html(fragment,'Target') if module else re.sub('<[^>]+>','',fragment)
        self.assertIn('<meta charset="utf-8">',value)
        self.assertEqual(value.count('<msup'),fragment.count('<msup'))
        self.assertIn('<msub',value)
    def test_actual_publisher_metadata_binding_and_wrong_doi(self):
        r=json.loads((WORK/'results/VER-44b62514b8f18a8d525b1228.json').read_text());meta={'citation_doi':['10.1016/j.tcs.2025.115540'],'citation_title':[r['metadata']['title']],'citation_publication_date':['2025/11/21'],'citation_online_date':['2025/09/03']}
        body=(BASE/'intake/kudos-recovery/g05/VER-44b62514b8f18a8d525b1228/firefox-public-abstract.txt').read_text()
        module=self.module();fn=module.publisher_identity if module else lambda *args:False
        self.assertTrue(fn(r['metadata'],meta,body))
        self.assertFalse(fn(r['metadata'],dict(meta,citation_doi=['10.1016/other']),body))
    def test_actual_captcha_is_an_access_notice_not_bibliographic_conflict(self):
        import science_direct
        body=(BASE/'intake/kudos-recovery/g05/VER-3b82bf030dc937915b35b0be/native-publisher.txt').read_text()
        fn=getattr(science_direct,'access_notice',lambda text:False)
        self.assertTrue(fn(body))

    def test_navigation_timeout_preserves_actual_visible_body(self):
        import science_direct
        from playwright.sync_api import TimeoutError
        from unittest.mock import Mock
        page=Mock();page.goto.side_effect=TimeoutError('load event did not arrive');page.locator.return_value.inner_text.return_value='Are you a robot? captcha challenge'
        fn=getattr(science_direct,'visit_body',lambda page,url:('',False))
        body,timed_out=fn(page,'https://www.sciencedirect.com/science/article/pii/observed')
        self.assertTrue(timed_out);self.assertIn('captcha challenge',body)

    def test_native_source_step_uses_a_fresh_tab_after_challenge(self):
        import resume
        from unittest.mock import Mock
        context=Mock();page=Mock();fresh=Mock();context.new_page.return_value=fresh
        fn=getattr(resume,'fresh_source_page',lambda context,page:page)
        self.assertIs(fn(context,page),fresh);page.close.assert_called_once()

    def test_institutional_source_uses_observed_proxy_link_not_public_captcha_route(self):
        import science_direct
        r=json.loads((WORK/'results/VER-022f997d68492e3705be19c6.json').read_text())
        url=science_direct.source_url(r,r['metadata'],institutional=True)
        self.assertIn('www-sciencedirect-com.libproxy.knu.ac.kr/science/article/',url)
        self.assertIn(url,[e.get('url') for e in r['evidence']])

    def test_actual_pdf_anchor_without_href_is_a_clickable_control(self):
        import science_direct
        controls=json.loads((BASE/'intake/kudos-recovery/g05/VER-2bb97c857e10d1adb8a73f9a/native-pdf-controls.json').read_text())
        fn=getattr(science_direct,'is_pdf_control',lambda item:bool(item.get('href')))
        self.assertTrue(any(fn(x) for x in controls))

    def test_hydrated_pdf_links_exclude_other_cited_papers(self):
        import science_direct
        links=[{'text':'View PDF','url':'https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S0166218X22001809/pdfft'},{'text':'View PDF','url':'https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S0167506008708173/pdf'}]
        fn=getattr(science_direct,'matching_pdf_links',lambda links,url:links)
        self.assertEqual(fn(links,'https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S0166218X22001809'),links[:1])

    def test_actual_preparing_download_html_requires_browser_continuation(self):
        import science_direct
        body=(BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6/native-pdf-response.txt').read_text()
        fn=getattr(science_direct,'requires_browser_download',lambda text:False)
        self.assertTrue(fn(body))
        self.assertFalse(fn('Are you a robot? captcha challenge'))

    def test_resume_source_does_not_select_previous_pdf_response_as_article(self):
        import science_direct
        r=json.loads((WORK/'results/VER-0451eeaddb50df2ad5b626ed.json').read_text())
        url=science_direct.source_url(r,r['metadata'],institutional=True)
        self.assertTrue(url.endswith('/S1071579725001467'),url)

    def test_actual_empty_body_is_ui_retry_not_identity_conflict(self):
        import science_direct
        body=(BASE/'intake/kudos-recovery/g05/VER-022f997d68492e3705be19c6/native-publisher-e3b0c44298fc1c14.txt').read_text()
        fn=getattr(science_direct,'body_ready',lambda body:True)
        self.assertFalse(fn(body));self.assertFalse(fn('Loading...'))
        self.assertTrue(fn('Are you a robot? captcha challenge'))

    def test_html_task_routes_to_institutional_html_only_collection(self):
        import resume
        fn=getattr(resume,'native_mode',lambda key:(False,False))
        self.assertEqual(fn('sciencedirect-html'),(True,True))
        self.assertEqual(fn('sciencedirect-native'),(False,False))

    def test_html_route_waits_for_complete_capture_before_early_metadata_gate(self):
        import science_direct,native_article
        from unittest.mock import Mock,patch
        r=json.loads((WORK/'results/VER-0451eeaddb50df2ad5b626ed.json').read_text());paper=dict(r['metadata'],paper_id=r['paper_id'])
        page=Mock();page.url='https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S1071579725001467';page.context.browser.browser_type.name='firefox';page.locator.return_value.inner_text.return_value='Full text access. Article content is loading.';page.locator.return_value.evaluate_all.return_value=[]
        with patch.object(science_direct,'artifact',return_value={'path':'fixture','url':page.url}),patch.object(native_article,'capture',return_value={'status':'found','reason':'late DOM capture fixture'}) as capture:
            science_direct.collect(Mock(),page,paper,True,page.url,True)
        capture.assert_called_once()

    def test_requested_native_browser_engine_is_selected(self):
        import resume
        with sync_playwright() as pw:
            fn=getattr(resume,'browser_type',lambda pw,engine:pw.chromium)
            kind=fn(pw,'firefox');options={'headless':True}
            if kind.name=='chromium':options['channel']='chrome'
            browser=kind.launch(**options)
            try:self.assertEqual(browser.browser_type.name,'firefox')
            finally:browser.close()

if __name__=='__main__':unittest.main()
