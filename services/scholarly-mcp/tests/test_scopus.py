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


if __name__ == "__main__":
    unittest.main()
