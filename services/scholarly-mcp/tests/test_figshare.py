import hashlib,json,sys,tempfile,unittest
from pathlib import Path
import httpx
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scholarly import ArtifactStore,ServiceError


class FigshareContract(unittest.TestCase):
    def test_null_graphql_objects_keep_metadata_and_partial_members(self):
        for payload in ({'data':None},{'data':{'searchAdvanced':None}},[]):
            with self.subTest(payload=payload):
                def handler(request):
                    if request.url.host=='api.figshare.com':
                        return httpx.Response(200,json={'id':42,'version':1,'articles_count':1})
                    return httpx.Response(200,json=payload)
                result=self.adapter(handler).fetch('collection:42@1',parts=['metadata','supplementary'])
                self.assertEqual(result['components']['metadata']['status'],'available')
                component=result['components']['supplementary']
                self.assertEqual(component['status'],'partial')
                self.assertEqual(component['error']['code'],'invalid_response')
                self.assertEqual(json.loads(self.store.read(component['artifact']['ref'])[1]),[])
                evidence=component['error']['evidence']
                self.assertEqual(json.loads(self.store.read(evidence['ref'])[1]),payload)

    def adapter(self,handler):
        from figshare import Figshare
        temp=tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.store=ArtifactStore(temp.name); self.calls=[]
        def serve(req):
            self.calls.append(req)
            self.assertNotIn('authorization',req.headers)
            return handler(req)
        client=httpx.Client(transport=httpx.MockTransport(serve)); self.addCleanup(client.close)
        adapter=Figshare(self.store,client); adapter.min_interval=0
        return adapter

    def test_search_preserves_native_post_filters_and_arbitrary_window(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json=[{'id':12,'title':'a'},{'id':13,'title':'b'}]))
        result=adapter.search('quantum',options={'institution':42},start=3,limit=2,export='native')
        self.assertEqual(json.loads(self.calls[0].content),{'search_for':'quantum','institution':42,'offset':3,'limit':2})
        self.assertEqual(self.calls[0].method,'POST')
        self.assertIsNone(result['total']); self.assertEqual(result['next'],{'start':5})

    def test_post_redirect_semantics_and_boundary(self):
        for code,method in [(302,'GET'),(303,'GET'),(307,'POST'),(308,'POST')]:
            with self.subTest(code=code):
                adapter=self.adapter(lambda r:httpx.Response(code,headers={'Location':'https://api.figshare.com/v2/articles'}) if r.url.path.endswith('/search') else httpx.Response(200,json=[]))
                adapter.search('quantum',options={},limit=2)
                self.assertEqual(self.calls[-1].method,method)
        adapter=self.adapter(lambda r:httpx.Response(307,headers={'Location':'https://other.example/'}))
        with self.assertRaises(ServiceError) as cm: adapter.search('quantum',options={})
        self.assertEqual(cm.exception.result['code'],'source_boundary'); self.assertEqual(len(self.calls),1)

    def test_page_number_recovers_window_beyond_offset_limit(self):
        def handler(req):
            body=json.loads(req.content)
            self.assertEqual(body['search_for'],'data')
            self.assertEqual(body['order'],'published_date')
            if 'offset' in body:return httpx.Response(400,json={'message':'offset limit'})
            offset=(body['page']-1)*body['page_size']
            return httpx.Response(200,json=[{'id':i} for i in range(offset,offset+body['page_size'])])
        adapter=self.adapter(handler)
        result=adapter.search('data',options={'order':'published_date'},start=5001,limit=2,export='native')
        self.assertEqual([r['id'] for r in json.loads(self.store.read(result['records']['ref'])[1])],[5001,5002])
        self.assertEqual(result['next'],{'start':5003})
        self.assertEqual(len(result['export']['artifacts']),2)
        self.assertEqual([r['native_start'] for r in result['native_pages']],[5000,5002])

    def test_later_page_failure_preserves_selected_records(self):
        def handler(req):
            body=json.loads(req.content)
            return httpx.Response(200,json=[{'id':5000},{'id':5001}]) if body['page']==2501 else httpx.Response(503)
        adapter=self.adapter(handler)
        result=adapter.search('data',options={},start=5001,limit=2)
        self.assertEqual(result['status'],'partial')
        self.assertEqual(result['received'],1)
        self.assertEqual(result['next'],{'start':5002})
        self.assertEqual(result['errors'][0]['http_status'],503)

    def test_collection_members_cross_old_offset_ceiling(self):
        def handler(req):
            if req.url.path.endswith('/articles'):
                params=req.url.params
                size=int(params.get('limit',params.get('page_size',100)))
                offset=int(params['offset']) if 'offset' in params else (int(params['page'])-1)*size
                return httpx.Response(200,json=[{'id':i} for i in range(offset,min(offset+size,5102))])
            return httpx.Response(200,json={'id':42,'version':1,'articles_count':5102})
        adapter=self.adapter(handler)
        result=adapter.fetch('collection:42',parts=['supplementary'])
        component=result['components']['supplementary']
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['received'],5102)
        self.assertIn('page',self.calls[-1].url.params)

    def test_versioned_file_integrity_and_external_links(self):
        content=b'original file bytes\n'
        row={'id':42,'version':2,'doi':'10.6084/m9.figshare.42.v2','files':[
            {'id':12,'name':'data.txt','size':len(content),'computed_md5':hashlib.md5(content).hexdigest(),'download_url':'https://ndownloader.figshare.com/files/12','is_link_only':False},
            {'id':13,'name':'external','download_url':'https://other.example/file','is_link_only':True}]}
        for received in [content,b'corrupt']:
            def handler(req):
                if req.url.path=='/files/12': return httpx.Response(200,content=received,headers={'Content-Type':'text/plain'})
                self.assertEqual(req.url.path,'/v2/articles/42/versions/2')
                return httpx.Response(200,json=row)
            adapter=self.adapter(handler)
            result=adapter.fetch('10.6084/m9.figshare.42.v2',parts=['metadata','fulltext'])
            files=result['components']['fulltext']['files']
            self.assertEqual(files[1]['status'],'selection_required'); self.assertEqual(len(self.calls),2)
            if received==content:
                self.assertEqual(self.store.read(files[0]['artifact']['ref'])[1],content)
                self.assertTrue(files[0]['artifact']['checksum_verified'])
            else: self.assertEqual(files[0]['code'],'file_integrity_mismatch')

    def test_collection_pagination_and_historical_membership(self):
        def handler(req):
            if req.url.path=='/api/graphql':
                body=json.loads(req.content)
                self.assertEqual(body['operationName'],'getItems')
                self.assertEqual(body['variables']['filters']['collectionIdVersion'],'42_1')
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':3,'cursor':None,'elements':[
                        {'id':7,'title':'old a','url':'https://figshare.com/articles/dataset/old_a/7'},
                        {'id':8,'title':'old b','url':'https://figshare.com/articles/dataset/old_b/8'},
                        {'id':9,'title':'old c','url':'https://figshare.com/articles/dataset/old_c/9'}]}}}})
            if req.url.path.endswith('/articles'):
                offset=int(req.url.params['offset'])
                return httpx.Response(200,json=[{'id':i,'doi':f'10.6084/m9.figshare.{i}.v1'} for i in range(offset,min(offset+100,102))])
            version=1 if '/versions/1' in req.url.path else 2
            count=3 if version==1 else 102
            return httpx.Response(200,json={'id':42,'version':version,'articles_count':count,'doi':f'10.6084/m9.figshare.c.42.v{version}'})
        adapter=self.adapter(handler)
        result=adapter.fetch('collection:42',parts=['metadata','supplementary'])
        component=result['components']['supplementary']
        self.assertEqual(component['received'],102)
        self.assertEqual(len(self.calls),3)
        adapter=self.adapter(handler)
        result=adapter.fetch('10.6084/m9.figshare.c.42.v1',parts=['supplementary'])
        component=result['components']['supplementary']
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['received'],3)
        self.assertEqual(component['expected'],3)
        self.assertEqual(component['membership_version'],1)
        self.assertEqual(json.loads(self.store.read(component['artifact']['ref'])[1])[0]['id'],7)
        self.assertEqual(len(self.calls),2)

    def test_historical_collection_membership_paginates_and_preserves_partial_results(self):
        def handler(req):
            if req.url.host=='api.figshare.com':
                return httpx.Response(200,json={'id':42,'version':1,'articles_count':41,'doi':'10.6084/m9.figshare.c.42.v1'})
            body=json.loads(req.content); cursor=body['variables']['cursor']
            if cursor=='':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':41,'cursor':'next-page','elements':[{'id':i,'title':str(i)} for i in range(1,41)]}}}})
            self.assertEqual(cursor,'next-page')
            return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                'count':41,'cursor':None,'elements':[{'id':41,'title':'41'}]}}}})
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@1',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['received'],41)
        self.assertEqual(component['reported'],41)
        self.assertEqual(len(component['artifact']['evidence_refs']),2)

        def failed_second_page(req):
            if req.url.host=='api.figshare.com':
                return httpx.Response(200,json={'id':42,'version':1,'articles_count':41})
            body=json.loads(req.content)
            if body['variables']['cursor']=='':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':41,'cursor':'next-page','elements':[{'id':i} for i in range(1,41)]}}}})
            return httpx.Response(503)
        adapter=self.adapter(failed_second_page)
        component=adapter.fetch('collection:42@1',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],40)
        self.assertEqual(component['error']['http_status'],503)
        self.assertEqual(len(json.loads(self.store.read(component['artifact']['ref'])[1])),40)

    def test_historical_membership_stops_at_reported_count_even_with_cursor(self):
        def handler(req):
            if req.url.host=='api.figshare.com':
                return httpx.Response(200,json={'id':42,'version':1,'articles_count':40})
            return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                'count':40,'cursor':'unnecessary-follow-up','elements':[{'id':i} for i in range(1,41)]}}}})
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@1',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['received'],40)
        self.assertEqual(len(self.calls),2)

    def test_current_version_count_mismatch_reconciles_with_stable_current_rest(self):
        current_metadata_calls=0
        def handler(req):
            nonlocal current_metadata_calls
            if req.url.path=='/v2/collections/42/versions/8':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':2,'cursor':None,'elements':[{'id':7},{'id':8}]}}}})
            if req.url.path=='/v2/collections/42':
                current_metadata_calls+=1
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/v2/collections/42/articles':
                return httpx.Response(200,json=[{'id':7},{'id':8},{'id':9}])
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@8',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'available')
        self.assertEqual(component['received'],3)
        self.assertEqual(component['reported'],2)
        self.assertEqual(component['membership_version'],8)
        self.assertEqual(component['membership_basis'],'current_rest_verified_same_version')
        self.assertEqual(component['reconciliation']['search_only_ids'],[])
        self.assertEqual(component['reconciliation']['current_rest_only_ids'],[9])
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['search_subset_artifact']['ref'])[1])],[7,8])
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['artifact']['ref'])[1])],[7,8,9])
        self.assertEqual(current_metadata_calls,2)

    def test_current_version_reconciliation_rejects_a_version_change(self):
        current_metadata_calls=0
        def handler(req):
            nonlocal current_metadata_calls
            if req.url.path=='/v2/collections/42/versions/8':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':2,'cursor':None,'elements':[{'id':7},{'id':8}]}}}})
            if req.url.path=='/v2/collections/42':
                current_metadata_calls+=1
                version=8 if current_metadata_calls==1 else 9
                return httpx.Response(200,json={'id':42,'version':version,'articles_count':3,
                    'doi':f'10.6084/m9.figshare.c.42.v{version}'})
            if req.url.path=='/v2/collections/42/articles':
                return httpx.Response(200,json=[{'id':7},{'id':8},{'id':9}])
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@8',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],2)
        self.assertEqual(component['error']['code'],'result_set_changed')
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['artifact']['ref'])[1])],[7,8])

    def test_past_version_count_mismatch_preserves_public_search_subset(self):
        def handler(req):
            if req.url.path=='/v2/collections/42/versions/6':
                return httpx.Response(200,json={'id':42,'version':6,'articles_count':17,'doi':'10.6084/m9.figshare.c.42.v6'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':16,'cursor':None,'elements':[{'id':i} for i in range(1,17)]}}}})
            if req.url.path=='/v2/collections/42':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':21,'doi':'10.6084/m9.figshare.c.42.v8'})
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@6',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],16)
        self.assertEqual(component['reported'],16)
        self.assertEqual(component['error']['code'],'provider_membership_count_mismatch')
        self.assertEqual(component['error']['current_version'],8)
        self.assertEqual(len(json.loads(self.store.read(component['artifact']['ref'])[1])),16)

    def test_current_reconciliation_refuses_a_non_superset_and_preserves_search_rows(self):
        def handler(req):
            if req.url.path=='/v2/collections/42/versions/8':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':2,'cursor':None,'elements':[{'id':7},{'id':8}]}}}})
            if req.url.path=='/v2/collections/42':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/v2/collections/42/articles':
                return httpx.Response(200,json=[{'id':7},{'id':9},{'id':10}])
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@8',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],2)
        self.assertEqual(component['error']['code'],'provider_membership_count_mismatch')
        self.assertEqual(component['error']['search_only_ids'],[8])
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['artifact']['ref'])[1])],[7,8])

    def test_current_reconciliation_rejects_a_count_change_during_listing(self):
        current_metadata_calls=0
        def handler(req):
            nonlocal current_metadata_calls
            if req.url.path=='/v2/collections/42/versions/8':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':2,'cursor':None,'elements':[{'id':7},{'id':8}]}}}})
            if req.url.path=='/v2/collections/42':
                current_metadata_calls+=1
                count=3 if current_metadata_calls==1 else 4
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':count,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/v2/collections/42/articles':
                return httpx.Response(200,json=[{'id':7},{'id':8},{'id':9}])
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@8',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],2)
        self.assertEqual(component['error']['code'],'result_set_changed')
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['artifact']['ref'])[1])],[7,8])

    def test_current_version_reconciliation_rejects_a_version_change(self):
        current_metadata_calls=0
        def handler(req):
            nonlocal current_metadata_calls
            if req.url.path=='/v2/collections/42/versions/8':
                return httpx.Response(200,json={'id':42,'version':8,'articles_count':3,'doi':'10.6084/m9.figshare.c.42.v8'})
            if req.url.path=='/api/graphql':
                return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                    'count':2,'cursor':None,'elements':[{'id':7},{'id':8}]}}}})
            if req.url.path=='/v2/collections/42':
                current_metadata_calls+=1
                version=8 if current_metadata_calls==1 else 9
                return httpx.Response(200,json={'id':42,'version':version,'articles_count':3,
                    'doi':f'10.6084/m9.figshare.c.42.v{version}'})
            if req.url.path=='/v2/collections/42/articles':
                return httpx.Response(200,json=[{'id':7},{'id':8},{'id':9}])
            self.fail(f'unexpected request path {req.url.path}')
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@8',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],2)
        self.assertEqual(component['error']['code'],'result_set_changed')
        self.assertEqual([x['id'] for x in json.loads(self.store.read(component['artifact']['ref'])[1])],[7,8])

    def test_historical_membership_graphql_url_is_exactly_scoped(self):
        adapter=self.adapter(lambda r:httpx.Response(500))
        self.assertTrue(adapter.allowed_url('https://figshare.com/api/graphql'))
        self.assertFalse(adapter.allowed_url('https://figshare.com/api/graphql/other'))
        self.assertFalse(adapter.allowed_url('https://figshare.com/account'))

    def test_historical_membership_does_not_follow_an_empty_cursor_page(self):
        def handler(req):
            if req.url.host=='api.figshare.com':
                return httpx.Response(200,json={'id':42,'version':1,'articles_count':1})
            self.assertEqual(json.loads(req.content)['variables']['cursor'],'')
            return httpx.Response(200,json={'data':{'searchAdvanced':{'results':{
                'count':1,'cursor':'unexpected-follow-up','elements':[]}}}})
        adapter=self.adapter(handler)
        component=adapter.fetch('collection:42@1',parts=['supplementary'])['components']['supplementary']
        self.assertEqual(component['status'],'partial')
        self.assertEqual(component['received'],0)
        self.assertEqual(component['error']['code'],'incomplete_response')
        self.assertEqual(len(self.calls),2)

    def test_restricted_files_and_wrong_identity_are_not_downloaded(self):
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':42,'version':1,'is_embargoed':True,'files':[{'id':12}]}))
        result=adapter.fetch('42',parts=['fulltext'])
        self.assertEqual(result['components']['fulltext']['status'],'restricted'); self.assertEqual(len(self.calls),1)
        adapter=self.adapter(lambda r:httpx.Response(200,json={'id':43,'version':1}))
        with self.assertRaises(ServiceError) as cm: adapter.fetch('42',parts=['metadata'])
        self.assertEqual(cm.exception.result['code'],'identity_mismatch')

    def test_native_downloader_redirect_is_bound_to_the_selected_file(self):
        content=b'selected public file'
        row={'id':42,'version':1,'files':[{'id':12,'name':'file.txt','size':len(content),
            'computed_md5':hashlib.md5(content).hexdigest(),'download_url':'https://ndownloader.figshare.com/files/12'}]}
        for destination,expected in [('https://s3-eu-west-1.amazonaws.com/pstorage-acs-6854636/file','available'),
                                     ('https://unrelated.example/file','error')]:
            def handler(req):
                if req.url.host=='api.figshare.com':return httpx.Response(200,json=row)
                if req.url.host=='ndownloader.figshare.com':return httpx.Response(302,headers={'Location':destination})
                return httpx.Response(200,content=content)
            adapter=self.adapter(handler)
            result=adapter.fetch('42#file:12',parts=['fulltext'])
            self.assertEqual(result['components']['fulltext']['files'][0]['status'],expected)
            self.assertFalse(adapter.allowed_url(destination))
            if expected=='error':self.assertEqual(len(self.calls),2)

    def test_public_urls_preserve_record_kind_and_version(self):
        adapter=self.adapter(lambda r:httpx.Response(500))
        for target,expected in [
            ('https://aip.figshare.com/articles/figure/Supplementary/29678765/1',('articles',29678765,1,None,None)),
            ('https://aip.figshare.com/collections/Example/7956296/1',('collections',7956296,1,None,None)),
            ('https://api.figshare.com/v2/articles/42/versions/2',('articles',42,2,None,None))]:
            self.assertEqual(adapter.resolve(target),expected)
        self.assertFalse(adapter.allowed_url('https://s3-eu-west-1.amazonaws.com/unrelated/file'))
        self.assertFalse(adapter.allowed_url('https://api.figshare.com/v2/account/articles/42'))


if __name__=='__main__': unittest.main()
