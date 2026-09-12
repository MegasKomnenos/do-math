import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from publishers import Publisher
from scholarly import ServiceError

class WileyAdvancedRows(unittest.TestCase):
    def test_more_than_three_total_rows_are_preserved_without_an_invented_cap(self):
        fields={'Anywhere':'AllField','Title':'Title','Author':'Contrib','Keywords':'Keyword'}
        options={'field':'Title','terms':[{'field':'Author','query':'A'},{'field':'Keywords','query':'B'},
            {'field':'Title','query':'C'},{'field':'Anywhere','query':'D'},{'field':'Author','query':'E'}]}
        self.assertEqual(Publisher.wiley_terms('algebra',options,fields),[
            {'field':'Title','query':'algebra'},{'field':'Author','query':'A'},{'field':'Keywords','query':'B'},
            {'field':'Title','query':'C'},{'field':'Anywhere','query':'D'},{'field':'Author','query':'E'}])

    def test_invalid_rows_are_rejected_before_browser_work(self):
        fields={'Anywhere':'AllField','Title':'Title'}
        for terms in ('bad',[{'field':'Unknown','query':'x'}],[{'field':'Title'}]):
            with self.subTest(terms=terms),self.assertRaises(ServiceError):
                Publisher.wiley_terms('algebra',{'field':'Title','terms':terms},fields)

if __name__=='__main__':unittest.main()
