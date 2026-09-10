from pathlib import Path
import sys,io,tempfile,unittest
from datetime import datetime
from openpyxl import Workbook
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,extract_artifact

MIME='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

class SpreadsheetContract(unittest.TestCase):
    def test_wos_native_xls_preserves_title_doi_and_accession_columns(self):
        raw=(ROOT/'tests/fixtures/wos-excel.xls').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put(raw,'application/vnd.ms-excel','wos','https://www.webofscience.com/')
            result=extract_artifact(store,artifact['ref'],start=1,count=1,fields=['I','BE','BS'])
            self.assertEqual(result['total'],2)
            row=result['items'][0]['values']
            self.assertEqual(row['BS'],'WOS:000269418800023')
            self.assertEqual(row['BE'],'10.1145/1562164.1562186')
            self.assertIn('P versus NP',row['I'])

    def test_public_title_list_is_not_misclassified_as_xml_and_requires_sheet_selection(self):
        raw=(ROOT/'tests/fixtures/kudos-acm-titles.xlsx').read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put(raw,MIME,'kudos-title-list','https://kudos.knu.ac.kr/')
            self.assertEqual(store.read(artifact['ref'])[1],raw)
            choice=extract_artifact(store,artifact['ref'])
            self.assertEqual(choice['status'],'selection_required')
            self.assertEqual([s['name'] for s in choice['sheets']],['Journal','Proceedings','Co-Publishing'])
            rows=extract_artifact(store,artifact['ref'],selection='Journal',count=3,fields=['A','B'])
            self.assertEqual(rows['returned'],3)
            self.assertEqual(rows['total'],178)
            self.assertEqual(rows['items'][0]['row'],1)
            self.assertTrue(all(set(row['values']) <= {'A','B'} for row in rows['items']))

    def test_formulas_are_text_and_number_formats_remain_available(self):
        workbook=Workbook()
        sheet=workbook.active
        sheet.append([1,'=1+1',datetime(2026,9,10)])
        sheet['A1'].number_format='0000'
        buffer=io.BytesIO()
        workbook.save(buffer)
        workbook.close()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put(buffer.getvalue(),MIME,'test','https://example.org/workbook.xlsx')
            result=extract_artifact(store,artifact['ref'],count=1)
            row=result['items'][0]
            self.assertEqual(row['values']['B'],'=1+1')
            self.assertEqual(row['formula_columns'],['B'])
            self.assertEqual(row['number_formats']['A'],'0000')
            self.assertEqual(row['values']['C'],'2026-09-10T00:00:00')
            self.assertEqual(row['cell_types']['C'],'d')

if __name__=='__main__':
    unittest.main()
