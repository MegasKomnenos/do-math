import json,unittest
from pathlib import Path
from playwright.sync_api import sync_playwright
from summon_collect import document_matches,ensure_scope,search,provider_candidate,clean
BASE=Path('C:/math/research/pvsnp/literature-baseline')

class SummonBindingTests(unittest.TestCase):
    def test_actual_cpe_is_provider_content_error_not_subscription_denial(self):
        import summon_collect
        body=(BASE/'intake/kudos-recovery/g05/service-probes/sciencedirect-entry.txt').read_text()
        self.assertIn('CPE00001',body)
        value=getattr(summon_collect,'restriction_reason',lambda marker:'Access/security restriction: '+marker)('CPE00001')
        self.assertIn('content-provision error',value)
        self.assertIn('cause unconfirmed',value)
    def test_actual_book_without_doi_matches_print_isbn_and_editor_names(self):
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-0c26fc7b79631b63b132fbae.json').read_text())
        response=next(json.loads((BASE/e['path']).read_text()) for e in reversed(r['evidence']) if e.get('kind')=='actual-ui-search-response')
        doc=next(d for d in response['documents'] if '9783031929311' in (d.get('isbns') or []) and d.get('abstracts'))
        paper=dict(r['metadata'],record_type='proceedings')
        self.assertTrue(document_matches(paper,doc))
        self.assertFalse(document_matches(paper,dict(doc,dois=['10.1007/other-edition'])))
    def test_explicit_remaining_query_is_not_replaced_by_doi(self):
        import summon_collect
        paper={'title':'Algorithms and Complexity','authors':[],'identifiers':{'doi':['10.1007/978-3-031-92932-8']}}
        fn=getattr(summon_collect,'query_terms',lambda paper,override:paper['identifiers']['doi'])
        self.assertEqual(fn(paper,['Algorithms and Complexity']),['Algorithms and Complexity'])
    def test_actual_later_title_variant_supplies_database_abstract(self):
        import summon_collect
        r=json.loads((BASE/'kudos-recovery/g05/results/VER-5e89856450ccdd4ba5209072.json').read_text())
        paper=dict(r['metadata'],record_type='article')
        response=json.loads((BASE/'intake/kudos-recovery/g05/VER-5e89856450ccdd4ba5209072/summon-response-0.json').read_text())
        self.assertTrue(document_matches(paper,response['documents'][2]))
        pick=getattr(summon_collect,'choose_document',lambda p,ds:next((d for d in ds if document_matches(p,d)),None))
        self.assertTrue(pick(paper,response['documents'])['abstracts'])
    def test_all_pages_consumed_when_target_is_not_first(self):
        import summon_collect
        from unittest.mock import patch
        first={'record_count':3,'documents':[{'title':'a'},{'title':'b'}]}
        second={'record_count':3,'documents':[{'title':'target'}]}
        fn=getattr(summon_collect,'search_pages',lambda page,term:iter([first]))
        with patch.object(summon_collect,'search',return_value=first),patch.object(summon_collect,'next_search_page',return_value=second):
            pages=list(fn(None,'target'))
        self.assertEqual(sum(len(x['documents']) for x in pages),3)
    def test_actual_title_query_highlights_preserve_identity(self):
        path=BASE/'intake/kudos-recovery/g05/VER-1e2c17b1bd6f486acf7bd65f/summon-response-1.json'
        response=json.loads(path.read_text())
        title=response['query']['original_query'];doc=response['documents'][0]
        self.assertIn('<mark>',doc['full_title'])
        self.assertEqual(clean(title),clean(doc['full_title']))
    def test_math_structure_not_erased_as_highlighting(self):
        power='<mml:msup><mml:mi>x</mml:mi><mml:mn>2</mml:mn></mml:msup>'
        self.assertNotEqual(clean(power),clean('x2'))
    def test_provider_field_cannot_override_visual_judgment(self):
        citation={'path':'intake/kudos-recovery/g05/VER-069990e1d9f45ad96cda8ed8/summon-abstract.txt'}
        result=provider_candidate({'status':'not_found','reason':'Printed Education Forum has no separate abstract'},citation)
        self.assertEqual(result['status'],'unresolved')
        self.assertIn('candidate_artifacts',result)
        existing={'status':'found','artifacts':[{'path':'verified.png'}],'extraction_quality':'source_region_verified'}
        kept=provider_candidate(existing,citation)
        self.assertEqual(kept['artifacts'],existing['artifacts'])
    def test_actual_response_identity_and_wrong_title(self):
        doc=json.loads((BASE/'intake/kudos-recovery/operator/summon-response-first.json').read_text())
        paper={'title':doc['title'],'year':2009,'authors':['Goebel, Rafal','Sanfelice, Ricardo G.','Teel, Andrew R.'],'record_type':'article','identifiers':{'doi':['10.1109/MCS.2008.931718']}}
        self.assertTrue(document_matches(paper,doc))
        self.assertFalse(document_matches(dict(paper,title='Different target'),doc))
        self.assertFalse(document_matches(dict(paper,year=1994,record_type='book'),doc))

class SummonLiveTests(unittest.TestCase):
    def test_actual_ui_next_page_keeps_query_and_scope(self):
        import summon_collect
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state='C:/math/.credentials/kudos-recovery/bootstrap.json');s=c.new_page();s.goto(summon_collect.SUMMON);ensure_scope(s)
            first=search(s,'computational complexity')
            follow=getattr(summon_collect,'next_search_page',lambda page,term:first)
            second=follow(s,'computational complexity')
            self.assertIn('pn=2',s.url)
            self.assertEqual(second['query']['original_query'],'computational complexity')
            self.assertNotEqual(first['documents'][0]['title'],second['documents'][0]['title'])
            self.assertIn('ho=f',s.url)
            b.close()
    def test_actual_ui_scope_query_and_full_abstract(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state='C:/math/.credentials/kudos-recovery/bootstrap.json');s=c.new_page();s.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=')
            ensure_scope(s)
            self.assertIn('ho=f',s.url)
            data=search(s,'10.1016/j.disopt.2023.100821')
            self.assertEqual(data.get('query',{}).get('original_query'),'10.1016/j.disopt.2023.100821')
            doc=data['documents'][0]
            self.assertEqual(doc['dois'],['10.1016/j.disopt.2023.100821'])
            s.locator('button[data-aid=quick-look-button]:visible').first.click()
            self.assertEqual(s.locator('.modal.quick-look [data-aid=abstract]').inner_text(),doc['abstracts'][0]['abstract'])
            s.keyboard.press('Escape')
            zero=search(s,'kudosg05zzzxqvvnoexistingpaper20260908')
            self.assertEqual(len(zero['documents']),0)
            self.assertIn('ho=f',s.url)
            b.close()

if __name__=='__main__':unittest.main()
