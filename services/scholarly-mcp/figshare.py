"""Anonymous Figshare public metadata and hosted files; linked providers stay explicit."""
import hashlib
import mimetypes
import re
from urllib.parse import unquote,urlsplit
from api_adapters import APIAdapter,doi
from scholarly import ServiceError,encoded


def public_row(value):
    if isinstance(value,list): return [public_row(x) for x in value]
    if isinstance(value,dict): return {k:public_row(v) for k,v in value.items() if not k.startswith('url_private_')}
    return value


class Figshare(APIAdapter):
    source='figshare'
    hosts=('api.figshare.com','figshare.com','ndownloader.figshare.com','s3-eu-west-1.amazonaws.com')
    min_interval=1.05
    max_limit=1000
    options=('kind','order','order_direction','institution','published_since','modified_since','group','resource_doi','doi','handle','item_type','project_id','collection_id')

    def allowed_url(self,url):
        if not super().allowed_url(url): return False
        parsed=urlsplit(url)
        if parsed.hostname=='api.figshare.com':
            return bool(re.fullmatch(r'/v2/(articles|collections)(?:/(?:search|[1-9]\d*(?:/versions/[1-9]\d*)?(?:/articles)?))?',parsed.path))
        if parsed.hostname=='figshare.com':
            return parsed.path=='/api/graphql'
        if parsed.hostname=='ndownloader.figshare.com':
            return bool(re.fullmatch(r'/files/[1-9]\d*',parsed.path))
        # The observed AIP storage bucket. Additional Figshare stores need an observed route.
        return parsed.path.startswith('/figshare-production-eu-aip-storage5262-eu-west-1/') and '..' not in unquote(parsed.path).split('/')

    def search(self,query,*,options,start=0,limit=20,cursor=None,export=None):
        self.validate(options,start,limit)
        if cursor or start+limit>5000000:
            raise ServiceError('invalid_range','Use start/limit within the documented 5000 pages of at most 1000 records; no cursor is provided')
        kind=options.get('kind','articles')
        if kind not in ('articles','collections'):
            raise ServiceError('invalid_options','kind must be articles or collections')
        if kind=='collections' and any(k in options for k in ('item_type','project_id','collection_id')):
            raise ServiceError('invalid_options','These filters apply to articles only')
        collection=options.get('collection_id')
        if collection is not None and (query or set(options)-{'collection_id','kind'} or type(collection) is not int or collection<1):
            raise ServiceError('invalid_options','collection_id lists current members with an empty query and no other filters')
        body={k:v for k,v in options.items() if k!='kind'}
        if query:body['search_for']=query
        rows=[];native_pages=[];errors=[]
        page_size=max(limit,(start+limit+4999)//5000)
        offset=start if start<=5000 else start//page_size*page_size
        while len(rows)<limit:
            pagination={'offset':offset,'limit':limit} if start<=5000 else {'page':offset//page_size+1,'page_size':page_size}
            requested_size=pagination.get('limit',page_size)
            try:
                if collection is not None:
                    raw,evidence=self.request(f'https://api.figshare.com/v2/collections/{collection}/articles',params=pagination)
                else:
                    raw,evidence=self.request('https://api.figshare.com/v2/'+kind+'/search',json_body={**body,**pagination})
                if not isinstance(raw,list) or len(raw)>requested_size or any(not isinstance(r,dict) or type(r.get('id')) is not int for r in raw):
                    raise ServiceError('invalid_response','Figshare did not return the requested result window',evidence=evidence)
                selected=raw[max(0,start-offset):start+limit-offset]
                ids=[r['id'] for r in rows+selected]
                if len(ids)!=len(set(ids)):
                    raise ServiceError('inconsistent_pagination','Figshare repeated a record in the selected window',evidence=evidence)
            except ServiceError as error:
                if not rows:raise
                errors.append(error.result);break
            rows.extend(selected)
            native_pages.append({'artifact':evidence,'native_start':offset,'received':len(raw),'selected':len(selected)})
            if len(raw)<requested_size or start<=5000:break
            offset+=page_size
        evidence=native_pages[0]['artifact']
        result=self.page(public_row(rows),None,evidence,query,options,start,limit,more=bool(errors) or len(rows)==limit,
            evidence_refs=[p['artifact']['ref'] for p in native_pages])
        result['native_pages']=native_pages
        if errors:result.update(status='partial',errors=errors)
        result['pagination_basis']='No global total is provided; a full page may have a following page'
        if result['has_more'] and start+len(rows)>=5000000:
            result.update(next=None,continuation_limited=True)
        result=self.export_page(result,export)
        if export=='native' and (len(native_pages)>1 or native_pages[0]['received']!=len(rows)):
            result['export']={'artifacts':[p['artifact'] for p in native_pages],
                'scope':'Original provider pages; records contains the exact requested window'}
        return result

    def resolve(self,target):
        value=target.strip(); requested_doi=None; file_id=None
        if value.startswith(('http://','https://')):
            parsed=urlsplit(value)
            if parsed.username or parsed.password or parsed.port not in (None,443) or parsed.scheme!='https':
                raise ServiceError('invalid_target','Use an HTTPS public Figshare record URL')
            if parsed.hostname in ('doi.org','dx.doi.org'):
                value=doi(value)
            elif parsed.hostname=='api.figshare.com' or parsed.hostname=='figshare.com' or (parsed.hostname or '').endswith('.figshare.com'):
                path=unquote(parsed.path)
                patterns=(r'/v2/(articles|collections)/([1-9]\d*)(?:/versions/([1-9]\d*))?(?:/files/([1-9]\d*))?/?',) if parsed.hostname=='api.figshare.com' else (
                    r'/(articles)/(?:[^/]+/[^/]+/)?([1-9]\d*)(?:/([1-9]\d*))?(?:/files/([1-9]\d*))?/?',
                    r'/(collections)/(?:[^/]+/)?([1-9]\d*)(?:/([1-9]\d*))?(?:/files/([1-9]\d*))?/?')
                match=next((m for pattern in patterns if (m:=re.fullmatch(pattern,path))),None)
                if not match:
                    raise ServiceError('invalid_target','Use a public article/collection URL, DOI, or article:ID@version#file:ID')
                if match[1]=='collections' and match[4]: raise ServiceError('invalid_target','Select an article before selecting a file')
                return match[1],int(match[2]),int(match[3]) if match[3] else None,int(match[4]) if match[4] else None,None
            else:
                raise ServiceError('source_boundary','Target is outside Figshare')
        if value.startswith(('10.','doi:')):
            requested_doi=doi(value)
            match=re.fullmatch(r'10\.(?:6084/m9\.figshare|60893/figshare\.aip)\.(c\.)?([1-9]\d*)(?:\.v([1-9]\d*))?',requested_doi,re.I)
            if not match:
                result=self.search('',options={'doi':requested_doi},limit=5)
                result['status']='selection_required' if result['received'] else 'not_found'
                return result
            return 'collections' if match[1] else 'articles',int(match[2]),int(match[3]) if match[3] else None,None,requested_doi
        match=re.fullmatch(r'(?:(article|collection):)?([1-9]\d*)(?:@([1-9]\d*))?(?:#file:([1-9]\d*))?',value)
        if match:
            kind='collections' if match[1]=='collection' else 'articles'
            if kind=='collections' and match[4]: raise ServiceError('invalid_target','Select an article before selecting a file')
            return kind,int(match[2]),int(match[3]) if match[3] else None,int(match[4]) if match[4] else None,None
        result=self.search(value,options={},limit=5)
        result['status']='selection_required' if result['received'] else 'not_found'
        return result

    def collection_members(self,row,version,evidence):
        if version is not None:
            query='''query getItems($searchQuery: String, $cursor: String, $pageSize: Int, $sort: Order, $filters: AdvancedSearchFilter) {
              searchAdvanced(searchQuery: $searchQuery, cursor: $cursor, pageSize: $pageSize, sort: $sort, filters: $filters, scope: "public_collection_items") {
                results { count cursor elements { id title contentType: entityType institution: institutionName publishedDate revisionDate isEmbargoed embargoDate embargoType url } }
              }
            }'''
            rows=[]; refs=[]; expected=row.get('articles_count'); reported=None; cursor=''; error=None
            while True:
                try:
                    raw,page_evidence=self.request('https://figshare.com/api/graphql',json_body={
                        'operationName':'getItems','variables':{'searchQuery':'','cursor':cursor,'pageSize':40,
                        'sort':{'by':'added_date','type':'desc'},'filters':{'collectionIdVersion':f"{row['id']}_{version}"}},'query':query})
                    if not isinstance(raw,dict) or raw.get('errors'):
                        raise ServiceError('invalid_response','Figshare returned an error for historical collection membership',evidence=page_evidence)
                    data=raw.get('data')
                    advanced=data.get('searchAdvanced') if isinstance(data,dict) else None
                    result=advanced.get('results') if isinstance(advanced,dict) else None
                    if not isinstance(result,dict) or type(result.get('count')) is not int or result['count']<0 \
                            or not isinstance(result.get('elements'),list) or any(not isinstance(item,dict) or type(item.get('id')) is not int for item in result['elements']):
                        raise ServiceError('invalid_response','Figshare returned an invalid historical collection member page',evidence=page_evidence)
                    if reported is not None and result['count']!=reported:
                        raise ServiceError('result_set_changed','Figshare changed the historical membership count between pages',evidence=page_evidence)
                    identifiers=[item['id'] for item in rows+result['elements']]
                    if len(identifiers)!=len(set(identifiers)):
                        raise ServiceError('inconsistent_pagination','Figshare repeated a historical collection member',evidence=page_evidence)
                    next_cursor=result.get('cursor')
                    if next_cursor is not None and (not isinstance(next_cursor,str) or not next_cursor or next_cursor==cursor):
                        raise ServiceError('inconsistent_pagination','Figshare returned an invalid historical membership cursor',evidence=page_evidence)
                    if next_cursor is not None and not result['elements']:
                        raise ServiceError('incomplete_response','Figshare reported another historical membership page after an empty page',evidence=page_evidence)
                    reported=result['count']; rows.extend(public_row(result['elements'])); refs.append(page_evidence['ref'])
                    if len(rows)>reported:
                        raise ServiceError('invalid_response','Figshare returned more historical members than its reported count',evidence=page_evidence)
                    if len(rows)==reported or next_cursor is None: break
                    cursor=next_cursor
                except ServiceError as exc:
                    error=exc.result; break
            search_artifact=self.store.put(encoded(rows),'application/json',self.source,evidence['url'],role='collection_member_search_subset',evidence_refs=refs,
                metadata_ref=evidence['ref'],collection_id=row['id'],membership_version=version)
            if error is None and reported is not None and len(rows)!=reported:
                error={'code':'incomplete_response','message':'Historical collection search pagination ended before its reported count',
                       'search_received':len(rows),'search_reported':reported}
            if error is None and type(expected) is int and len(rows)!=expected:
                mismatch={'code':'provider_membership_count_mismatch',
                    'message':'Version metadata count differs from the public collection-version search subset',
                    'metadata_count':expected,'search_count':reported,'search_received':len(rows)}
                try:
                    current_before,before_evidence=self.request(f"https://api.figshare.com/v2/collections/{row['id']}")
                    if not isinstance(current_before,dict) or current_before.get('id')!=row['id'] or type(current_before.get('version')) is not int:
                        raise ServiceError('identity_mismatch','Figshare returned invalid current collection identity',evidence=before_evidence)
                    mismatch['current_version']=current_before['version']
                    same_doi=not row.get('doi') or bool(current_before.get('doi')) \
                        and str(row['doi']).casefold()==str(current_before['doi']).casefold()
                    if current_before['version']==version and same_doi:
                        import json
                        current_rows=[]; current_refs=[]; current_error=None
                        while True:
                            try:
                                page=self.search('',options={'collection_id':row['id']},start=len(current_rows),limit=100)
                                batch=json.loads(self.store.read(page['records']['ref'])[1]); current_refs.append(page['evidence']['ref'])
                                if set(x['id'] for x in current_rows)&set(x['id'] for x in batch):
                                    raise ServiceError('inconsistent_pagination','Current collection pagination repeated a member')
                                current_rows.extend(batch)
                                if page.get('status')=='partial':
                                    current_error=(page.get('errors') or [{'code':'incomplete_response'}])[0]; break
                                if not page['has_more'] or len(current_rows)>=expected: break
                            except ServiceError as exc:
                                current_error=exc.result; break
                        current_after,after_evidence=self.request(f"https://api.figshare.com/v2/collections/{row['id']}")
                        stable=isinstance(current_after,dict) and current_after.get('id')==row['id'] \
                            and current_after.get('version')==version and current_after.get('doi')==current_before.get('doi') \
                            and current_after.get('articles_count')==current_before.get('articles_count')
                        search_ids={item['id'] for item in rows}; current_ids={item['id'] for item in current_rows}
                        if current_error is None and stable and len(current_rows)==expected \
                                and current_before.get('articles_count')==expected and search_ids<=current_ids:
                            artifact=self.store.put(encoded(current_rows),'application/json',self.source,evidence['url'],role='collection_members',
                                evidence_refs=current_refs,metadata_ref=evidence['ref'],current_identity_refs=[before_evidence['ref'],after_evidence['ref']],
                                collection_id=row['id'],membership_version=version)
                            return {'status':'available','artifact':artifact,'search_subset_artifact':search_artifact,
                                'received':len(current_rows),'expected':expected,'reported':reported,'error':None,
                                'content_kind':'historical_collection_member_references','membership_version':version,
                                'membership_basis':'current_rest_verified_same_version',
                                'reconciliation':{'search_received':len(rows),'current_rest_received':len(current_rows),
                                    'search_only_ids':sorted(search_ids-current_ids),'current_rest_only_ids':sorted(current_ids-search_ids)},
                                'scope':'Member references for the explicitly selected immutable collection version. The current REST relation was used only after matching the requested version before and after listing; the public collection-version search subset is preserved separately.'}
                        if not stable:
                            mismatch.update(code='result_set_changed',message='Current collection identity changed while reconciling the requested version')
                        elif current_error is not None:
                            mismatch['current_rest_error']=current_error
                        else:
                            mismatch.update(current_rest_received=len(current_rows),current_rest_count=current_before.get('articles_count'),
                                search_only_ids=sorted(search_ids-current_ids))
                except ServiceError as exc:
                    mismatch['current_identity_error']=exc.result
                error=mismatch
            artifact=search_artifact
            return {'status':'partial' if error else 'available','artifact':artifact,'received':len(rows),'expected':expected,
                    'reported':reported,'error':error,'content_kind':'historical_collection_member_references','membership_version':version,
                    'membership_basis':'version_ui_public_collection_search',
                    'scope':'Member references for the explicitly selected immutable collection version. Select a member DOI or article ID to retrieve its files.'}
        rows=[]; refs=[]; expected=row.get('articles_count'); error=None
        while True:
            if len(rows)>=5000000:
                error={'code':'continuation_limited','message':'Documented page-number limit reached; the collection member list is incomplete'}; break
            try:
                page=self.search('',options={'collection_id':row['id']},start=len(rows),limit=100)
            except ServiceError as exc:
                error=exc.result; break
            import json
            batch=json.loads(self.store.read(page['records']['ref'])[1]); refs.append(page['evidence']['ref'])
            if set(x['id'] for x in rows)&set(x['id'] for x in batch):
                error={'code':'inconsistent_pagination','message':'Collection pagination repeated a member'}; break
            rows.extend(batch)
            if not page['has_more'] or (type(expected) is int and len(rows)>=expected): break
        if error is None and type(expected) is int and len(rows)!=expected:
            error={'code':'incomplete_response','message':'Collected membership differs from the metadata count'}
        artifact=self.store.put(encoded(rows),'application/json',self.source,evidence['url'],role='collection_members',evidence_refs=refs,metadata_ref=evidence['ref'])
        return {'status':'partial' if error else 'available','artifact':artifact,'received':len(rows),'expected':expected,'error':error,
                'content_kind':'current_collection_member_references','membership_version':None,
                'scope':'Current member references only. Select a member DOI or article ID to retrieve its files.'}

    def article_files(self,row,file_id,evidence):
        if row.get('download_disabled') or row.get('is_embargoed') or row.get('is_confidential'):
            return {'status':'restricted','reason':'Figshare metadata marks this record as unavailable for public file download'}
        if row.get('is_metadata_record'):
            return {'status':'not_offered','reason':'Figshare marks this as a metadata-only record'}
        native=row.get('files',[])
        if not isinstance(native,list): raise ServiceError('invalid_response','Figshare files must be a list')
        selected=[f for f in native if file_id is None or f.get('id')==file_id]
        files=[]
        for file in selected:
            item=public_row(file)
            if file.get('is_link_only'):
                files.append({**item,'status':'selection_required','reason':'External linked file; select its provider explicitly'}); continue
            try:
                link=file.get('download_url','')
                if urlsplit(link).hostname!='ndownloader.figshare.com' or urlsplit(link).path!='/files/'+str(file.get('id')):
                    raise ServiceError('source_boundary','Hosted file metadata did not identify the expected Figshare download route')
                def native_file_redirect(origin,destination):
                    parsed=urlsplit(destination)
                    return origin==link and parsed.scheme=='https' and not parsed.username and not parsed.password \
                        and parsed.port in (None,443) and parsed.hostname=='s3-eu-west-1.amazonaws.com' \
                        and '..' not in unquote(parsed.path).split('/')
                data,downloaded=self.request(link,accept='binary',allow_redirect=native_file_redirect)
                checksum=file.get('computed_md5') or file.get('supplied_md5')
                if (file.get('size') is not None and len(data)!=file['size']) or (checksum and hashlib.md5(data).hexdigest().lower()!=checksum.lower()):
                    raise ServiceError('file_integrity_mismatch','Downloaded file differs from Figshare size or MD5 metadata',evidence=downloaded)
                media=mimetypes.guess_type(file.get('name',''))[0] or downloaded['media_type']; extra={}
                if data.startswith(b'%PDF-'):
                    import pymupdf
                    with pymupdf.open(stream=data,filetype='pdf') as doc: extra['pages']=len(doc)
                    media='application/pdf'
                artifact=self.store.put(data,media,self.source,downloaded['url'],preserve_bytes=True,role='record_file',
                    record_id=row['id'],version=row['version'],filename=file.get('name'),metadata_ref=evidence['ref'],
                    provider_md5=checksum,checksum_verified=bool(checksum),**extra)
                files.append({**item,'status':'available','artifact':artifact})
            except ServiceError as exc:
                files.append({**item,**exc.result})
            except Exception as exc:
                files.append({**item,'status':'error','code':'file_retrieval_failed','error_type':type(exc).__name__})
        return {'status':'available' if files and all(f['status']=='available' for f in files) else 'partial' if files else 'not_found' if file_id else 'not_offered',
                'files':files,'received':sum(f['status']=='available' for f in files),'requested_files':len(selected),'content_kind':'record_files'}

    def fetch(self,target,*,parts):
        resolved=self.resolve(target)
        if isinstance(resolved,dict): return resolved
        kind,identifier,version,file_id,requested_doi=resolved
        url=f'https://api.figshare.com/v2/{kind}/{identifier}'+(f'/versions/{version}' if version else '')
        raw,evidence=self.request(url)
        if not isinstance(raw,dict) or raw.get('id')!=identifier or (version and raw.get('version')!=version):
            raise ServiceError('identity_mismatch','Figshare returned a different record or version',evidence=evidence)
        if requested_doi:
            actual=str(raw.get('doi','')).casefold(); expected=requested_doi.casefold()
            if actual!=expected and (version or re.sub(r'\.v\d+$','',actual)!=expected):
                raise ServiceError('identity_mismatch','Figshare record DOI differs from the requested DOI',evidence=evidence)
        row=public_row(raw)
        result=self.fetched([row],evidence,parts,('metadata','export'))
        result.update(target=target,record_id=identifier,record_kind=kind,version=raw.get('version'),version_selection='explicit' if version else 'latest_at_retrieval')
        if 'abstract' in parts:
            result['components']['abstract']={'status':'source_page' if raw.get('description') else 'not_found','artifact':result['records'],
                'selection':'/0/description','reason':'Repository description; not asserted to be an author abstract'}
        if {'fulltext','supplementary'}&set(parts):
            component=self.collection_members(raw,version,evidence) if kind=='collections' else self.article_files(raw,file_id,evidence)
            for part in ('fulltext','supplementary'):
                if part in parts:
                    result['components'][part]=({'status':'not_offered','reason':'A collection has member references; request supplementary and select a member'} if kind=='collections' and part=='fulltext' else component)
        result['status']='ok' if all(c['status']=='available' for c in result['components'].values()) else 'partial'
        return result
