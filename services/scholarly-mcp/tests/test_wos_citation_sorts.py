import sys,unittest
from pathlib import Path
from unittest.mock import Mock
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from browser_adapters import WebOfScience
from scholarly import ServiceError

class WOSCitationSorts(unittest.TestCase):
    def test_citation_class_submenu_is_explicit(self):
        self.assertEqual(WebOfScience.citation_class_sorts,{'background-highest','basis-highest','support-highest','differ-highest','discuss-highest'})

    def test_citing_search_accepts_the_same_current_result_sorts(self):
        adapter=WebOfScience(None,None);adapter.search_citations=Mock(return_value={'status':'ok'})
        for sort in adapter.sorts:
            adapter.search('WOS:000269418800023',options={'kind':'citations','sort':sort},limit=1)
            self.assertEqual(adapter.search_citations.call_args.kwargs['sort'],sort)
        with self.assertRaises(ServiceError):adapter.search('WOS:000269418800023',options={'kind':'citations','sort':'invented'},limit=1)

if __name__=='__main__':unittest.main()
