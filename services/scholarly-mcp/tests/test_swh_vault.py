import io,json,sys,tarfile,tempfile,unittest
import httpx
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ServiceError,ArtifactStore
from api_adapters import SoftwareHeritage

class SoftwareHeritageVault(unittest.TestCase):
    def test_release_cycles_and_wrong_revision_identity_keep_the_original_metadata(self):
        original=json.loads((ROOT/'tests/fixtures/swh-release-revision.json').read_text('utf-8'))
        revision=json.loads((ROOT/'tests/fixtures/swh-release-revision-target.json').read_text('utf-8'))
        for bad_release,bad_revision,code in [({**original,'target_type':'release','target':original['id']},revision,'release_cycle'),
                (original,{**revision,'id':'0'*40},'identity_mismatch')]:
            calls=[]
            def response(request):
                calls.append(request)
                return httpx.Response(200,json=bad_release if '/release/' in request.url.path else bad_revision)
            with tempfile.TemporaryDirectory() as temp:
                adapter=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
                result=adapter.fetch('swh:1:rel:'+original['id'],parts=['metadata','fulltext'])
                self.assertEqual(result['components']['metadata']['status'],'available')
                self.assertEqual(result['components']['fulltext']['code'],code)
                self.assertFalse(any('/vault/' in str(request.url) for request in calls))

    def test_native_releases_select_their_directory_or_revision_tree(self):
        for kind in ('directory','revision'):
            release=json.loads((ROOT/f'tests/fixtures/swh-release-{kind}.json').read_text('utf-8'))
            revision=json.loads((ROOT/'tests/fixtures/swh-release-revision-target.json').read_text('utf-8'))
            directory=release['target'] if kind=='directory' else revision['directory'];core='swh:1:rel:'+release['id'];calls=[]
            def response(request):
                calls.append(request)
                if request.url.path=='/api/1/release/'+release['id']+'/':return httpx.Response(200,json=release)
                if request.url.path=='/api/1/revision/'+revision['id']+'/':return httpx.Response(200,json=revision)
                if request.url.path=='/api/1/vault/flat/swh:1:dir:'+directory+'/':return httpx.Response(200,json={'swhid':'swh:1:dir:'+directory,'status':'pending'})
                raise AssertionError('Unexpected request')
            with tempfile.TemporaryDirectory() as temp:
                adapter=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
                result=adapter.fetch(core,parts=['metadata','fulltext'])
                self.assertEqual(result['components']['fulltext']['status'],'pending')
                self.assertEqual(result['archive_selection']['requested_swhid'],core)
                self.assertEqual(result['archive_selection']['directory_swhid'],'swh:1:dir:'+directory)
                self.assertEqual(len(result['archive_selection']['evidence']),1 if kind=='directory' else 2)
                self.assertEqual(result['components']['metadata']['status'],'available')

    def test_uncached_archive_is_prepared_without_email_and_keeps_metadata(self):
        core='swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904';calls=[]
        def response(request):
            calls.append(request)
            if '/directory/' in request.url.path:return httpx.Response(200,json=[])
            if request.method=='GET':return httpx.Response(404,json={'exception':'NotFoundExc'})
            return httpx.Response(200,json={'swhid':core,'status':'new'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=adapter.fetch(core,parts=['metadata','fulltext'])
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['components']['metadata']['status'],'available')
            self.assertEqual(result['components']['fulltext']['status'],'pending')
            self.assertEqual([r.method for r in calls],['GET','GET','POST'])
            self.assertEqual(json.loads(calls[-1].content),{})
            self.assertEqual(result['components']['fulltext']['retry']['target'],core)

    def test_wrong_job_or_download_identity_does_not_download(self):
        from software_heritage import vault_archive
        core='swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        jobs=[{'swhid':'swh:1:dir:'+'0'*40,'status':'done'},
              {'swhid':core,'status':'done','fetch_url':'https://archive.softwareheritage.org/api/1/vault/flat/swh:1:dir:'+'0'*40+'/raw/'}]
        for job in jobs:
            calls=[]
            def response(request):calls.append(request);return httpx.Response(200,json=job)
            with tempfile.TemporaryDirectory() as temp:
                adapter=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
                with self.assertRaises(ServiceError) as error:vault_archive(adapter,core)
                self.assertEqual(error.exception.result['code'],'archive_identity_mismatch')
                self.assertEqual(len(calls),1)

    def test_failed_integrity_keeps_original_archive_and_metadata(self):
        core='swh:1:dir:'+'0'*40
        data=(ROOT/'tests/fixtures/swh-empty-directory.tar.gz').read_bytes()
        def response(request):
            if '/directory/' in request.url.path:return httpx.Response(200,json=[])
            if request.url.path.endswith('/raw/'):return httpx.Response(200,content=data,headers={'content-type':'application/gzip'})
            return httpx.Response(200,json={'swhid':core,'status':'done','fetch_url':str(request.url)+'raw/'})
        with tempfile.TemporaryDirectory() as temp:
            adapter=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=adapter.fetch(core,parts=['metadata','fulltext'])
            self.assertEqual(result['status'],'partial')
            self.assertEqual(result['components']['metadata']['status'],'available')
            self.assertEqual(result['components']['fulltext']['code'],'archive_path_mismatch')
            self.assertEqual(adapter.store.read(result['components']['fulltext']['source_archive']['ref'])[1],data)

    def test_single_file_tree_matches_independent_git_hash(self):
        from software_heritage import verify_flat_archive
        # Independently obtained with git hash-object -t tree for this filename and known blob.
        core='swh:1:dir:a0e52c3df0ae637f5b38d3cb16f7fa0f7e41bbcb'
        data=(ROOT/'tests/fixtures/swh-simplefarm.ml').read_bytes();stream=io.BytesIO()
        with tarfile.open(fileobj=stream,mode='w:gz') as archive:
            member=tarfile.TarInfo(core+'/simplefarm.ml');member.size=len(data);member.mode=0o644
            archive.addfile(member,io.BytesIO(data))
        proof=verify_flat_archive(stream.getvalue(),core)
        self.assertTrue(proof['verified']);self.assertEqual(proof['files'],1)

    def test_empty_native_archive_matches_its_directory_swhid(self):
        from software_heritage import verify_flat_archive
        core='swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        proof=verify_flat_archive((ROOT/'tests/fixtures/swh-empty-directory.tar.gz').read_bytes(),core)
        self.assertTrue(proof['verified']);self.assertEqual(proof['files'],0)

    def test_file_changes_and_path_traversal_are_not_accepted(self):
        from software_heritage import verify_flat_archive
        core='swh:1:dir:4b825dc642cb6eb9a060e54bf8d69288fbee4904'
        for name in (core+'/file',core+'/../file'):
            stream=io.BytesIO()
            with tarfile.open(fileobj=stream,mode='w:gz') as archive:
                member=tarfile.TarInfo(name);member.size=3;member.mode=0o644;archive.addfile(member,io.BytesIO(b'abc'))
            with self.assertRaises(ServiceError):verify_flat_archive(stream.getvalue(),core)

    def test_download_allowlist_is_specific_to_the_observed_vault_container(self):
        adapter=SoftwareHeritage(None)
        self.assertTrue(adapter.allowed_url('https://swhvaultstorage.blob.core.windows.net/contents-uncompressed/blob?sig=SYNTHETIC'))
        self.assertFalse(adapter.allowed_url('https://swhvaultstorage.blob.core.windows.net/other-container/blob'))
        self.assertFalse(adapter.allowed_url('https://unrelated.blob.core.windows.net/contents-uncompressed/blob'))
        self.assertFalse(adapter.allowed_url('https://swhvaultstorage.blob.core.windows.net/contents-uncompressed/../other/blob'))

if __name__=='__main__':unittest.main()
