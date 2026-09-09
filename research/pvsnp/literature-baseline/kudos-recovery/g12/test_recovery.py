import hashlib
import json
from pathlib import Path
import unittest
import recovery
import resume

BASE = Path(__file__).resolve().parents[2]
RAW = BASE / 'intake/kudos-recovery/g12'
PDF = BASE / 'originals/paper-summary/03e45d574d66af5430fc846a6be99778811758dc2668cc44bd9a4f7920daa957.pdf'

class RecoveryTests(unittest.TestCase):
    def test_observed_author_preprint_link_and_distinct_date(self):
        html = (RAW / 'ad091b3d29060d86e8c09fcb61c8d8335cc21bf395d7c650ebf6153e4e360419.html').read_text()
        result = recovery.author_record(html)
        self.assertIsNotNone(result)
        self.assertEqual(result['year'], None)
        self.assertEqual(result['related_publication']['year'], 1992)
        self.assertEqual(result['related_publication']['pages'], '59-75')
        self.assertEqual(result['pdf_url'], 'https://www.ms.u-tokyo.ac.jp/~toshi/texpdf/19-pro-ceed-preprint.pdf')

    def test_real_26_page_pdf_and_no_invented_abstract(self):
        result = recovery.inspect_pdf(PDF.read_bytes())
        self.assertEqual(result['pages'], 26)
        self.assertTrue(result['target_preprint'])
        self.assertFalse(result['has_abstract_heading'])
        self.assertIn('Question A-0.', result['first_page'])

    def test_login_html_is_not_pdf(self):
        html = (RAW / 'ad091b3d29060d86e8c09fcb61c8d8335cc21bf395d7c650ebf6153e4e360419.html').read_bytes()
        self.assertFalse(recovery.inspect_pdf(html)['target_preprint'])

    def test_real_expanded_records_do_not_supply_preprint_abstract(self):
        d = json.loads((RAW / '74141006ec075e5ae09e4f8165f35631af6739bd09c4f0f21f95bc3f6e8f441d.json').read_text())
        self.assertEqual(d['record_count'], 8)
        self.assertIn('s.ho=f', d['query']['query_string'])
        decisions = recovery.assess_search(d)
        self.assertEqual(len(decisions), 8)
        self.assertEqual(sum(x['same_title'] for x in decisions), 7)
        self.assertFalse(any(x['preprint_abstract'] for x in decisions))
        self.assertEqual(decisions[-1]['reason'], 'Different title; book table of contents is not this preprint abstract.')

    def test_real_near_title_and_different_author_are_rejected(self):
        d = json.loads((RAW / '1e2f1bfbc5848a6817d959495098a50b2b12671e053715d54c1687a948b0fdba.json').read_text())
        decisions = recovery.assess_search(d)
        self.assertEqual(len(decisions), 7)
        self.assertFalse(any(x['same_title'] for x in decisions))

    def test_empty_search_is_not_unvisited_search(self):
        # Structural boundary fixture derived from the observed response schema.
        self.assertEqual(recovery.assess_search({'record_count':0, 'documents':[]}), [])
        with self.assertRaises(ValueError):
            recovery.assess_search({'record_count':8, 'documents':[]})

    def test_safe_projection_drops_openurl_and_unknown_fields(self):
        d={'record_count':0,'page_count':0,'query':{'original_query':'q','query_string':'s.ho=f'},'documents':[], 'private_field':'synthetic'}
        self.assertNotIn('private_field', recovery.safe_search(d))

    def test_no_completion_before_direct_review(self):
        self.assertEqual(resume.review_status(None), 'unresolved')
        self.assertEqual(resume.review_status({'abstract':{'status':'not_found','reason':'Observed PDF and complete DB scope','scope_complete':True}}), 'not_found')

    def test_stale_or_invalid_saved_result_is_reopened(self):
        self.assertFalse(resume.can_reuse({'identity':{'status':'confirmed'}}))

    def test_changed_source_does_not_inherit_direct_review(self):
        current={'evidence':[{'path':'source.pdf','sha256':'new','kind':'pdf-inspection'}]}
        old={'reviewed_sources':{'source.pdf':'old'}}
        self.assertFalse(resume.review_matches(current,old))
        old['reviewed_sources']['source.pdf']='new'
        self.assertTrue(resume.review_matches(current,old))

    def test_different_article_is_not_called_a_book(self):
        d = json.loads((RAW / '1e2f1bfbc5848a6817d959495098a50b2b12671e053715d54c1687a948b0fdba.json').read_text())
        self.assertEqual(recovery.assess_search(d)[0]['reason'],'Different title and publication; not the registered preprint.')

    def test_saved_replay_reports_no_new_browser_requests(self):
        collected=json.loads((Path(__file__).parent/'collected.json').read_text())
        self.assertEqual(resume.replay_metrics(collected)['searches'],0)

if __name__ == '__main__':
    unittest.main()
