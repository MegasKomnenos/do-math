import importlib.util,json,re,unittest
from pathlib import Path
from collect import BASE,WORK
class LinkScopeTests(unittest.TestCase):
    def select(self,paper,url,links,**kw):
        if importlib.util.find_spec('link_scope'):
            from link_scope import select_downloads
            return select_downloads(paper,url,links,**kw)
        return [x for x in links if re.search('pdf|download',x.get('text','')+x.get('url',''),re.I)]
    def test_actual_references_and_perlego_pdf_slugs_are_not_downloads(self):
        cases=json.loads((WORK/'tdd/fixtures/actual-link-scope-cases.json').read_text())
        for case in cases:self.assertEqual(self.select(case['paper'],case['url'],case['links']),[],case['url'])
    def test_found_original_is_preserved_during_abstract_source_visit(self):
        import copy,summon_collect
        from unittest.mock import patch
        source=json.loads((WORK/'results/VER-028dadfb49623dd97a98242c.json').read_text());record=copy.deepcopy(source);record['abstract']={'status':'unresolved'};before=copy.deepcopy(record['fulltext']);calls=[]
        wrong=(BASE/'intake/kudos-recovery/g05/VER-014dd490736be8ba7793740c/pdf-pending.pdf').read_bytes();doi=source['metadata']['identifiers']['doi'][0]
        class Locator:
            def count(self):return 1
            def inner_text(self):return source['metadata']['title']
            def evaluate_all(self,code):return [{'text':'PDF','url':'https://example.org/doi/pdf/'+doi}]
            @property
            def first(self):return self
        class Page:
            url='https://example.org/doi/'+doi
            def goto(self,*a,**kw):pass
            def wait_for_timeout(self,*a):pass
            def locator(self,*a):return Locator()
            def title(self):return source['metadata']['title']
            def close(self):pass
        class Context:
            def new_page(self):return Page()
            @property
            def request(self):return self
            def get(self,url,**kw):
                calls.append(url)
                class Response:
                    status=200
                    def body(self):return wrong
                return Response()
        with patch.object(summon_collect,'artifact',side_effect=lambda pid,name,data,url,*a,**kw:{'path':name,'url':url}):
            summon_collect.publisher(Context(),record,dict(source['metadata'],paper_id=source['paper_id']),Page.url,'fixture')
        self.assertEqual(calls,[]);self.assertEqual(record['fulltext'],before)
    def test_actual_europepmc_global_directories_and_zip_are_excluded(self):
        from link_scope import classify
        for url in ['https://europepmc.org/ftp/pdf/','https://europepmc.org/ftp/pdf/PMCxxxx204/','https://europepmc.org/ftp/pdf/PMCxxxx204/PMC2039864.zip']:
            self.assertEqual(classify({'identifiers':{'doi':['10.1007/978-3-031-81217-0_5']}},'https://europepmc.org',{'text':'PDF','url':url})[0],'excluded',url)
    def test_explicit_reference_location_is_not_overridden_by_full_text_parameter(self):
        from link_scope import classify
        # Actual Wiley parameter pair reported in the Tsay source investigation.
        url='https://onlinelibrary.wiley.com/resolve?linkLocation=Reference&linkSource=FULL_TEXT'
        self.assertEqual(classify({},'https://onlinelibrary.wiley.com',{'text':'PDF','url':url})[0],'excluded')
    def test_actual_save_chapter_control_is_excluded(self):
        case=json.loads((WORK/'tdd/fixtures/actual-link-scope-cases.json').read_text())[0]
        controls=[x for x in case['links'] if x['text'].lower()=='save chapter']
        self.assertTrue(controls);self.assertEqual(self.select(case['paper'],case['url'],controls),[])
    def test_actual_whole_book_pdf_is_kept_without_front_matter_or_other_chapters(self):
        r=json.loads((WORK/'results/VER-0c26fc7b79631b63b132fbae.json').read_text())
        links=json.loads((BASE/'intake/kudos-recovery/g05/VER-0c26fc7b79631b63b132fbae/springer-download-links.json').read_text())
        chosen=self.select(r['metadata'],'https://link-springer-com.libproxy.knu.ac.kr/book/10.1007/978-3-031-92932-8',links)
        self.assertEqual(len(chosen),1);self.assertEqual(chosen[0]['url'],links[0]['url'])
    def test_actual_nips_paper_hash_binds_download_without_doi(self):
        r=json.loads((WORK/'results/VER-6ca41f512673a1b0643f9f14.json').read_text())
        asset=next(e for e in r['evidence'] if e['path'].endswith('/resume-fulltext.pdf'))
        source='https://proceedings.neurips.cc/paper/1990/hash/8dd48d6a2e2cad213179a3992c0be53c-Abstract.html'
        self.assertEqual(len(self.select(r['metadata'],source,[{'text':'Paper','url':asset['url']}],title_matches=True)),1)
    def test_reviewed_parent_book_link_is_kept_for_target_chapter_boundary_review(self):
        links=json.loads((BASE/'intake/kudos-recovery/g05/VER-0c26fc7b79631b63b132fbae/springer-download-links.json').read_text())
        child=next(x for x in links if x['url'].endswith('92932-8_1'));parent=links[0]
        paper={'paper_id':'actual-book-chapter-scope-fixture','identifiers':{'doi':['10.1007/978-3-031-92932-8_1']}}
        binding={'url':parent['url'],'target_paper_id':paper['paper_id'],'review_status':'verified','reason':'Actual bound book TOC lists this chapter DOI; whole book needs chapter boundary review.','evidence_paths':['intake/kudos-recovery/g05/VER-0c26fc7b79631b63b132fbae/springer-download-links.json']}
        chosen=self.select(paper,child['url'],[parent],reviewed_parents=[binding])
        self.assertEqual(len(chosen),1);self.assertEqual(chosen[0].get('scope_role'),'parent')
if __name__=='__main__':unittest.main()
