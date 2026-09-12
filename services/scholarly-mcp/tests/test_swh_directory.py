import hashlib,json,sys,tempfile,unittest
from pathlib import Path
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api_adapters import SoftwareHeritage
from scholarly import ArtifactStore,ServiceError

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def tree(rows):
    body=b''.join(format(row['perms'],'o').encode()+b' '+row['name'].encode('utf-8',errors='surrogateescape')+b'\0'+bytes.fromhex(row['target'])
        for row in sorted(rows,key=lambda r:r['name'].encode('utf-8',errors='surrogateescape')+(b'/' if r['type']=='dir' else b'')))
    return hashlib.sha1(b'tree '+str(len(body)).encode()+b'\0'+body).hexdigest()
def file(name,data,mode=0o100644):
    return {'name':name,'type':'file','target':blob(data),'perms':mode,'length':len(data),'checksums':{'sha1_git':blob(data)}}

class SWHDirectoryFiles(unittest.TestCase):
    def run_fetch(self,corrupt=False,wrong_directory=False,rate_limited=False,non_utf8=False,reopen=False):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup);store=ArtifactStore(folder.name)
        data=b'original source\n';link=b'../README';nested=[file('again',data),file('link',link,0o120000)]
        child=tree(nested);root_rows=[file('\udcff' if non_utf8 else 'README',data),{'name':'src','type':'dir','perms':0o40000,'target':child}]
        root=tree(root_rows);calls=[]
        def serve(request):
            calls.append(request.url.path)
            self.assertNotIn('authorization',request.headers)
            if '/vault/' in request.url.path:raise AssertionError('Direct files must not request or poll Vault')
            if '/directory/'+root+'/' in request.url.path:
                value=[{**root_rows[0],'name':'wrong'},root_rows[1]] if wrong_directory else root_rows
                return httpx.Response(200,content=json.dumps(value,ensure_ascii=True).encode(),headers={'Content-Type':'application/json'})
            if '/directory/'+child+'/' in request.url.path:return httpx.Response(200,json=nested)
            if rate_limited:return httpx.Response(429)
            raw=link if blob(link) in request.url.path else b'wrong' if corrupt else data
            return httpx.Response(200,content=raw,headers={'Content-Type':'application/octet-stream'})
        client=httpx.Client(transport=httpx.MockTransport(serve));self.addCleanup(client.close)
        adapter=SoftwareHeritage(store,client)
        try:result=adapter.fetch('swh:1:dir:'+root,parts=['metadata','files'])
        except ServiceError as error:return error.result,[],calls
        if reopen:
            count=len(calls)
            result=SoftwareHeritage(store,client).fetch('swh:1:dir:'+root,parts=['metadata','files'])
            self.assertEqual(len(calls),count,'Previously verified immutable objects were downloaded again')
        component=result['components']['files'];rows=json.loads(store.read(component['artifact']['ref'])[1])
        return component,rows,calls

    def test_pending_archive_does_not_prevent_direct_files_or_symlink_bytes(self):
        component,rows,calls=self.run_fetch()
        self.assertEqual(component['status'],'available');self.assertTrue(component['complete'])
        self.assertEqual(component['files'],2);self.assertEqual(component['symlinks'],1)
        self.assertEqual({row['path'] for row in rows},{'','README','src','src/again','src/link'})
        self.assertEqual(len(calls),4)
        self.assertEqual(next(row for row in rows if row['path']=='README')['artifact']['ref'],next(row for row in rows if row['path']=='src/again')['artifact']['ref'])

    def test_wrong_directory_identity_stops_before_content_requests(self):
        component,rows,calls=self.run_fetch(wrong_directory=True)
        self.assertEqual(component['status'],'error')
        self.assertEqual(component['code'],'directory_integrity_mismatch')
        self.assertIn('evidence',component)
        self.assertEqual(len(calls),1);self.assertEqual(rows,[])

    def test_corrupt_blob_keeps_other_verified_entries(self):
        component,rows,calls=self.run_fetch(corrupt=True)
        self.assertEqual(component['status'],'partial');self.assertFalse(component['complete'])
        self.assertEqual(component['symlinks'],1)
        self.assertEqual(component['errors'][0]['code'],'content_integrity_mismatch')

    def test_rate_limit_stops_further_network_calls(self):
        component,rows,calls=self.run_fetch(rate_limited=True)
        self.assertEqual(component['status'],'partial');self.assertFalse(component['complete'])
        self.assertEqual(component['errors'][0]['code'],'rate_limited');self.assertEqual(len(calls),2)

    def test_nested_directory_retains_the_parent_entry_mode(self):
        component,rows,calls=self.run_fetch()
        self.assertEqual(next(row for row in rows if row['path']=='src')['mode'],0o40000)

    def test_git_byte_filename_is_reversible_and_json_safe(self):
        component,rows,calls=self.run_fetch(non_utf8=True)
        self.assertEqual(component['status'],'available')
        named=next(row for row in rows if row.get('path_bytes_hex')=='ff')
        self.assertEqual(named['path'],'\\udcff')
        json.dumps(rows,ensure_ascii=False).encode('utf-8')

    def test_reopened_adapter_reuses_verified_objects_without_network(self):
        component,rows,calls=self.run_fetch(reopen=True)
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['cached_directories'],2)
        self.assertEqual(component['cached_files'],2)

    def test_cache_candidates_require_their_exact_source_uri(self):
        from swh_directory import object_refs
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup);store=ArtifactStore(folder.name)
        data=b'correct bytes';key=blob(data);directory=tree([])
        store.put('[]','application/json','software-heritage','http://archive.softwareheritage.org/api/1/directory/'+directory+'/?view=other',role='provider_response')
        store.put(data,'application/octet-stream','software-heritage','https://unrelated.example/file',preserve_bytes=True,
            role='archived_content',swhid='swh:1:cnt:'+key,integrity={'verified':True})
        client=httpx.Client(transport=httpx.MockTransport(lambda request: (_ for _ in ()).throw(AssertionError('unexpected request'))))
        self.addCleanup(client.close)
        self.assertEqual(object_refs(SoftwareHeritage(store,client)),{'dir':{},'cnt':{}})

if __name__=='__main__':unittest.main()
