import sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

class SupplementContract(unittest.TestCase):
    def test_degruyter_native_attachment_retains_its_document_doi(self):
        from supplements import degruyter_links
        raw=(ROOT/'tests/fixtures/degruyter-supplement-region.html').read_text('utf-8')
        rows=degruyter_links(raw,'https://www.degruyterbrill.com/')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['filename'],'snde1089_supplementary_2.zip')
        self.assertEqual(rows[0]['linked_doi'],'10.2202/1558-3708.1089')
        self.assertEqual(rows[0]['label'],'Data and code (zip file)')

    def test_taylor_zip_and_table_csv_controls_keep_their_different_roles(self):
        from supplements import taylor_links
        raw=(ROOT/'tests/fixtures/taylor-supplement-region.html').read_text('utf-8')+(ROOT/'tests/fixtures/taylor-table-controls.html').read_text('utf-8')
        rows=taylor_links(raw,'https://www.tandfonline.com/')
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[0]['filename'],'ucgs_a_1349663_sm4648.zip')
        self.assertEqual([row['role'] for row in rows],['supplementary_file','article_table','article_table'])
        self.assertEqual([row['table_id'] for row in rows[1:]],['t0001','t0003'])
        self.assertTrue(all(row['linked_doi']=='10.1080/10618600.2017.1349663' for row in rows))

    def test_cambridge_native_table_keeps_two_files_with_the_same_title(self):
        from supplements import cambridge_links
        raw=(ROOT/'tests/fixtures/cambridge-supplement-region.html').read_text('utf-8')
        rows=cambridge_links(raw,'https://www-cambridge-org.libproxy.knu.ac.kr/')
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['label'],rows[1]['label'])
        self.assertTrue(rows[0]['filename'].endswith('sup001.pdf'))
        self.assertTrue(rows[1]['filename'].endswith('sup002.zip'))
        self.assertEqual(rows[0]['linked_pii'],'S0033312300006608')

    def test_oxford_uses_attachment_widget_and_retains_embedded_doi(self):
        from supplements import oxford_links
        raw=(ROOT/'tests/fixtures/oxford-supplement-region.html').read_text('utf-8')
        rows=oxford_links(raw+'<a href="https://other.example/file.pdf">Other paper</a>','https://academic.oup.com/')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['linked_doi_path'],'10.1093_restud_rdag022')
        self.assertEqual(rows[0]['filename'],'rdag022_supplementary_data.pdf')

    def test_cambridge_attachment_with_a_different_pii_is_not_downloaded(self):
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        from scholarly import ArtifactStore
        from supplements import fetch_supplementary
        raw='<meta name="citation_pdf_url" content="https://www.cambridge.org/content/S9999999999999999a.pdf/paper.pdf">'+(ROOT/'tests/fixtures/cambridge-supplement-region.html').read_text('utf-8')
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp); source=store.put(raw,'text/html','cambridge','https://www.cambridge.org/')
            adapter=SimpleNamespace(store=store,source='cambridge',gateway=SimpleNamespace(context=None),profile=SimpleNamespace(download_hosts={'static.cambridge.org'}))
            page=SimpleNamespace(url='https://www.cambridge.org/',content=Mock(return_value=raw))
            with patch('supplements.browser_download') as download:
                result=fetch_supplementary(adapter,page,'10.1007/s11336-020-09720-7',source)
            download.assert_not_called()
            self.assertEqual(result['received'],0)
            self.assertTrue(all(x['status']=='selection_required' for x in result['files']))

    def test_aip_supplement_reference_stays_with_explicit_figshare_source(self):
        from supplements import aip_links
        raw=(ROOT/'tests/fixtures/aip-supplement-region.html').read_text('utf-8')
        rows=aip_links(raw,'https://pubs-aip-org.libproxy.knu.ac.kr/')
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['source'],'figshare')
        self.assertEqual(rows[0]['target'],'10.60893/figshare.aip.c.7956296')
        self.assertEqual(rows[0]['status'],'selection_required')

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
