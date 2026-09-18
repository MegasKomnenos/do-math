import importlib
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class ScopusContract(unittest.TestCase):
    def test_current_publication_url_resolves_its_eid(self):
        from scopus import Scopus
        from unittest.mock import patch
        adapter=Scopus(None,None)
        with patch.object(adapter,'search',return_value={'total':0,'received':0}) as search:
            result=adapter.fetch('https://www.scopus.com/pages/publications/77957268169',parts=['metadata'])
        self.assertEqual(result['status'],'not_found')
        self.assertEqual(search.call_args.args[0],'EID(2-s2.0-77957268169)')

    def test_reference_range_keeps_unindexed_records(self):
        from scopus import reference_records
        from scholarly import ServiceError
        payload=json.loads((ROOT/'tests/fixtures/scopus-references.json').read_bytes())
        payload['items'][0].pop('eid',None)
        rows,total,offset=reference_records(payload)
        self.assertEqual((len(rows),total,offset),(10,47,0))
        self.assertEqual(rows[0],payload['items'][0])
        payload['items'].pop()
        with self.assertRaises(ServiceError):
            reference_records(payload)

    def test_primary_documents_are_not_confused_with_preprint_counts(self):
        self.assertTrue((ROOT / "scopus.py").exists(), "Scopus adapter is absent")
        mod = importlib.import_module("scopus")
        payload = json.loads((ROOT / "tests/fixtures/scopus-primary.json").read_text("utf-8"))
        records, total, offset = mod.scopus_records(payload)
        self.assertEqual(total, 21)
        self.assertEqual(offset, 0)
        self.assertEqual(len(records), 10)
        self.assertEqual(records[-1]["title"], "P versus NP and geometry")
        self.assertTrue(mod.primary_request({"query": 'TITLE("P versus NP")', "documentClassification": "primary"}, 'TITLE("P versus NP")'))
        self.assertFalse(mod.primary_request({"query": 'TITLE("P versus NP")', "documentClassification": "preprint"}, 'TITLE("P versus NP")'))

    def test_page_capacity_can_exceed_last_page_record_count(self):
        mod = importlib.import_module("scopus")
        payload = json.loads((ROOT / "tests/fixtures/scopus-single.json").read_text("utf-8"))
        rows, total, offset = mod.scopus_records(payload)
        self.assertEqual((len(rows), total, offset), (1, 1, 0))

    def test_primary_pages_reject_duplicate_eids_within_and_across_pages(self):
        from scopus import scopus_records,unique_primary_ids
        from scholarly import ServiceError
        payload=json.loads((ROOT/'tests/fixtures/scopus-primary.json').read_text('utf-8'));row=payload['items'][0]
        payload={'metadata':{'offset':0,'totalCount':2,'itemCount':2},'items':[row,{**row}]}
        with self.assertRaises(ServiceError):scopus_records(payload)
        rows,_,_=scopus_records(payload,check_unique=False);self.assertEqual(len(rows),2)
        with self.assertRaises(ServiceError):unique_primary_ids([{'eid':'2-s2.0-2'}],{'2-s2.0-2'})
        with self.assertRaises(ServiceError):unique_primary_ids(rows,{'2-s2.0-prior'})
        with self.assertRaises(ServiceError):unique_primary_ids([{'eid':'wrong'}])

    def test_a_rejected_query_ends_the_wait_instead_of_running_it_out(self):
        """질의가 거절되면 검색 응답은 영영 오지 않는다. 대기를 끝까지 쓰지 않고 거절을 보고한다."""
        from types import SimpleNamespace
        from scopus import require_accepted_query, search_settled
        from scholarly import ServiceError
        hosts = {'www.scopus.com'}
        host = 'https://www.scopus.com'
        def response(path, status, method='GET', body=None, media='application/json'):
            return SimpleNamespace(url=host + path, status=status, headers={'content-type': media},
                                   request=SimpleNamespace(method=method, post_data_json=body))
        rejected = response('/gateway/documents/search/parsequery', 400, 'POST', {'userQuery': 'Q'}, 'text/html; charset=UTF-8')
        accepted = response('/gateway/documents/search/parsequery', 200, 'POST', {'userQuery': 'Q'})
        primary = response('/gateway/documents/search', 200, 'POST', {'documentClassification': 'primary', 'query': 'Q'})
        preprint = response('/gateway/documents/search', 200, 'POST', {'documentClassification': 'preprint', 'query': 'Q'})
        other = response('/gateway/documents/search', 200, 'POST', {'documentClassification': 'primary', 'query': 'OTHER'})
        self.assertTrue(search_settled(hosts, 'Q', rejected))
        self.assertTrue(search_settled(hosts, 'Q', primary))
        self.assertFalse(search_settled(hosts, 'Q', accepted))
        self.assertFalse(search_settled(hosts, 'Q', preprint))
        self.assertFalse(search_settled(hosts, 'Q', other))
        self.assertFalse(search_settled({'elsewhere.example'}, 'Q', primary))
        self.assertIs(require_accepted_query('Q', primary), primary)
        with self.assertRaises(ServiceError) as raised:
            require_accepted_query('Q', rejected)
        self.assertEqual(raised.exception.result['code'], 'query_rejected')
        self.assertEqual(raised.exception.result['http_status'], 400)
        # 실측: 기관 프록시는 자기 HTML 오류 쪽을, Scopus는 JSON을 돌려준다. 막은 주체를 구별해야 호출자가 검색식 모양을 바꾼다.
        self.assertEqual(raised.exception.result['rejected_by'], 'institutional_proxy')
        own = response('/gateway/documents/search/parsequery', 400, 'POST', {'userQuery': 'Q'})
        with self.assertRaises(ServiceError) as raised:
            require_accepted_query('Q', own)
        self.assertEqual(raised.exception.result['rejected_by'], 'scopus')

    def test_a_new_search_forgets_the_previous_result_table_position(self):
        """실측: Scopus는 결과 표의 쪽·정렬을 sessionStorage의 primary_documents~activePage 등에 기억하고 다음 검색에 복원한다.
        쪽을 넘긴 검색 뒤의 검색은 offset 190 같은 옛 위치의 요청을 함께 보내 range_mismatch·query_mismatch로 실패했다."""
        from types import SimpleNamespace
        from scopus import forget_result_table_state
        storage={'primary_documents~activePage':'19','primary_documents~sort':'cp-f','primary_documents~pageSize':'10',
                 'document-search-results-page~is-advanced-query':'true','pendo_tabId':'x'}
        def evaluate(script,prefix):
            self.assertIn('sessionStorage',script)
            for key in [key for key in storage if key.startswith(prefix)]:del storage[key]
        forget_result_table_state(SimpleNamespace(evaluate=evaluate))
        self.assertEqual(sorted(storage),['document-search-results-page~is-advanced-query','pendo_tabId'])


if __name__ == "__main__":
    unittest.main()
