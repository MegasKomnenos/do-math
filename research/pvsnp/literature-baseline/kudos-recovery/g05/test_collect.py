import unittest
from collect import identity_matches, pdf_valid, completed, publisher_failure, click_pdf_link,artifact,BASE
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from acm_collect import pdf_abstract,pdf_identity,select_title_link
import json,pymupdf
from pathlib import Path

class RecoveryTests(unittest.TestCase):
    def test_actual_tex_named_accents_and_times_match_source_titles(self):
        import collect
        for prefix in ['1e93042f','626d333a','98360dc5','6f74eb']:
            r=json.loads(next((BASE/'kudos-recovery/g05/results').glob('VER-'+prefix+'*.json')).read_text())
            source=next(e for e in r['evidence'] if e.get('kind')=='actual-ui-search-response')
            documents=json.loads((BASE/source['path']).read_text())['documents']
            target=next(d for d in documents if set(d.get('dois',[])) & set(r['metadata']['identifiers']['doi']))
            self.assertEqual(collect.norm(r['metadata']['title']),collect.norm(target['title']),r['paper_id'])
        self.assertNotEqual(collect.norm(r'\vec{x}'),collect.norm('x'))

    def test_transient_windows_replace_failure_preserves_json_and_retries(self):
        import tempfile,collect
        from unittest.mock import patch
        original=Path.replace;calls=[]
        def replace_once(path,target):
            calls.append(path)
            if len(calls)==1:raise PermissionError('[WinError 5] observed result replacement failure')
            return original(path,target)
        with tempfile.TemporaryDirectory(dir=BASE/'kudos-recovery/g05/tdd') as folder:
            target=Path(folder)/'record.json';target.write_text('{"old":true}')
            with patch.object(Path,'replace',replace_once),patch.object(collect.time,'sleep'):
                collect.save_json(target,{'new':'preserved'})
            self.assertEqual(json.loads(target.read_text()),{'new':'preserved'});self.assertEqual(len(calls),2)

    def test_acm_title_tex_accent_matches_actual_unicode(self):
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-0c59f733300f1f570cd0ba5e.json').read_text())
        url='https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/2744447.2744451'
        self.assertIsNotNone(select_title_link(r['metadata'],[{'text':'Review of: A Walk Through Combinatorics by Miklós Bóna','url':url}]))
    def test_acm_same_title_reprint_does_not_hide_target_doi(self):
        paper={'title':'Characterizations of Pushdown Machines in Terms of Time-Bounded Computers','identifiers':{'doi':['10.1145/321623.321625']}}
        links=[{'text':paper['title'],'url':'https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/3588287.3588298'},{'text':paper['title'],'url':'https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/321623.321625'}]
        self.assertEqual(select_title_link(paper,links)['url'],links[1]['url'])
    def test_nonpdf_evidence_excludes_scripts_inputs_and_navigation(self):
        import collect
        raw=b'<html><script>secret_cookie_fixture</script><nav>account fixture</nav><main><h1>Target</h1><input value="private_fixture"><p>Get this Chapter</p></main></html>'
        value=getattr(collect,'nonpdf_body',lambda data:data.decode())(raw)
        self.assertIn('Get this Chapter',value)
        self.assertNotIn('secret_cookie_fixture',value)
        self.assertNotIn('private_fixture',value)
        self.assertNotIn('account fixture',value)
    def test_transient_download_response_obeys_retry_after(self):
        import collect
        waits=[]
        class Response:
            def __init__(self,status):self.status=status;self.headers={'retry-after':'2'}
        class Context:
            def __init__(self):self.calls=0;self.request=self
            def get(self,*a,**k):self.calls+=1;return Response(503 if self.calls==1 else 200)
        c=Context();fn=getattr(collect,'get_download',lambda c,url,wait:c.request.get(url))
        r=fn(c,'https://example.org/observed.pdf',wait=waits.append)
        self.assertEqual(r.status,200)
        self.assertEqual(waits,[2])
    def test_actual_acm_title_and_subtitle_links(self):
        url='https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/2902945.2902948'
        paper={'title':'Review of: The Nature of Computation by Cristopher Moore and Stephan Mertens'}
        links=[{'text':'Review of','url':url},{'text':': The Nature of Computation by Cristopher Moore and Stephan Mertens','url':url}]
        self.assertIsNotNone(select_title_link(paper,links))
        self.assertIsNone(select_title_link(paper,[dict(links[0]),dict(links[1],url=url+'-other')]))
    def test_known_ocr_keeps_raw_and_corrected_versions(self):
        r=json.loads(Path('research/pvsnp/literature-baseline/kudos-recovery/g05/results/VER-028dadfb49623dd97a98242c.json').read_text())
        self.assertEqual(r['abstract']['extraction_quality'],'visually_corrected')
        raw=(BASE/r['abstract']['raw_ocr_artifacts'][0]['path']).read_text()
        corrected=(BASE/r['abstract']['artifacts'][0]['path']).read_text()
        self.assertIn('dmgram',raw)
        self.assertNotIn('dmgram',corrected)
        self.assertIn('diagram',corrected)
    def test_changed_capture_preserves_old_evidence(self):
        import uuid
        pid='tdd-'+uuid.uuid4().hex
        old=artifact(pid,'capture.txt','first','https://example.org/source')
        new=artifact(pid,'capture.txt','second','https://example.org/source')
        self.assertEqual((BASE/old['path']).read_text(),'first')
        self.assertNotEqual(old['path'],new['path'])
    def test_pdf_reference_is_not_identity(self):
        paper={'title':'Noncommutative geometry','authors':['Connes, Alain'],'year':1994,'publication':{'pages':None}}
        self.assertFalse(pdf_identity(paper,'Other research paper\n2020\nReferences\nConnes, Alain. Noncommutative geometry. 1994.',47))
    def test_real_lee_pdf_identity(self):
        r=json.loads(Path('research/pvsnp/literature-baseline/kudos-recovery/g05/results/VER-028dadfb49623dd97a98242c.json').read_text())
        paper=dict(r['metadata'],publication={'pages':'604–618'})
        with pymupdf.open('research/pvsnp/literature-baseline/'+r['fulltext']['artifacts'][0]['path']) as d:
            self.assertTrue(pdf_identity(paper,d[0].get_text(),len(d)))
            self.assertFalse(pdf_identity(paper,d[0].get_text(),1))
    def test_real_pdf_abstract_boundary(self):
        text=Path('research/pvsnp/literature-baseline/intake/kudos-recovery/g05/VER-028dadfb49623dd97a98242c/pdf-first-pages.txt').read_text()
        value=pdf_abstract(text)
        self.assertIsNotNone(value)
        self.assertTrue(value.startswith('The Voronoi diagram'))
        self.assertTrue(value.endswith('constant factor.'))
        self.assertNotIn('KEY WORDS',value)
        self.assertIsNone(pdf_abstract('Title\nReferences\nAbstract algebra in computing\n1. Intro'))
    def test_publisher_timeout_is_retryable(self):
        failure=publisher_failure(PlaywrightTimeoutError('navigation timed out'))
        self.assertEqual(failure['status'],'unresolved')
    def test_second_pdf_link_is_clicked(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True)
            page=b.new_page()
            page.set_content('<a href="https://example.org/first.pdf" onclick="event.preventDefault();document.body.dataset.chosen=1">PDF</a><a href="https://example.org/second.pdf" onclick="event.preventDefault();document.body.dataset.chosen=2">Download PDF</a>')
            click_pdf_link(page,{'url':'https://example.org/second.pdf'})
            self.assertEqual(page.locator('body').get_attribute('data-chosen'),'2')
            b.close()
    def test_doi_case_and_target(self):
        paper={'title':'On polytopes with linear rank','identifiers':{'doi':['10.1016/j.disopt.2023.100821']}}
        self.assertTrue(identity_matches(paper,'On polytopes with linear rank\nDOI\n10.1016/J.DISOPT.2023.100821'))
        self.assertFalse(identity_matches(paper,'Different paper\nDOI\n10.1016/j.disopt.2023.100822'))
        self.assertFalse(identity_matches(paper,'On polytopes with linear rank\narXiv.org\n10/2021'))
    def test_login_html_not_pdf(self):
        self.assertFalse(pdf_valid(b'<html>Login</html>'))
        self.assertFalse(pdf_valid(b'%PDF- broken'))
    def test_resume_requires_resolved_record(self):
        self.assertFalse(completed({'identity':{'status':'unresolved'}}))
        self.assertFalse(completed({'identity':{'status':'confirmed'},'abstract':{'status':'found'},'fulltext':{'status':'unresolved'}}))
        self.assertTrue(completed({'identity':{'status':'confirmed'},'abstract':{'status':'found'},'fulltext':{'status':'unavailable'}}))

if __name__=='__main__': unittest.main()
