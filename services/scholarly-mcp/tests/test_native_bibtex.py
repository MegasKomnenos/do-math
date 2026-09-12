import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,bibliography,extract_artifact


class NativeBibTeXRecovery(unittest.TestCase):
    def test_keyless_source_fields_and_original_bytes_are_preserved(self):
        data=b'@phdthesis{\n title={An original, {nested} title},\n url={https://www.proquest.com/docview/1234},\n year={2026}\n}'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            artifact=store.put(data,'application/x-bibtex','pqdt','https://www.proquest.com/',preserve_bytes=True)
            result=extract_artifact(store,artifact['ref'],count=1)
            row=result['items'][0]
            self.assertEqual(row['id'],'')
            self.assertEqual(row['title'],'An original, {nested} title')
            self.assertEqual(row['url'],'https://www.proquest.com/docview/1234')
            self.assertIn('citation_key_missing',row['parse_warnings'])
            self.assertEqual(row['raw_text'].encode(),data)
            self.assertEqual(store.read(artifact['ref'])[1],data)

    def test_normal_equals_key_and_multiple_empty_keys_remain_distinct_records(self):
        data=b'@article{key=value,title={Normal}}\n@book{,title={First}}\n@book{,title="Second"}'
        rows=bibliography(data,'application/x-bibtex')
        self.assertEqual([row['id'] for row in rows],['key=value','',''])
        self.assertEqual([row['title'] for row in rows],['Normal','First','Second'])
        self.assertNotIn('citation_key_missing',rows[0]['parse_warnings'])


if __name__=='__main__':
    unittest.main()
