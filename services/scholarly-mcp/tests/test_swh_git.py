import io,json,sys,tarfile,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError
from api_adapters import SoftwareHeritage
REV='swh:1:rev:2db189928c94d62a3b4757b3eec68f0a4d4113f0'
SNP='swh:1:snp:1a8893e6a86f444e8be8e7bda6cb34fb1735a00e'

class SWHGitContract(unittest.TestCase):
    def test_release_with_native_missing_email_keeps_hash_verification_and_warning(self):
        from swh_git import verify_git_archive
        result=verify_git_archive((ROOT/'tests/fixtures/swh-git-release.tar').read_bytes(),'swh:1:rel:fc8e44c5bb3fabe81e5ebe46ac013a2510271616')
        self.assertTrue(result['verified'])
        self.assertIn('missingEmail',[w['code'] for w in result['warnings']])

    def test_history_uses_git_bare_job_and_retains_metadata(self):
        calls=[]
        def response(request):
            calls.append(request)
            if '/revision/' in request.url.path:return httpx.Response(200,json={'id':REV.split(':')[-1]})
            self.assertIn('/vault/git-bare/'+REV+'/',request.url.path)
            return httpx.Response(200,json={'swhid':REV,'status':'pending'})
        with tempfile.TemporaryDirectory() as temp:
            a=SoftwareHeritage(ArtifactStore(temp),httpx.Client(transport=httpx.MockTransport(response)))
            result=a.fetch(REV,parts=['metadata','history'])
            self.assertEqual(result['components']['metadata']['status'],'available')
            self.assertEqual(result['components']['history']['status'],'pending')
            self.assertEqual(result['components']['history']['retry']['parts'],['history'])

    def test_native_revision_bundle_contains_verified_history(self):
        from swh_git import verify_git_archive
        result=verify_git_archive((ROOT/'tests/fixtures/swh-git-revision.tar').read_bytes(),REV)
        self.assertTrue(result['verified'])
        self.assertEqual(result['objects'],349)
        self.assertGreater(result['commits'],1)
        self.assertEqual(result['refs']['refs/heads/master'],REV.split(':')[-1])

    def test_empty_snapshot_is_distinct_from_missing_branch_data(self):
        from swh_git import verify_git_archive
        data=(ROOT/'tests/fixtures/swh-git-empty-snapshot.tar').read_bytes()
        result=verify_git_archive(data,SNP,branches={})
        self.assertTrue(result['verified']);self.assertEqual(result['objects'],0)
        with self.assertRaises(ServiceError):verify_git_archive(data,SNP)

    def test_untrusted_archive_paths_and_corrupt_pack_are_rejected(self):
        from swh_git import verify_git_archive
        data=(ROOT/'tests/fixtures/swh-git-revision.tar').read_bytes()
        for escape in (True,False):
            stream=io.BytesIO()
            with tarfile.open(fileobj=io.BytesIO(data)) as original,tarfile.open(fileobj=stream,mode='w') as changed:
                for member in original:
                    payload=original.extractfile(member).read() if member.isfile() else None
                    if member.name.endswith('.pack'):
                        if escape:
                            member.name=REV+'.git/../outside.pack';member.pax_headers={}
                        else:payload=payload[:40]+bytes([payload[40]^1])+payload[41:]
                    changed.addfile(member,io.BytesIO(payload) if payload is not None else None)
            with self.subTest(escape=escape),self.assertRaises(ServiceError):verify_git_archive(stream.getvalue(),REV)

if __name__=='__main__':unittest.main()
