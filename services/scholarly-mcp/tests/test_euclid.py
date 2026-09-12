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

    def test_extended_native_expression_uses_observed_field_and_operator_syntax(self):
        from euclid import native_clause,extend_native_query,retains_native_terms
        self.assertEqual(native_clause({'query':'complexity','field':'ALL'}),'(complexity)')
        self.assertEqual(native_clause({'query':'complexity','field':'TITLE'}),'TITLE:(complexity)')
        self.assertEqual(
            extend_native_query('(first)',[
                {'query':'second','field':'ABSTRACT','operator':'OR'},
                {'query':'third','field':'KEYWORDS','operator':'NOT'}]),
            '(first) OR ABSTRACT:(second) NOT KEYWORDS:(third)')
        terms=[{'query':'complexity','field':'ALL'},{'query':'complexity','field':'TITLE','operator':'OR'}]
        self.assertTrue(retains_native_terms('(complexity) OR TITLE:(complexity)',terms))
        self.assertFalse(retains_native_terms('(complexity)',terms))
        nested=[{'query':'(complexity)','field':'ALL'},{'query':'complexity','field':'ALL','operator':'AND'}]
        self.assertTrue(retains_native_terms('((complexity)) AND (complexity)',nested))
        wrong_operator=[{'query':'first','field':'ALL'},{'query':'complexity','field':'TITLE','operator':'AND'}]
        self.assertFalse(retains_native_terms('(first) OR TITLE:(complexity)',wrong_operator))
        mixed='((((((marker0) OR ABSTRACT:(marker1))  NOT AUTHORNAME:(marker2) AND AFFILIATION:(marker3))  OR DOI_ISSN_ISBN:(marker4))  NOT FIGURETABLECAPTIONS:(marker5) AND KEYWORDS:(marker6))  OR TITLE:(marker7) OR TITLE:(marker8))  NOT ABSTRACT:(marker9)'
        fields=('ALL','ABSTRACT','AUTHORNAME','AFFILIATION','DOI_ISSN_ISBN','FIGURETABLECAPTIONS','KEYWORDS','TITLE','TITLE','ABSTRACT')
        operators=('AND','OR','NOT','AND','OR','NOT','AND','OR','OR','NOT')
        self.assertTrue(retains_native_terms(mixed,[{'query':f'marker{i}','field':field,'operator':operators[i]} for i,field in enumerate(fields)]))

if __name__=='__main__':
    unittest.main()
