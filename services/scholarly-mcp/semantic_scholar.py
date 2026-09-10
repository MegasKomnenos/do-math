"""Credential-free Semantic Scholar records, native citations and bounded graph pages."""
import json,re
from urllib.parse import urlsplit,quote
from scholarly import ServiceError,encoded,bibliography

BASE='https://api.semanticscholar.org/graph/v1/paper/'
PAPER_FIELDS='title,authors,year,abstract,externalIds,url,openAccessPdf,publicationTypes,citationCount,referenceCount,corpusId'
EDGE_FIELDS='title,authors,year,externalIds,contexts,intents,isInfluential'


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
            artifacts.append(artifact)
        except ServiceError as exc:errors.append({'paper_id':row.get('paperId'),**exc.result,'source_export':artifact})
        except Exception as exc:errors.append({'paper_id':row.get('paperId'),'status':'error','code':'invalid_native_citation','error_type':type(exc).__name__,'source_export':artifact})
    result={'status':'partial' if errors else 'available' if artifacts else 'not_found','artifacts':artifacts,'errors':errors}
    if artifacts:
        data=b'\n\n'.join(adapter.store.read(a['ref'])[1] for a in artifacts)
        combined=artifacts[0] if len(artifacts)==1 else adapter.store.put(data,'application/x-bibtex',adapter.source,proof['url'],role='native_citations',parent_refs=[a['ref'] for a in artifacts])
        result.update(combined);result['artifact']=combined
    return result


def search(adapter,query,*,options,start,limit,cursor,export):
    adapter.validate(options,start,limit)
    if cursor:raise ServiceError('invalid_cursor','Semantic Scholar uses start offsets for these search modes')
    kind=options.get('kind','papers')
    if kind not in ('papers','references','citations'):raise ServiceError('invalid_options','kind must be papers, references or citations')
    if kind=='papers' and limit>100:raise ServiceError('invalid_range','Paper search limit is 1..100; relation search allows 1..1000')
    if 'fields' in options and not isinstance(options['fields'],str):raise ServiceError('invalid_options','fields must be a comma-separated string')
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
        result=adapter.search(target.replace('-',' '),options={},limit=5)
        result['requested_target']=target
        result['status']='selection_required' if result['received'] else 'not_found';return result
    fields=PAPER_FIELDS+(',citationStyles' if 'export' in parts else '')
    raw,proof=adapter.request(BASE+quote(identifier,safe=''),params={'fields':fields})
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
