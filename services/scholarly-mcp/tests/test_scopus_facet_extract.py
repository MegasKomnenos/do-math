import sys
import csv
import io
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,extract_artifact,ServiceError


class ScopusFacetExtraction(unittest.TestCase):
    def test_filtered_native_query_is_read_for_download_and_response_artifacts(self):
        data=(ROOT/'tests/fixtures/scopus-filter-counts.csv').read_text(encoding='utf-8-sig')
        rows=list(csv.reader(io.StringIO(data)));native='TITLE("P versus NP") AND ( LIMIT-TO ( DOCTYPE,"ar" ) )'
        rows[2]=['Your query : ('+native+')'];stream=io.StringIO();csv.writer(stream).writerows(rows)
        with tempfile.TemporaryDirectory() as folder:
            store=ArtifactStore(folder)
            for role in ('native_facet_counts','native_facet_counts_response'):
                artifact=store.put(stream.getvalue().encode(),'text/csv','scopus','https://www.scopus.com/gateway/document-facet-api/facets/export',
                    preserve_bytes=True,role=role,query='TITLE("P versus NP")',native_query=native)
                result=extract_artifact(store,artifact['ref'],start=5,count=1)
                self.assertEqual(result['total'],6)
                self.assertEqual(result['items'][0],{'facet_group':'FUNDING SPONSOR','label':'Deutsche Forschungsgemeinschaft','count':1})

    def test_paired_count_columns_are_preserved_after_the_native_preamble(self):
        data=(ROOT/'tests/fixtures/scopus-filter-counts.csv').read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            store=ArtifactStore(folder)
            artifact=store.put(data,'text/csv','scopus','https://www.scopus.com/gateway/document-facet-api/facets/export',
                preserve_bytes=True,role='native_facet_counts',query='TITLE("P versus NP")')
            result=extract_artifact(store,artifact['ref'],count=20)
            funding=[row for row in result['items'] if row.get('facet_group')=='FUNDING SPONSOR']
            self.assertEqual(funding,[{'facet_group':'FUNDING SPONSOR','label':'National Science Foundation','count':3},
                {'facet_group':'FUNDING SPONSOR','label':'Deutsche Forschungsgemeinschaft','count':1}])
            self.assertEqual(result['total'],6)
            raw=extract_artifact(store,artifact['ref'],selection='raw',count=2)
            self.assertEqual(raw['items'],data.decode('utf-8-sig').splitlines()[:2])
            self.assertEqual(store.read(artifact['ref'])[1],data)
            with self.assertRaises(ServiceError):extract_artifact(store,artifact['ref'],selection='guessed')


if __name__=='__main__':unittest.main()
