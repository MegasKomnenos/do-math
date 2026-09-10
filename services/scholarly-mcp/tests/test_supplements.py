import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class SupplementContract(unittest.TestCase):
    def test_wiley_table_preserves_native_filename_description_and_doi(self):
        from supplements import wiley_links
        raw=(ROOT/'tests/fixtures/wiley-supplement-table.html').read_text('utf-8')
        rows=wiley_links(raw,'https://onlinelibrary-wiley-com.libproxy.knu.ac.kr/')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['filename'],'rsa70063-sup-0001-Supinfo.zip')
        self.assertEqual(rows[0]['linked_doi'],'10.1002/rsa.70063')
        self.assertEqual(rows[0]['description'],'Data S1.')

    def test_later_download_failure_preserves_the_successful_attachment(self):
        import pymupdf
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore,ServiceError
        from supplements import springer_links,fetch_supplementary
        raw=(ROOT/'tests/fixtures/nature-supplement-region.html').read_text('utf-8')
        base='https://www.nature.com/articles/s41467-023-41217-6'
        links=springer_links(raw,base)
        with pymupdf.open() as pdf:
            pdf.new_page()
            data=pdf.tobytes()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp)
            source=store.put(raw,'text/html','springer',base)
            adapter=SimpleNamespace(store=store,source='springer',gateway=SimpleNamespace(context=None),profile=SimpleNamespace(download_hosts={'media.springernature.com'}))
            page=SimpleNamespace(url=base,content=Mock(return_value=raw))
            with patch('supplements.browser_download',side_effect=[(data,'application/pdf',links[0]['url']),ServiceError('access_restricted','Restricted',status='restricted')]):
                result=fetch_supplementary(adapter,page,'10.1038/s41467-023-41217-6',source)
            self.assertEqual((result['status'],result['discovered'],result['received']),('partial',2,1))
            self.assertEqual(store.read(result['files'][0]['artifact']['ref'])[1],data)
            self.assertEqual(result['files'][1]['status'],'restricted')

    def test_document_attachment_controls_keep_their_labels_and_doi(self):
        from supplements import springer_links
        raw=(ROOT/'tests/fixtures/nature-supplement-region.html').read_text('utf-8')
        rows=springer_links(raw,'https://www.nature.com/articles/s41467-023-41217-6')
        self.assertEqual(len(rows),2)
        self.assertIn('Supplementary Information',rows[0]['label'])
        self.assertIn('Peer Review File',rows[1]['label'])
        self.assertTrue(all(row['linked_doi']=='10.1038/s41467-023-41217-6' for row in rows))
        extra='<a href="https://other.example/unrelated.pdf">Unrelated PDF</a>'
        self.assertEqual(springer_links(raw+extra,'https://www.nature.com/'),rows)

if __name__=='__main__':
    unittest.main()
