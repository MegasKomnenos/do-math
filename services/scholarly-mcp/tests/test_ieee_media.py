import json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError

class IEEEMediaContract(unittest.TestCase):
    def test_ranges_assemble_only_matching_bytes_and_version(self):
        from ieee_media import range_download
        payload=b'abcdefghijkl'; calls=[]
        def download(context,url,hosts,*,headers,response_info):
            start,end=map(int,headers['Range'][6:].split('-')); end=min(end,len(payload)-1)
            calls.append(headers)
            response_info.update(status=206,**{'content-range':f'bytes {start}-{end}/{len(payload)}','etag':'"version-1"'})
            return payload[start:end+1],'video/mp4',url
        with patch('ieee_media.browser_download',side_effect=download):
            data,media,url,details=range_download(None,'https://ieeexplore.ieee.org/video',(),chunk_size=5)
        self.assertEqual(data,payload);self.assertEqual(details['ranges'],3)
        self.assertEqual(calls[1]['If-Range'],'"version-1"')

    def test_changed_range_version_or_wrong_offset_is_rejected(self):
        from ieee_media import range_download
        for changed in ['version','offset']:
            def download(context,url,hosts,*,headers,response_info):
                start=int(headers['Range'][6:].split('-')[0])
                response_info.update(status=206,**{'content-range':f'bytes {0 if changed=="offset" else start}-{4 if changed=="offset" else start+4}/10',
                    'etag':'"new"' if changed=='version' and start else '"old"'})
                return b'abcde','video/mp4',url
            with patch('ieee_media.browser_download',side_effect=download),self.assertRaises(ServiceError):
                range_download(None,'https://ieeexplore.ieee.org/video',(),chunk_size=5)

    def test_date_validator_requires_separation_and_no_weak_etag(self):
        from ieee_media import range_validator
        headers={'last-modified':'Sat, 28 Feb 2026 19:04:33 GMT','date':'Thu, 10 Sep 2026 08:56:00 GMT'}
        self.assertEqual(range_validator(headers),('last-modified',headers['last-modified']))
        with self.assertRaises(ServiceError):range_validator({**headers,'etag':'W/"weak"'})
        with self.assertRaises(ServiceError):range_validator({**headers,'date':headers['last-modified']})

    def metadata(self):
        return json.loads((ROOT/'tests/fixtures/ieee-graphical-metadata.json').read_text('utf-8'))

    def test_document_json_identity_and_operational_fields(self):
        from ieee_media import document_metadata
        row=self.metadata();row['userInfo']={'token':'SYNTHETIC'}
        html='<script>xplGlobal.document.metadata='+json.dumps(row)+';</script>'
        result=document_metadata(html,'11259066')
        self.assertEqual(result['graphicalAbstract']['type'],'video'); self.assertNotIn('userInfo',result)
        with self.assertRaises(ServiceError): document_metadata(html,'42')

    def test_later_media_failure_keeps_the_successful_cover(self):
        from ieee_media import download_media
        row=self.metadata()
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp); proof=store.put(json.dumps(row),'application/json','ieee-xplore','https://ieeexplore.ieee.org/document/11259066/')
            adapter=SimpleNamespace(store=store,gateway=SimpleNamespace(context=None),hosts=('ieeexplore.ieee.org',),source='ieee-xplore')
            with patch('ieee_media.browser_download',side_effect=[(b'\xff\xd8\xffexample','image/jpeg','https://ieeexplore.ieee.org/cover.jpg'),ServiceError('timeout','Timeout')]):
                result=download_media(adapter,row,proof['url'],proof)
            self.assertEqual(result['status'],'partial'); self.assertEqual(result['received'],1)
            self.assertEqual(result['files'][0]['role'],'graphical_abstract_cover')
            self.assertEqual(result['files'][1]['code'],'timeout')

    def test_media_paths_must_belong_to_this_document(self):
        from ieee_media import download_media
        row=self.metadata(); row['graphicalAbstract']['coverImage']='/ielx8/1/2/42/graphical_abstract/cover.jpg'
        row['graphicalAbstract']['file']='https://other.example/video.mp4'
        with tempfile.TemporaryDirectory() as temp:
            store=ArtifactStore(temp); proof=store.put(json.dumps(row),'application/json','ieee-xplore','https://ieeexplore.ieee.org/document/11259066/')
            adapter=SimpleNamespace(store=store,gateway=SimpleNamespace(context=None),hosts=('ieeexplore.ieee.org',),source='ieee-xplore')
            with patch('ieee_media.browser_download') as download:
                result=download_media(adapter,row,proof['url'],proof)
            download.assert_not_called(); self.assertEqual(result['received'],0)
            self.assertTrue(all(f['code']=='source_boundary' for f in result['files']))

    def test_no_graphical_media_and_unimplemented_multimedia_are_distinct(self):
        from ieee_media import download_media
        row=self.metadata(); row.pop('graphicalAbstract')
        result=download_media(None,row,'https://ieeexplore.ieee.org/',{})
        self.assertEqual(result['status'],'not_found')
        row['sections']['multimedia']='true'
        result=download_media(None,row,'https://ieeexplore.ieee.org/',{})
        self.assertEqual(result['status'],'not_implemented')

if __name__=='__main__': unittest.main()
