import json
from pathlib import Path
import unittest
import fitz
import recover
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
BASE = ROOT.parents[1]
FIXTURE = BASE/'intake/kudos-recovery/g08/interface'
PAPER = json.loads((BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines()[0])

class RecoveryTests(unittest.TestCase):
    def test_actual_book_subtitle_with_same_isbn_year_and_author(self):
        import copy
        pid='VER-064f3fe56f66b7313daeda8d'
        paper=next(json.loads(line) for line in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines() if json.loads(line)['paper_id']==pid)
        record=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
        source=next(a for a in record['evidence'] if a.get('kind')=='ui-search-response' and json.loads((BASE/a['path']).read_text(encoding='utf-8'))['original_query']=='2705658491')
        payload=json.loads((BASE/source['path']).read_text(encoding='utf-8'))
        self.assertEqual(len(recover.response_documents(paper,payload)),1)
        for field,value in [('publication_years',['1998']),('authors',[{'fullname':'Other, Author'}]),('isbns',['0000000000']),('full_title','Different book')]:
            changed=copy.deepcopy(payload);changed['documents'][0][field]=value
            self.assertFalse(recover.response_documents(paper,changed),field)
    def test_actual_start_page_has_trailing_range_separator(self):
        paper=next(json.loads(line) for line in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines() if json.loads(line)['paper_id']=='VER-c446ea90e7b8e8a53781a3ad')
        payload=json.loads((BASE/'intake/kudos-recovery/g08/VER-c446ea90e7b8e8a53781a3ad/summon-response-25b369fc32080514.json').read_text(encoding='utf-8'))
        matched=recover.response_documents(paper,payload)
        self.assertTrue(matched)
        self.assertEqual(matched[0]['start_pages'],['321-'])
        for doc in payload['documents']:doc['start_pages']=['322-']
        self.assertFalse(recover.response_documents(paper,payload))
    def test_actual_toc_title_without_h1(self):
        html=(BASE/'intake/kudos-recovery/g08/VER-189e7df30665d9cc4ad3ad18/publisher-live-0cddb6401e4393fe.html').read_text(encoding='utf-8')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page();page.set_content(html)
            self.assertEqual(recover.publisher_title(page),'Maximizing the Spread of Influence through a Social Network')
            page.set_content('<meta name="citation_title" content="Unrelated metadata"><body>Access denied</body>')
            self.assertEqual(recover.publisher_title(page),'')
            browser.close()
    def test_retained_overbar_mathml_binds_without_erasing_closure(self):
        papers=[json.loads(x) for x in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines()]
        paper=next(p for p in papers if p['paper_id']=='VER-4867d9ceedd63f5b65239e41')
        record=json.loads((ROOT/'results'/f"{paper['paper_id']}.json").read_text(encoding='utf-8'))
        self.assertTrue(recover.bind_mr(paper,'MR1944572',record['identity']['observed_bibliography']))
        self.assertNotEqual(recover.normalize_title(r'Gal(\overline{\bf Q}_p/{\bf Q}_p)'),recover.normalize_title('Gal(Q_p/Q_p)'))

    def test_retained_registered_symbol_binds_matlab_book(self):
        papers=[json.loads(x) for x in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines()]
        paper=next(p for p in papers if p['paper_id']=='VER-83a98b47e2be1a937703d5da')
        record=json.loads((ROOT/'results'/f"{paper['paper_id']}.json").read_text(encoding='utf-8'))
        self.assertTrue(recover.bind_mr(paper,'MR2280154',record['identity']['observed_bibliography']))
    def test_tex_title_matches_printed_math(self):
        self.assertEqual(recover.normalize_title(PAPER['title']), recover.normalize_title('Higher algebraic K-theory. I'))
    def test_real_quillen_mr_binds_without_doi(self):
        text=(FIXTURE/'quillen-main.txt').read_text(encoding='utf-8')
        self.assertTrue(recover.bind_mr(PAPER,'MR0338129(49 #2895)',text))
    def test_wrong_mr_is_rejected_even_with_matching_title(self):
        self.assertFalse(recover.bind_mr(PAPER,'MR0325307',PAPER['title']+' Quillen 1973'))
    def test_login_and_zero_results_cannot_bind(self):
        for text in ['Login Username Password','No results found']:
            self.assertFalse(recover.bind_mr(PAPER,'',text))
    def test_signed_review_is_not_author_abstract(self):
        text=(FIXTURE/'quillen-main.txt').read_text(encoding='utf-8')
        self.assertIsNone(recover.abstract_from_review(text))
    def test_explicit_author_summary_boundary(self):
        self.assertEqual(recover.abstract_from_review('Summary: "We prove a theorem."\nReferences'), 'We prove a theorem.')
    def test_html_not_pdf(self):
        self.assertFalse(recover.valid_pdf(b'<html>Login to view PDF</html>'))
    def test_actual_pdf_opens(self):
        doc=fitz.open(); doc.new_page(); self.assertTrue(recover.valid_pdf(doc.tobytes()))
    def test_partial_record_must_resume(self):
        self.assertFalse(recover.can_resume({'identity':{'status':'confirmed'},'abstract':{'status':'unresolved'},'fulltext':{'status':'unavailable'}}))
    def test_finished_record_is_preserved(self):
        self.assertTrue(recover.can_resume({'identity':{'status':'confirmed'},'abstract':{'status':'not_found'},'fulltext':{'status':'unavailable'}}))
    def test_collector_entrypoint_exists(self):
        self.assertTrue(callable(getattr(recover,'collect',None)), 'Collector must expose the live Playwright collection flow')
    def test_real_dom_heading_contains_numeric_mr(self):
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page()
            page.set_content((FIXTURE/'quillen-main.html').read_text(encoding='utf-8'))
            self.assertIn('0338129',recover.read_heading(page))
            browser.close()
    def test_real_summon_abstract_without_metadata_tail(self):
        with sync_playwright() as p:
            browser=p.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page()
            page.set_content((FIXTURE/'summon-gorbunov.html').read_text(encoding='utf-8'))
            value=recover.summon_abstract(page)
            self.assertIsNotNone(value)
            self.assertTrue(value.startswith('In an attribute-based encryption'))
            self.assertTrue(value.endswith('under quantitatively better assumptions.'))
            browser.close()
    def test_wrong_connes_article_cannot_be_1994_book(self):
        paper={'title':'Noncommutative geometry','authors':['Connes, Alain'],'year':1994,'record_type':'book'}
        self.assertFalse(recover.publisher_identity(paper,'Spectral Truncations in Noncommutative Geometry and Operator Systems','Alain Connes; Walter D. van Suijlekom','2020','https://link.springer.com/article/10.1007/s00220-020-03825-x'))
    def test_same_title_wrong_year_is_rejected(self):
        self.assertFalse(recover.publisher_identity(PAPER,'Higher algebraic K-theory. I','Quillen, Daniel','2020','https://example.org/article'))
    def test_title_author_year_positive(self):
        self.assertTrue(recover.publisher_identity(PAPER,'Higher algebraic K-theory: I','Daniel Quillen','1973','https://link.springer.com/chapter/10.1007/BFb0067053'))
    def test_real_tex_author_accents(self):
        for tex,printed in [(r'\v Sujan','Šujan'),(r'Musta\c t\u a','Mustaţă'),(r'P\v aun','Pǎun')]:
            self.assertEqual(recover.normalize_title(tex),recover.normalize_title(printed))
    def test_real_greek_title(self):
        self.assertEqual(recover.normalize_title(r'W^{k,p(x)}(\Omega)'),recover.normalize_title('Wk,p(x)(Ω)'))
    def test_known_doi_is_searched_before_title(self):
        paper=dict(PAPER,identifiers={'doi':['10.1007/BFb0067053']})
        self.assertEqual(recover.first_query(paper),'10.1007/BFb0067053')
    def test_et_al_is_not_an_author_name(self):
        paper=dict(PAPER,authors=['Quillen, Daniel','et al.'])
        self.assertTrue(recover.publisher_identity(paper,'Higher algebraic K-theory: I','Daniel Quillen','1973','https://link.springer.com/chapter/10.1007/BFb0067053'))
    def test_actual_ui_response_matches_displayed_gorbunov(self):
        response=json.loads((FIXTURE/'summon-gorbunov-response.json').read_text(encoding='utf-8'))
        papers=[json.loads(x) for x in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines()]
        paper=next(p for p in papers if p['paper_id']=='VER-05eea17a72a07d16d806738b')
        docs=recover.response_documents(paper,response)
        self.assertTrue(docs)
        self.assertEqual(docs[0]['full_title'],'Attribute-based encryption for circuits')
        self.assertIn('under quantitatively better assumptions.',docs[0]['abstracts'][0]['abstract'])
    def test_online_year_is_not_silently_assigned_original_year(self):
        response=json.loads((FIXTURE/'summon-quillen-response.json').read_text(encoding='utf-8'))
        self.assertEqual(recover.response_documents(PAPER,response),[])
    def test_actual_quillen_subscription_preview_is_restriction(self):
        path=BASE/'intake/kudos-recovery/g08/VER-03ffef9bcb026605ecb23809/publisher-156068d1d347.txt'
        self.assertTrue(recover.publisher_restriction(path.read_text(encoding='utf-8')))
    def test_actual_polish_letter(self):
        self.assertEqual(recover.normalize_title(r'P\l oski'),recover.normalize_title('Płoski'))
    def test_actual_cyrillic_bibtex_romanization(self):
        self.assertEqual(recover.normalize_title(r'{\cyr Izmereniya v psikhologii: matematicheskie osnovy}'),recover.normalize_title('Измерения в психологии: математические основы'))
    def test_actual_editor_name_order(self):
        paper={'title':'Handbook of neuroimaging data analysis','authors':['ombao hernando','lindquist martin','thompson wesley','aston john'],'year':2017,'record_type':'book'}
        self.assertTrue(recover.publisher_identity(paper,paper['title'],'Hernando Ombao; Martin Lindquist; Wesley Thompson; John Aston','2017','https://example.org/book'))
    def test_mr_editorial_note_is_not_search_title(self):
        self.assertEqual(recover.plain_title('Algebraic surfaces [{MR}1060325 (91f:14029)]'),'Algebraic surfaces')
    def test_challenge_parameter_is_removed_from_record_url(self):
        self.assertEqual(recover.public_url('https://example.org/article?id=3971&__cf_chl_rt_tk=test-challenge'),'https://example.org/article?id=3971')
    def test_actual_ojs_galley_not_reference_books(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True); page=b.new_page()
            page.set_content((FIXTURE/'ojs-pdf-links.html').read_text(encoding='utf-8'))
            links=recover.pdf_links(page)
            self.assertEqual(len(links),1)
            self.assertIn('/article/view/3971/4645',links[0]['url'])
            b.close()
    def test_actual_ojs_viewer_download(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True); page=b.new_page()
            page.set_content((FIXTURE/'ojs-viewer-links.html').read_text(encoding='utf-8'))
            self.assertEqual(recover.viewer_download_link(page),'https://revistas.unitru.edu.pe/index.php/SSMM/en/article/download/3971/4645/15789')
            b.close()
    def test_actual_mathscinet_tex_quoted_summary(self):
        value=recover.abstract_from_review((FIXTURE/'liquid-summary.txt').read_text(encoding='utf-8'))
        self.assertIsNotNone(value)
        self.assertTrue(value.startswith('The Liquid Tensor Experiment is a project'))
        self.assertTrue(value.endswith('mathematical research.'))
    def test_publisher_description_is_not_abstract(self):
        self.assertIsNone(recover.abstract_from_review((FIXTURE/'publisher-description.txt').read_text(encoding='utf-8')))
    def test_actual_ojs_pdf_accent_encoding(self):
        self.assertEqual(recover.normalize_title('Mej´ıa Alem´an'),recover.normalize_title(r"Mej\'ia Aleman"))
    def test_shared_review_selects_requested_mr_section(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True); page=b.new_page()
            page.set_content((FIXTURE/'mathscinet-grouped-main.html').read_text(encoding='utf-8'))
            section=recover.article_scope(page,'MR1323150')
            self.assertEqual(section.locator('.bibliography').count(),1)
            self.assertIn('II. On completeness',section.locator('.bibliography').inner_text())
            b.close()
    def test_enabled_article_anchor_is_a_source_link(self):
        with sync_playwright() as p:
            b=p.chromium.launch(channel='chrome',headless=True); page=b.new_page()
            page.set_content((FIXTURE/'mathscinet-grouped-main.html').read_text(encoding='utf-8'))
            section=page.locator('div.article').nth(1)
            self.assertTrue(recover.article_link(section))
            b.close()
    def test_actual_remaining_bibtex_notation(self):
        cases=[(r'Raconte-moi\dots les invariants','Raconte-moi… les invariants'),(r'Borel\cprime','Borelʹ'),(r'2-\epsilon','2−ϵ'),(r'H\aa stad','Håstad'),(r'{\rm P}={\rm BPP}','P=BPP'),(r'\Gamma \sb{0}(m)','Γ0(m)'),(r'J\o rgensen','Jørgensen')]
        for tex,printed in cases:
            with self.subTest(tex=tex):
                self.assertEqual(recover.normalize_title(tex),recover.normalize_title(printed))
    def test_anonymous_record_can_bind_by_mr_title_year(self):
        papers=[json.loads(x) for x in (BASE/'catalog/abstract-format-partition/groups/08-needs-source-mathscinet-bibtex/members.jsonl').read_text(encoding='utf-8').splitlines()]
        paper=next(p for p in papers if p['paper_id']=='VER-5a63dd56e6687f1921651ac0')
        self.assertTrue(recover.bind_mr(paper,paper['publication']['source_record']['record_id'],"L systems problem book '75. Automata, languages, development, pp.347–350. North-Holland, 1976."))
    def test_actual_summon_highlight_is_not_part_of_title(self):
        self.assertEqual(recover.normalize_title('<mark>Progress in the theory of complex algebraic curves</mark>'),recover.normalize_title('Progress in the theory of complex algebraic curves'))

if __name__=='__main__':
    unittest.main()
