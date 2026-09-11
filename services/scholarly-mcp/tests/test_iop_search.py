import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

class IOPSearchContract(unittest.TestCase):
    def test_reported_zero_results_are_distinct_from_an_unreadable_page(self):
        from iop_search import search_records,applied_filters
        from bs4 import BeautifulSoup
        from scholarly import ServiceError
        result=search_records((ROOT/'tests/fixtures/iop-empty.html').read_text('utf-8'),'https://iopscience.iop.org/nsearch')
        self.assertEqual((result['rows'],result['total'],result['accessible_total']),([],0,0))
        self.assertEqual(applied_filters(BeautifulSoup((ROOT/'tests/fixtures/iop-empty.html').read_text('utf-8'),'html.parser'))['searchDatePeriod'],{'anytime'})
        with self.assertRaises(ServiceError):search_records('<html><h1>Service unavailable</h1></html>','https://iopscience.iop.org/nsearch')

    def test_name_lookup_requests_relevance_instead_of_recent_citing_papers(self):
        from publishers import Publisher,PROFILES
        from unittest.mock import Mock
        adapter=Publisher(None,None,next(p for p in PROFILES if p.source=='iop'))
        adapter.search=Mock(return_value={'status':'ok','received':1,'records':{'ref':'candidate'}})
        result=adapter.fetch('Hydrodynamical simulation of the electric wind',parts=['metadata'])
        self.assertEqual(result['status'],'selection_required')
        self.assertEqual(adapter.search.call_args.kwargs['options'],{'sort':'relevance'})

    def test_api_failure_does_not_switch_to_ranked_browser_search(self):
        from iop_search import search
        from scholarly import ServiceError
        from unittest.mock import Mock,patch
        from types import SimpleNamespace
        adapter=SimpleNamespace(_rss_api=SimpleNamespace(search=Mock(side_effect=ServiceError('rate_limited','Retry later'))))
        with patch('iop_search.web_search') as browser,self.assertRaises(ServiceError):
            search(adapter,'complexity',options={})
        browser.assert_not_called()

    def test_capped_window_is_not_a_global_match_count_or_link_count(self):
        from iop_search import search_records
        raw=(ROOT/'tests/fixtures/iop-search.html').read_text('utf-8')
        result=search_records(raw,'https://iopscience.iop.org/nsearch')
        self.assertEqual((result['start'],result['accessible_total'],len(result['rows'])),(0,500,10))
        self.assertIsNone(result['total'])
        self.assertEqual(result['source_window_limit'],500)
        self.assertEqual(result['rows'][0]['doi'],'10.1088/1742-6596/1980/1/012017')
        self.assertEqual(result['rows'][0]['title'],'Entropy-based economic complexity of China trade flows')

    def test_missing_native_card_is_rejected(self):
        from iop_search import search_records
        from scholarly import ServiceError
        from bs4 import BeautifulSoup
        soup=BeautifulSoup((ROOT/'tests/fixtures/iop-search.html').read_text('utf-8'),'html.parser')
        soup.select_one('.art-list-item').decompose()
        with self.assertRaises(ServiceError) as error:search_records(str(soup),'https://iopscience.iop.org/nsearch')
        self.assertEqual(error.exception.result['code'],'range_mismatch')

if __name__=='__main__':unittest.main()
