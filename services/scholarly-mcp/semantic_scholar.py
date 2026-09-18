"""Credential-free Semantic Scholar records, native citations and bounded graph pages."""
import json,re,unicodedata
from urllib.parse import urlsplit,quote
from scholarly import ServiceError, bibliography, encoded, failure_details

BASE='https://api.semanticscholar.org/graph/v1/paper/'
PAPER_FIELDS='title,authors,year,abstract,externalIds,url,openAccessPdf,publicationTypes,citationCount,referenceCount,corpusId'
MATCH_FIELDS='title,authors,year,externalIds,url,corpusId'
EDGE_FIELDS='title,authors,year,externalIds,contexts,intents,isInfluential'
IDENTITY_FIELDS=('title','externalIds','corpusId')
METADATA_FIELDS=('authors','year','url','openAccessPdf','publicationTypes','citationCount','referenceCount')
BULK_CURSOR_ROLE='semantic_scholar_bulk_cursor'
BULK_HISTORY_ROLE='semantic_scholar_bulk_history'


def normalized_title(value):
    text=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',value or '')).strip()
    return re.sub(r'\s+([,.;:!?])',r'\1',text).casefold()


def paper_identifier(target):
    from api_adapters import doi
    value=target.strip()
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value)
        if parsed.username or parsed.password or parsed.port not in (None,80,443):
            raise ServiceError('invalid_target','Use a public Semantic Scholar paper URL or DOI')
        if parsed.hostname in ('semanticscholar.org','www.semanticscholar.org'):
            match=re.fullmatch(r'/paper/(?:[^/]+/)?([a-f0-9]{40})/?',parsed.path,re.I)
            if not match:raise ServiceError('invalid_target','Semantic Scholar paper URL has no paper ID')
            return match[1].lower()
        if parsed.hostname not in ('doi.org','dx.doi.org'):
            raise ServiceError('source_boundary','Use a Semantic Scholar paper link or DOI')
        return 'DOI:'+doi(value)
    if value.startswith('10.') or value.lower().startswith('doi:'):return 'DOI:'+doi(value)
    if re.fullmatch(r'[a-f0-9]{40}',value,re.I):return value.lower()
    match=re.fullmatch(r'(ARXIV|PMID|CorpusId):(\S+)',value,re.I)
    if match:return {'arxiv':'ARXIV','pmid':'PMID','corpusid':'CorpusId'}[match[1].lower()]+':'+match[2]
    return None


def native_bibtex(adapter,rows,proof):
    artifacts=[];errors=[]
    for row in rows:
        styles=row.get('citationStyles') or {}
        if not isinstance(styles,dict):
            errors.append({'paper_id':row.get('paperId'),'status':'error','code':'invalid_native_citation'});continue
        raw=styles.get('bibtex')
        if not isinstance(raw,str) or not raw.strip():
            errors.append({'paper_id':row.get('paperId'),'status':'not_found','code':'citation_not_provided'});continue
        artifact=adapter.store.put(raw,'application/x-bibtex',adapter.source,proof['url'],role='native_citation',paper_id=row.get('paperId'),evidence_ref=proof['ref'])
        try:
            parsed=bibliography(raw.encode(),'application/x-bibtex')
            if len(parsed)!=1:
                raise ServiceError('invalid_native_citation','Semantic Scholar citationStyles did not contain one BibTeX entry')
            expected=(row.get('externalIds') or {}).get('DOI');observed=parsed[0].get('doi')
            if expected and observed:
                from api_adapters import doi
                if doi(expected).casefold()!=doi(observed).casefold():
                    raise ServiceError('identity_mismatch','Semantic Scholar BibTeX DOI differs from its paper metadata')
            elif not normalized_title(row.get('title')) or normalized_title(parsed[0].get('title'))!=normalized_title(row.get('title')):
                raise ServiceError('identity_mismatch','Semantic Scholar BibTeX without a DOI has another title')
            artifacts.append(artifact)
        except ServiceError as exc:errors.append({'paper_id':row.get('paperId'),**exc.result,'source_export':artifact})
        except Exception as exc:errors.append({'paper_id':row.get('paperId'),'status':'error','code':'invalid_native_citation',**failure_details(exc),'source_export':artifact})
    result={'status':'partial' if errors else 'available' if artifacts else 'not_found','artifacts':artifacts,'errors':errors}
    if artifacts:
        data=b'\n\n'.join(adapter.store.read(a['ref'])[1] for a in artifacts)
        combined=artifacts[0] if len(artifacts)==1 else adapter.store.put(data,'application/x-bibtex',adapter.source,proof['url'],role='native_citations',parent_refs=[a['ref'] for a in artifacts])
        result.update(combined);result['artifact']=combined
    return result


def _bulk_cursor(adapter,state,proof):
    artifact=adapter.store.put(encoded(state),'application/json',adapter.source,proof['url'],preserve_bytes=True,
        role=BULK_CURSOR_ROLE,version=2)
    return artifact['ref']


def _bulk_history(adapter,parent,paper_ids,proof):
    state={'version':1,'source':adapter.source,'parent':parent,'paper_ids':paper_ids,'response_ref':proof['ref']}
    artifact=adapter.store.put(encoded(state),'application/json',adapter.source,proof['url'],preserve_bytes=True,
        role=BULK_HISTORY_ROLE,version=1)
    return artifact['ref']


def _read_bulk_history(adapter,history_ref):
    seen=set();visited=set();current=history_ref
    try:
        while current is not None:
            if not isinstance(current,str) or current in visited:
                raise ValueError('Invalid bulk history link')
            visited.add(current)
            manifest,data=adapter.store.read(current);state=json.loads(data)
            if manifest.get('source')!=adapter.source or manifest.get('role')!=BULK_HISTORY_ROLE or manifest.get('version')!=1 \
                    or not isinstance(state,dict) or state.get('version')!=1 or state.get('source')!=adapter.source \
                    or not isinstance(state.get('paper_ids'),list) or not isinstance(state.get('response_ref'),str) \
                    or state.get('parent') is not None and not isinstance(state.get('parent'),str):
                raise ValueError('Invalid bulk history state')
            paper_ids=state['paper_ids']
            if any(not isinstance(value,str) or not re.fullmatch(r'[a-f0-9]{40}',value,re.I) for value in paper_ids) \
                    or len(paper_ids)!=len(set(value.casefold() for value in paper_ids)) \
                    or seen.intersection(value.casefold() for value in paper_ids):
                raise ValueError('Invalid bulk history identifiers')
            seen.update(value.casefold() for value in paper_ids);current=state['parent']
    except (ServiceError,ValueError,UnicodeDecodeError):
        raise ServiceError('invalid_cursor','Bulk cursor history is unavailable or invalid') from None
    return seen


def _bulk_history_seen(adapter,history_ref):
    cached=getattr(adapter,'_bulk_history_cache',None)
    if isinstance(cached,tuple) and len(cached)==2 and cached[0]==history_ref and isinstance(cached[1],frozenset):
        return cached[1]
    return frozenset(_read_bulk_history(adapter,history_ref))


def _read_bulk_cursor(adapter,cursor,query,options,export):
    try:
        manifest,data=adapter.store.read(cursor)
        state=json.loads(data)
    except (ServiceError,ValueError,UnicodeDecodeError):
        raise ServiceError('invalid_cursor','Use the bulk cursor returned for this query and options') from None
    if manifest.get('source')!=adapter.source or manifest.get('role')!=BULK_CURSOR_ROLE or manifest.get('version')!=2 \
            or not isinstance(state,dict) or state.get('version')!=2 or state.get('source')!=adapter.source or state.get('query')!=query \
            or state.get('options')!=options or state.get('export')!=export:
        raise ServiceError('invalid_cursor','Bulk cursor belongs to another source, query, options, or export')
    required={'response_ref':str,'index':int,'native_cursor':(str,type(None)),'total_estimate':int,'history_ref':str}
    if any(not isinstance(state.get(key),kind) for key,kind in required.items()) or state['index']<0 \
            or state['total_estimate']<0:
        raise ServiceError('invalid_cursor','Bulk cursor state is invalid')
    try:
        proof_manifest,raw_bytes=adapter.store.read(state['response_ref'])
        raw=json.loads(raw_bytes)
    except (ServiceError,ValueError,UnicodeDecodeError):
        raise ServiceError('invalid_cursor','Bulk cursor provider page is unavailable') from None
    if proof_manifest.get('source')!=adapter.source or proof_manifest.get('role')!='provider_response' or not isinstance(raw,dict):
        raise ServiceError('invalid_cursor','Bulk cursor does not refer to a Semantic Scholar provider page')
    rows=raw.get('data')
    if not isinstance(rows,list) or state['index']>len(rows):
        raise ServiceError('invalid_cursor','Bulk cursor position is outside its provider page')
    proof={'ref':state['response_ref'],**proof_manifest}
    return state,rows,proof


def _bulk_search(adapter,query,options,limit,cursor,export):
    state=None;rows=None;proof=None;native_cursor=None;index=0;history_ref=None;total=None
    if cursor:
        if not cursor.startswith('scholarly://artifact/'):
            raise ServiceError('invalid_cursor','Use the bound bulk cursor returned by this server')
        state,rows,proof=_read_bulk_cursor(adapter,cursor,query,options,export)
        index=state['index'];native_cursor=state['native_cursor'];history_ref=state['history_ref'];total=state['total_estimate']
    if rows is None or index==len(rows):
        params={'query':query,**{k:v for k,v in options.items() if k not in ('kind','openAccessPdf')}}
        if native_cursor:params['token']=native_cursor
        params.setdefault('fields',PAPER_FIELDS)
        flag=options.get('openAccessPdf')
        if flag is True:params['openAccessPdf']=''
        elif flag is not None and flag is not False:raise ServiceError('invalid_options','openAccessPdf must be true, false or null; false leaves the filter off')
        if export=='bibtex':params['fields']+=',citationStyles'
        raw,proof=adapter.request(BASE+'search/bulk',params=params)
        rows=raw.get('data') if isinstance(raw,dict) else None
        following=raw.get('token') if isinstance(raw,dict) else None
        total=raw.get('total') if isinstance(raw,dict) else None
        if not isinstance(rows,list) or len(rows)>1000 or any(not isinstance(row,dict) for row in rows) or type(total) is not int or total<0:
            raise ServiceError('invalid_response','Semantic Scholar bulk search returned an invalid native page',evidence=proof)
        paper_ids=[row.get('paperId') for row in rows]
        if any(not isinstance(value,str) or not re.fullmatch(r'[a-f0-9]{40}',value,re.I) for value in paper_ids):
            raise ServiceError('invalid_response','Semantic Scholar bulk search returned a paper without a valid paper ID',evidence=proof)
        folded_ids=[value.casefold() for value in paper_ids]
        if len(folded_ids)!=len(set(folded_ids)):
            raise ServiceError('inconsistent_pagination','Semantic Scholar repeated a paper in one bulk page',evidence=proof)
        if following is not None and (not isinstance(following,str) or not following):
            raise ServiceError('invalid_response','Semantic Scholar bulk search returned an invalid continuation token',evidence=proof)
        if following is not None and following==native_cursor:
            raise ServiceError('inconsistent_pagination','Semantic Scholar repeated its bulk continuation token',evidence=proof)
        if not rows and following is not None:
            raise ServiceError('incomplete_response','Semantic Scholar returned an empty bulk page with a continuation token',evidence=proof)
        seen=_bulk_history_seen(adapter,history_ref) if history_ref else frozenset()
        if seen.intersection(folded_ids):
            raise ServiceError('inconsistent_pagination','Semantic Scholar repeated a paper across bulk pages',evidence=proof)
        if rows:
            history_ref=_bulk_history(adapter,history_ref,paper_ids,proof)
            adapter._bulk_history_cache=(history_ref,seen.union(folded_ids))
        index=0;native_cursor=following
    selected=rows[index:index+limit];next_index=index+len(selected)
    has_more=next_index<len(rows) or native_cursor is not None
    next_cursor=None
    if has_more:
        next_cursor=_bulk_cursor(adapter,{'version':2,'source':adapter.source,'query':query,'options':options,'export':export,
            'response_ref':proof['ref'],'index':next_index,'native_cursor':native_cursor,'total_estimate':total,
            'history_ref':history_ref},proof)
    else:
        cached=getattr(adapter,'_bulk_history_cache',None)
        if isinstance(cached,tuple) and cached[0]==history_ref:
            del adapter._bulk_history_cache
    result=adapter.page(selected,total,proof,query,options,None if cursor else 0,limit,cursor=next_cursor,more=has_more)
    result.update(records_kind='bulk',total_is_estimate=True,
        native_page={'received':len(rows),'selected_start':index,'selected':len(selected),'evidence_ref':proof['ref']},
        native_export_scope='evidence is the full provider batch; records is the exact caller window')
    if export=='bibtex':
        result['export']=native_bibtex(adapter,selected,proof)
        if result['export']['errors']:result['status']='partial'
        return result
    return adapter.export_page(result,export)


def search(adapter,query,*,options,start,limit,cursor,export):
    adapter.validate(options,start,limit)
    if 'fields' in options and not isinstance(options['fields'],str):raise ServiceError('invalid_options','fields must be a comma-separated string')
    kind=options.get('kind','papers')
    if kind not in ('papers','bulk','references','citations'):raise ServiceError('invalid_options','kind must be papers, bulk, references or citations')
    if kind=='bulk':
        if start!=0:raise ServiceError('invalid_range','Bulk search uses its native cursor and requires start=0')
        return _bulk_search(adapter,query,options,limit,cursor,export)
    if cursor:raise ServiceError('invalid_cursor','Semantic Scholar relevance and relation searches use start offsets')
    if kind=='papers' and limit>100:raise ServiceError('invalid_range','Paper search limit is 1..100; relation search allows 1..1000')
    if 'sort' in options:raise ServiceError('invalid_options','sort is available only for kind=bulk')
    params={'offset':start,'limit':limit,**{k:v for k,v in options.items() if k not in ('kind','openAccessPdf')}}
    if kind=='papers':
        params.update(query=query);params.setdefault('fields',PAPER_FIELDS)
        flag=options.get('openAccessPdf')
        if flag is True:params['openAccessPdf']=''
        elif flag is not None and flag is not False:raise ServiceError('invalid_options','openAccessPdf must be true, false or null; false leaves the filter off')
        if export=='bibtex':params['fields']+=',citationStyles'
        url=BASE+'search'
    else:
        allowed={'kind','fields'}|({'publicationDateOrYear'} if kind=='citations' else set())
        if set(options)-allowed:raise ServiceError('invalid_options','These filters do not apply to the selected relation search')
        if export not in (None,'json','native'):raise ServiceError('export_not_implemented','Relation pages support json/native export',status='not_implemented')
        identifier=paper_identifier(query)
        if identifier is None:raise ServiceError('invalid_target','Relation search query must identify one paper')
        url=BASE+quote(identifier,safe='')+'/'+kind;params.setdefault('fields',EDGE_FIELDS)
    raw,proof=adapter.request(url,params=params)
    rows=raw.get('data');following=raw.get('next')
    if not isinstance(rows,list) or len(rows)>limit or raw.get('offset')!=start:
        raise ServiceError('range_mismatch','Semantic Scholar returned a different result window',evidence=proof)
    if following is not None and (type(following) is not int or following<=start):
        raise ServiceError('range_mismatch','Semantic Scholar next offset did not advance',evidence=proof)
    total=raw.get('total') if kind=='papers' else None
    result=adapter.page(rows,total,proof,query,options,start,limit,more=following is not None)
    result['records_kind']=kind
    if following is not None:result['next']={'start':following}
    elif total is not None and start+len(rows)<total:result.update(has_more=True,next=None,continuation_limited=True)
    if kind!='papers':
        key='citedPaper' if kind=='references' else 'citingPaper'
        result['preview']=[{key:row.get(key)} for row in rows[:3]]
    if export=='bibtex':
        result['export']=native_bibtex(adapter,rows,proof)
        if result['export']['errors']:result['status']='partial'
        return result
    return adapter.export_page(result,export)


def references(adapter,paper_id,reported,proof):
    rows=[];refs=[];offset=0;errors=[];complete=False
    while True:
        try:page=adapter.search(paper_id,options={'kind':'references'},start=offset,limit=1000)
        except ServiceError as exc:errors.append(exc.result);break
        rows.extend(json.loads(adapter.store.read(page['records']['ref'])[1]));refs.append(page['evidence']['ref'])
        if not page['next']:complete=True;break
        offset=page['next']['start']
    if complete and reported is not None and reported!=len(rows):
        errors.append({'status':'error','code':'relation_count_mismatch','reason':'Reference endpoint count differs from paper metadata'})
    artifact=adapter.store.put(encoded(rows),'application/json',adapter.source,proof['url'],role='references',paper_id=paper_id,evidence_refs=refs,metadata_ref=proof['ref'])
    return {'status':'partial' if errors else 'available' if rows else 'not_found','artifact':artifact,'reference_count':len(rows),
            'reported_reference_count':reported,'errors':errors,'complete':complete,
            'next':None if complete else {'source':adapter.source,'query':paper_id,'options':{'kind':'references'},'start':offset,'limit':1000},
            'scope':'Outgoing indexed references. Use search kind=citations for a bounded incoming citation window.'}


def fetch(adapter,target,*,parts):
    from api_adapters import doi
    if set(parts)-{'metadata','abstract','export','supplementary','fulltext'}:raise ServiceError('invalid_parts','Unknown requested content')
    identifier=paper_identifier(target)
    if identifier is None:
        # Name resolution adapts the documented hyphen limitation; explicit search queries stay literal.
        normalized=target.replace('-',' ')
        raw,proof=adapter.request(BASE+'search/match',params={'query':normalized,'fields':MATCH_FIELDS})
        rows=raw.get('data') if isinstance(raw,dict) else None
        if not isinstance(rows,list) or len(rows)>1 or any(not isinstance(row,dict) for row in rows):
            raise ServiceError('invalid_response','Semantic Scholar title match returned an invalid candidate set',evidence=proof)
        result=adapter.page(rows,len(rows),proof,normalized,{'kind':'title_match'},0,1,more=False)
        result['requested_target']=target
        result['status']='selection_required' if result['received'] else 'not_found';return result
    fields=list(IDENTITY_FIELDS)
    if 'metadata' in parts:fields.extend(METADATA_FIELDS)
    if 'abstract' in parts:fields.append('abstract')
    if 'supplementary' in parts and 'referenceCount' not in fields:fields.append('referenceCount')
    if 'export' in parts:fields.append('citationStyles')
    batch,proof=adapter.request(BASE+'batch',params={'fields':','.join(fields)},json_body={'ids':[identifier]})
    if not isinstance(batch,list) or len(batch)!=1:
        raise ServiceError('invalid_response','Semantic Scholar batch lookup returned a different result count',evidence=proof)
    raw=batch[0]
    if raw is None:
        raise ServiceError('not_found_at_source','Target was not found at this source',status='not_found',source=adapter.source,evidence=proof)
    if not isinstance(raw,dict):
        raise ServiceError('invalid_response','Semantic Scholar batch lookup returned an invalid paper record',evidence=proof)
    returned=raw.get('paperId') if isinstance(raw,dict) else None
    if not isinstance(returned,str) or not re.fullmatch(r'[a-f0-9]{40}',returned,re.I):
        raise ServiceError('invalid_response','Semantic Scholar returned no paper ID',evidence=proof)
    if ':' not in identifier:
        matches=returned.casefold()==identifier.casefold()
    else:
        kind,value=identifier.split(':',1);aliases={k.casefold():v for k,v in (raw.get('externalIds') or {}).items()}
        observed=aliases.get(kind.casefold(),raw.get('corpusId') if kind=='CorpusId' else None)
        matches=observed is not None and str(observed).casefold()==value.casefold()
        if kind=='DOI' and observed:
            try:matches=doi(str(observed)).casefold()==value.casefold()
            except ServiceError:matches=False
    if not matches:raise ServiceError('identity_mismatch','Semantic Scholar metadata does not match the requested identifier',evidence=proof)
    result=adapter.fetched([raw],proof,parts,('metadata',)+(('abstract',) if raw.get('abstract') else ()))
    result['identity']={'requested':target,'paper_id':returned,'external_ids':raw.get('externalIds')}
    if 'abstract' in parts and not raw.get('abstract'):result['components']['abstract']={'status':'not_found','reason':'This Semantic Scholar record has no abstract'}
    if 'export' in parts:result['components']['export']=native_bibtex(adapter,[raw],proof)
    if 'supplementary' in parts:result['components']['supplementary']=references(adapter,returned,raw.get('referenceCount'),proof)
    states={c['status'] for c in result['components'].values()}
    result['status']='ok' if not states or states=={'available'} else 'not_found' if states=={'not_found'} else 'partial'
    return result
