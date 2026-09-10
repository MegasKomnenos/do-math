import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class EuclidContract(unittest.TestCase):
    def test_native_endnote_retains_provider_doi_tag(self):
        from scholarly import bibliography
        rows=bibliography((ROOT/'tests/fixtures/euclid.enw').read_bytes(),'application/x-endnote-refer')
        self.assertEqual(rows[0]['fields']['DOI'],['10.1214/10-AOS798'])
        self.assertEqual(len(rows[0]['fields']['A']),2)

    def test_native_advanced_zero_is_not_a_loading_screen(self):
        from euclid import records
        from scholarly import ServiceError
        from bs4 import BeautifulSoup
        raw=(ROOT/'tests/fixtures/euclid-empty.html').read_text('utf-8')
        self.assertEqual(records(raw,'https://projecteuclid.org/search'),([],0,0))
        soup=BeautifulSoup(raw,'html.parser')
        soup.select_one('#searchHeaderTotalResults').clear()
        with self.assertRaises(ServiceError):
            records(str(soup),'https://projecteuclid.org/search')

    def test_visible_page_is_not_replaced_with_prefetched_next_page(self):
        from euclid import records
        raw=(ROOT/'tests/fixtures/euclid-search.html').read_text('utf-8')
        rows,total,first=records(raw,'https://projecteuclid.org/search?term=complexity')
        self.assertEqual((len(rows),total,first),(25,7662,0))
        self.assertEqual(rows[0]['doi'],'10.11650/tjm.18.2014.3904')
        self.assertEqual(rows[0]['title'],'TWO COMPLEX COMBINATIONS AND COMPLEX INTERSECTION BODIES')
        self.assertIn('dual Brunn-Minkowski',rows[0]['abstract_html'])

if __name__=='__main__':
    unittest.main()
