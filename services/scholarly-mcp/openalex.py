"""OpenAlex native aggregation, work identity and mechanical abstract reconstruction."""
import re
from urllib.parse import urlsplit,unquote,quote
from scholarly import ServiceError,encoded


def abstract_text(index):
    if not isinstance(index,dict):raise ServiceError('invalid_abstract','OpenAlex abstract index is not an object')
    words={}
    for word,positions in index.items():
        if not isinstance(word,str) or not isinstance(positions,list):
            raise ServiceError('invalid_abstract','OpenAlex abstract token positions have an unexpected structure')
        for position in positions:
            if type(position) is not int or position<0 or position in words:
                raise ServiceError('invalid_abstract','OpenAlex abstract contains invalid or overlapping positions')
            words[position]=word
    if any(i not in words for i in range(len(words))):
        raise ServiceError('incomplete_abstract','OpenAlex abstract positions have gaps; missing words are not invented')
    return ' '.join(words[i] for i in range(len(words)))


def search(adapter,query,*,options,start,limit,cursor,export):
    adapter.validate(options,start,limit)
    grouped=bool(options.get('group_by'))
    if (cursor or grouped) and start:
        raise ServiceError('invalid_range','Use start=0 with cursor or group_by; continue with the returned cursor')
    if grouped and any(k in options for k in ('select','sort')):
        raise ServiceError('invalid_options','select/sort apply to work records; grouped cursor results follow native key order')
    params={'per_page':limit,**options}
    if query:params['search']=query
    if grouped or cursor:
        params['cursor']=cursor or '*'
        raw,proof=adapter.request('https://api.openalex.org/works',params=params)
        meta=raw.get('meta',{});rows=raw.get('group_by' if grouped else 'results')
        if not isinstance(rows,list) or len(rows)>limit:
            raise ServiceError('invalid_response','OpenAlex returned no requested result array',evidence=proof)
        if grouped and meta.get('groups_count') is not None and meta['groups_count']!=len(rows):
            raise ServiceError('range_mismatch','OpenAlex page group count differs from its buckets',evidence=proof)
        following=meta.get('next_cursor')
        result=adapter.page(rows,None if grouped else meta.get('count'),proof,query,options,0,limit,following,more=bool(following))
        result.update(start=None,pagination='cursor',records_kind='groups' if grouped else 'works')
        if grouped:
            result.update(matched_work_count=meta.get('count'),page_group_count=meta.get('groups_count'),preview=rows[:3])
        return adapter.export_page(result,export)
    page_number=start//limit+1;rows=[];proofs=[];total=None;errors=[]
    while len(rows)<limit:
        try:
            raw,proof=adapter.request('https://api.openalex.org/works',params={**params,'page':page_number})
        except ServiceError as exc:
            if not rows:raise
            errors.append(exc.result);break
        proofs.append(proof);meta=raw.get('meta',{});native=raw.get('results');reported=meta.get('count')
        if not isinstance(native,list) or type(reported) is not int or len(native)>limit:
            raise ServiceError('invalid_response','OpenAlex returned no work result page',evidence=proof)
        if len(proofs)>1 and total!=reported:
            raise ServiceError('range_mismatch','OpenAlex result count changed between pages',evidence=proofs)
        if meta.get('page',page_number)!=page_number or meta.get('per_page',limit)!=limit:
            raise ServiceError('range_mismatch','OpenAlex returned a different page or page size',evidence=proof)
        total=reported;first=(page_number-1)*limit
        if len(native)!=min(limit,max(0,total-first)):
            raise ServiceError('incomplete_response','OpenAlex work page length differs from its count',evidence=proof)
        rows.extend(row for i,row in enumerate(native,first) if start<=i<start+limit)
        if len(native)<limit or first+len(native)>=total:break
        page_number+=1
    result=adapter.page(rows,total,proofs[0],query,options,start,limit,evidence_refs=[p['ref'] for p in proofs])
    result['records_kind']='works'
    if len(proofs)>1:result['evidence']={'artifacts':proofs}
    if errors:result.update(status='partial',errors=errors)
    return adapter.export_page(result,export)


def fetch(adapter,target,*,parts):
    from api_adapters import doi
    value=target.strip();requested_doi=None
    if value.startswith(('http://','https://')):
        parsed=urlsplit(value)
        if parsed.username or parsed.password or parsed.port not in (None,80,443):
            raise ServiceError('invalid_target','Use an ordinary OpenAlex work or DOI URL')
        if parsed.hostname in ('openalex.org','api.openalex.org'):
            value=unquote(parsed.path).strip('/').removeprefix('works/')
            if not re.fullmatch(r'W\d+',value,re.I):raise ServiceError('invalid_target','This OpenAlex URL identifies no single work')
        elif parsed.hostname in ('doi.org','dx.doi.org'):
            value=doi(value)
        else:raise ServiceError('source_boundary','Select an OpenAlex record or DOI')
    value=value.removeprefix('works/')
    if value.startswith(('10.','doi:')):
        requested_doi=doi(value);lookup='https://doi.org/'+requested_doi
    elif re.fullmatch(r'W\d+',value,re.I):lookup=value.upper()
    else:
        result=adapter.search(value,options={},limit=5)
        result['status']='selection_required' if result['received'] else 'not_found'
        return result
    raw,proof=adapter.request('https://api.openalex.org/works/'+quote(lookup,safe=''))
    if not isinstance(raw,dict) or not re.fullmatch(r'https://openalex\.org/W\d+',raw.get('id','')):
        raise ServiceError('invalid_response','OpenAlex returned no canonical work ID',evidence=proof)
    returned=raw['id'].rsplit('/',1)[1];redirected=False
    if requested_doi:
        try:observed=doi(raw.get('doi') or '')
        except ServiceError:raise ServiceError('identity_mismatch','OpenAlex returned no DOI for the requested DOI',evidence=proof) from None
        if observed.casefold()!=requested_doi.casefold():
            candidate=adapter.page([raw],1,proof,'',{},0,1)
            candidate.update(status='selection_required',reason='OpenAlex resolved this DOI to a work with a different canonical DOI',requested_doi=requested_doi,canonical_doi=observed)
            return candidate
    elif returned!=lookup:
        redirected=urlsplit(proof['url']).path.rstrip('/').endswith('/'+returned)
        if not redirected:raise ServiceError('identity_mismatch','OpenAlex returned a different work without a canonical redirect',evidence=proof)
    result=adapter.fetched([raw],proof,parts,('metadata','export'))
    result['identity']={'requested':target,'work_id':returned,'doi':raw.get('doi'),'canonical_redirect':redirected}
    if 'abstract' in parts:
        index=raw.get('abstract_inverted_index')
        if not index:
            component={'status':'not_found','reason':'This OpenAlex record has no abstract index'}
        else:
            try:
                content=abstract_text(index)
                artifact=adapter.store.put(content,'text/plain',adapter.source,proof['url'],role='reconstructed_abstract',work_id=returned,metadata_ref=result['records']['ref'])
                component={'status':'available','artifact':artifact,'content_kind':'openalex_indexed_abstract','spacing':'Tokens ordered by source positions and joined with single spaces'}
            except ServiceError as exc:component=exc.result
        result['components']['abstract']=component
    if 'supplementary' in parts:
        references=raw.get('referenced_works') or [];related=raw.get('related_works') or []
        if not isinstance(references,list) or not isinstance(related,list):
            component={'status':'error','code':'invalid_response','reason':'OpenAlex relationships were not arrays'}
        else:
            artifact=adapter.store.put(encoded({'referenced_works':references,'related_works':related}),'application/json',adapter.source,proof['url'],role='work_relationships',work_id=returned,metadata_ref=result['records']['ref'])
            component={'status':'available' if references or related else 'not_found','artifact':artifact,'reference_count':len(references),'related_count':len(related),
                       'scope':'Indexed outgoing references and related works keep separate arrays; no linked work is fetched'}
        result['components']['supplementary']=component
    states={c['status'] for c in result['components'].values()}
    result['status']='ok' if not states or states=={'available'} else 'not_found' if states=={'not_found'} else 'partial'
    return result
