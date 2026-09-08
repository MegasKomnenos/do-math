"""Browser collection and conservative evidence classification for g08."""
import re
import unicodedata
import html
import fitz
import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qs, parse_qsl, urlencode
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

ROOT=Path(__file__).parent
BASE=ROOT.parents[1]
ASSIGNMENT=json.loads((ROOT/'assignment.json').read_text(encoding='utf-8-sig'))
RAW=BASE/ASSIGNMENT['raw_root']
MS_SEARCH='https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/publications-search'
SUMMON='https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q='

def tex_literals(value):
    value=html.unescape(re.sub(r'<[^>]+>','',value))
    value=value.replace('´ı','í')
    value=value.replace('\\cprime',"'").replace('ʹ',"'")
    for command,symbol in [('dots','…'),('epsilon','ϵ'),('Gamma','Γ'),('Omega','Ω')]:
        value=re.sub(r'\\'+command+r'\b',symbol,value)
    value=re.sub(r'\\aa\b\s*','å',value)
    value=re.sub(r'\\o\b\s*','ø',value)
    value=re.sub(r'\\(?:rm|bf|it|sb)\b\s*','',value)
    value=re.sub(r'\\overline\s*\{\s*([A-Za-z])\s*\}',r' overline \1 ',value)
    value=re.sub(r'([A-Za-z])\s*(?:[¯̅]\s*)+',r' overline \1 ',value)
    value=re.sub(r'\\circledR\b','®',value)
    value=re.sub(r'\\[;, ]',' ',value)
    return value

def normalize_title(value):
    value=tex_literals(value)
    value=re.sub(r'\\cyr\b','',value)
    value=re.sub(r'\\[vcuHkbr](?:\s+|(?=\{))','',value)
    value=value.replace('\\Omega','Ω')
    value=unicodedata.normalize('NFKD',value).casefold()
    cyr=dict(zip('абвгдежзийклмнопрстуфхцчшщъыьэюя',['a','b','v','g','d','e','zh','z','i','i','k','l','m','n','o','p','r','s','t','u','f','kh','ts','ch','sh','shch','','y','','e','yu','ya']))
    value=''.join(cyr.get(c,c) for c in value).replace('ł','l').replace('ø','o')
    return ''.join(c for c in value if c.isalnum())

def named_authors(paper):
    return [a for a in paper['authors'] if a.strip().casefold() not in {'et al.','et al','others'}]

def author_matches(name,text):
    parts=[name.split(',')[0]] if ',' in name else name.split()
    return all(normalize_title(part) in normalize_title(text) for part in parts)

def document_creators(doc):
    entries=(doc.get('authors') or [])+(doc.get('editors') or [])+(doc.get('corporate_authors') or [])
    return '; '.join(a.get('fullname','') if isinstance(a,dict) else str(a) for a in entries)

def response_documents(paper,response):
    matches=[]
    for doc in response.get('documents',[]):
        title=doc.get('full_title') or doc.get('title') or ''
        authors=document_creators(doc)
        years='; '.join(doc.get('publication_years') or [])
        bound=publisher_identity(paper,title,authors,years,SUMMON)
        if not bound and paper.get('record_type') in {'book','proceedings'}:
            isbn=lambda value:re.sub(r'[-\s]','',str(value)).lower()
            same_isbn=bool({isbn(x) for x in paper.get('identifiers',{}).get('isbn',[])} & {isbn(x) for x in doc.get('isbns') or []})
            main_title=re.split(r'[:：]',title,maxsplit=1)[0]
            bound=same_isbn and normalize_title(main_title)==normalize_title(plain_title(paper['title'])) and str(paper.get('year')) in years and all(author_matches(a,authors) for a in named_authors(paper))
        if not bound:
            continue
        if paper.get('record_type') in {'book','proceedings'} and 'book' not in (doc.get('content_type') or '').lower():
            continue
        expected_dois={x.lower() for x in paper.get('identifiers',{}).get('doi',[])}
        actual_dois={x.lower() for x in doc.get('dois') or []}
        if expected_dois and actual_dois and not expected_dois.intersection(actual_dois):
            continue
        span=re.fullmatch(r'(\d+)\s*[-–]+\s*(\d+)',paper.get('publication',{}).get('pages') or '')
        if span and doc.get('start_pages') and doc.get('end_pages'):
            if span[1] not in [str(p).rstrip('-– ') for p in doc['start_pages']] or span[2] not in doc['end_pages']:
                continue
        matches.append(doc)
    return matches

def bind_mr(paper, heading, bibliography):
    expected=paper['publication']['source_record']['record_id']
    match=re.search(r'MR0*(\d+)',heading)
    if not match or int(match[1]) != int(expected.removeprefix('MR')):
        return False
    return (all(author_matches(a,bibliography) for a in named_authors(paper)) and
            normalize_title(plain_title(paper['title'])) in normalize_title(bibliography) and (paper['year'] is None or str(paper['year']) in bibliography))

def abstract_from_review(review):
    review=re.sub(r'^(?:Review|Summary)\s*\n','',review.strip(),count=1)
    prefix=re.match(r'Summary(?: \([^\n]*\))?:\s*',review)
    if not prefix:
        return None
    quoted=review[prefix.end():]
    if quoted.startswith('``'):
        depth=0
        for match in re.finditer(r"``|''",quoted):
            depth+=1 if match[0]=='``' else -1
            if depth==0:
                return quoted[2:match.start()].strip()
        return None
    match=re.match(r'["“](.+?)["”](?:\s*\nReferences|\s*$)',quoted,re.S)
    return match[1].strip() if match else None

def valid_pdf(data):
    if not data.startswith(b'%PDF-'):
        return False
    try:
        with fitz.open(stream=data,filetype='pdf') as doc:
            return len(doc)>0
    except Exception:
        return False

def can_resume(record):
    return all(record.get(c,{}).get('status') not in {None,'unresolved'} for c in ['identity','abstract','fulltext'])

def save_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    tmp.replace(path)

def artifact(pid,name,value,url,kind='detail-page',media_type='text/plain'):
    data=value if isinstance(value,bytes) else value.encode('utf-8')
    if not data:
        data=b'Observation: the page body was empty when captured; no article content was recovered from this response.'
        kind='empty-page-observation'
    filename=Path(name)
    path=RAW/pid/(filename.stem+'-'+hashlib.sha256(data).hexdigest()[:16]+filename.suffix)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(data)
    return {'path':path.relative_to(BASE).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'url':public_url(url),'kind':kind,'media_type':media_type}

def public_url(url):
    parts=urlsplit(url)
    query=[(key,value) for key,value in parse_qsl(parts.query,keep_blank_values=True) if not re.search(r'token|ticket|session|signature|credential|authorization|__cf_chl',key,re.I)]
    fragment=parts.fragment
    if re.search(r'(?:^|[?&])(access_token|id_token|refresh_token|session)=',fragment,re.I):
        fragment=''
    return urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(query),fragment))

def plain_title(title):
    title=tex_literals(title)
    title=re.sub(r'[{}$]','',title)
    title=re.sub(r'\s*\[(?:MR\d|translation of).*\]\s*$','',title,flags=re.I|re.S)
    title=re.sub(r'\\cyr\b','',title)
    title=re.sub(r'\\[vcuHkbr](?:\s+|(?=\{))','',title)
    title=re.sub(r'\\l\s*','l',title)
    title=re.sub(r'\\[\x27`\x22^~=]','',title)
    return re.sub(r'\s+',' ',title).strip()

def first_query(paper):
    if paper.get('identifiers',{}).get('doi'):
        return paper['identifiers']['doi'][0]
    if paper.get('identifiers',{}).get('isbn'):
        return paper['identifiers']['isbn'][0]
    return '"'+plain_title(paper['title'])+'" '+(paper['authors'][0].split(',')[0] if paper['authors'] else '')

def capture_text(page):
    main=page.locator('main')
    if main.count():
        return main.first.inner_text(timeout=10000)
    return page.locator('body').inner_text(timeout=10000)

def read_heading(page):
    return page.locator('.title').first.inner_text()

def article_scope(page,mr):
    groups=page.locator('div.article')
    for group in groups.all():
        heading=group.locator('h1').first.inner_text()
        match=re.search(r'MR\s*0*(\d+)',heading)
        if match and int(match[1])==int(mr.removeprefix('MR')):
            return group
    if groups.count():
        raise RuntimeError('Requested MR section was not found in the grouped review page')
    return page

def article_link(scope):
    links=scope.get_by_role('link',name='Article',exact=True)
    return links.first.get_attribute('href') if links.count() else None

def click_article(page,scope):
    before=list(page.context.pages)
    old_url=page.url
    link=scope.get_by_role('link',name='Article',exact=True)
    (link.first if link.count() else scope.get_by_role('button',name='Article',exact=True).first).click()
    deadline=time.monotonic()+10
    while time.monotonic()<deadline:
        new=[p for p in page.context.pages if p not in before]
        if new:
            new[-1].wait_for_load_state('domcontentloaded',timeout=25000)
            return new[-1]
        if page.url!=old_url:
            page.wait_for_load_state('domcontentloaded',timeout=25000)
            return page
        page.wait_for_timeout(100)
    return None

def summon_abstract(page):
    node=page.locator('#quick-look-abstract [data-aid=abstract]')
    return node.inner_text().strip() if node.count() else None

def preserve_database_abstract(paper,result,abstract,url,doc):
    value=abstract.get('abstract','').strip()
    if len(value)<=80:
        return
    asset=artifact(paper['paper_id'],'database-abstract-candidate.txt',value,url,'database-abstract-candidate')
    result['evidence'].append(asset)
    candidate={'source_kind':'database_indexing_abstract','attribution':abstract.get('attribution',''),'authorship':'unknown','artifacts':[asset],'binding':doc,'status':'needs_review'}
    candidates=result.setdefault('database_abstract_candidates',[])
    if not any(c['artifacts'][0]['sha256']==asset['sha256'] for c in candidates):
        candidates.append(candidate)

def abstract_quality_issue(value):
    if value.strip().startswith('The following sections are included:'):
        return 'contents_only'
    if '▪' in value or '\ufffd' in value:
        return 'missing_formula_or_replacement_character'
    return None

def publisher_identity(paper,title,authors,year,url):
    if normalize_title(plain_title(paper['title'])) != normalize_title(title):
        return False
    if str(paper['year']) not in re.findall(r'\b\d{4}\b',year):
        return False
    if paper.get('record_type') in {'book','proceedings'} and ('/article/' in url or '/doi/abs/' in url):
        return False
    return all(author_matches(a,authors) for a in named_authors(paper))

def publisher_restriction(text):
    return any(x in text.lower() for x in ['buy now','purchase','access through your institution','log in to access','get access','sign in to access','rent this article','preview of subscription content','log in via an institution'])

def pdf_links(page):
    galley=page.locator('a.obj_galley_link.pdf[href]')
    if galley.count():
        return galley.evaluate_all('(els)=>els.map(e=>({text:e.innerText,url:e.href}))')
    links=page.locator('a[href]').evaluate_all('(els)=>els.filter(e=>e.offsetWidth||e.offsetHeight).map(e=>({text:e.innerText,url:e.href}))')
    return [x for x in links if not x['text'].strip().lower().startswith(('http://','https://')) and ('pdf' in x['text'].lower() or 'download chapter' in x['text'].lower()) and not any(t in (x['text']+' '+x['url']).lower() for t in ['preview','references','citation','supplement','review'])]

def viewer_download_link(page):
    link=page.locator('a.download[href]')
    return link.first.evaluate('(e)=>e.href') if link.count() else None

def attempt(result,query,url,outcome):
    result['attempts'].append({'method':'playwright','query':query,'url':public_url(url),'outcome':outcome})

def publisher_title(page):
    heading=page.locator('h1').first.inner_text().strip() if page.locator('h1').count() else ''
    if heading:
        return heading
    node=page.locator('meta[name="citation_title"]').first
    title=node.get_attribute('content') if node.count() else ''
    # The publisher's bibliographic title must also be visible in the body.
    return title if title and normalize_title(title) in normalize_title(capture_text(page)) else ''

def _inspect_publisher(page,paper,result,byline=None,pdf_candidates=None):
    """Observe a linked publisher page; downloading is restricted to visible links."""
    pid=paper['paper_id']
    page.wait_for_timeout(1000)
    text=capture_text(page)
    url=public_url(page.url)
    result['evidence'].append(artifact(pid,'publisher.txt',text,url))
    if not text.strip():
        result['unvisited_link']=True
        attempt(result,paper['title'],url,'Source rendered an empty body; loading or direct-PDF inspection remains unresolved')
        return
    blocked=next((s for s in ['Unusual Traffic','Access Denied','Verify you are human','Checking your browser','Just a moment','Robot Check','403 Forbidden','Access blocked'] if s.casefold() in text.casefold()),None)
    if blocked:
        attempt(result,paper['title'],url,'Publisher access barrier: '+blocked)
        result['fulltext']={'status':'unavailable','reason':'Linked publisher page shows '+blocked}
        return
    h=publisher_title(page)
    meta=page.locator('meta[name^="citation_"]').evaluate_all('(els)=>els.map(e=>({name:e.name,value:e.content}))')
    author_metadata='; '.join(x['value'] for x in meta if x['name']=='citation_author')
    if byline is not None:author_metadata=byline
    year_metadata='; '.join(x['value'] for x in meta if x['name'] in ['citation_publication_date','citation_date','citation_year'])
    if page.locator('article > header .core-container').count():
        header=page.locator('article > header .core-container').inner_text()
        author_match=re.search(r'Authors?:\s*(.*?)Authors? Info',header,re.S)
        date_match=re.search(r'Published:\s*([^\n]+)',header)
        author_metadata=author_match[1] if author_match else ''
        year_metadata=date_match[1] if date_match else ''
    bound=publisher_identity(paper,h,author_metadata,year_metadata,url)
    result.setdefault('publisher_bindings',[]).append({'url':url,'title':h,'authors':author_metadata,'publication_date':year_metadata,'target_match':bound})
    if not bound:
        attempt(result,paper['title'],url,'Publisher heading does not yet bind the target title: '+h[:180])
        return
    abstract=page.locator('#Abs1-content, #abstract, section[aria-labelledby="abstract-heading"], .abstract, .abstractSection').all()
    for node in abstract:
        if node.is_visible():
            value=node.inner_text().strip()
            if len(value)>80 and not abstract_quality_issue(value) and not any(x in value.lower() for x in ['no abstract available','sign in to view']):
                value=re.sub(r'^Abstract\s*','',value).strip()
                result['abstract']={'status':'found','artifacts':[artifact(pid,'abstract.txt',value,url,media_type='text/plain')],'source_kind':'publisher-abstract'}
                break
    candidates=pdf_links(page) if pdf_candidates is None else pdf_candidates
    visits={'source_url':url,'discovered':len(candidates),'attempted':0,'remaining':len(candidates),'urls':[x['url'] for x in candidates]}
    result.setdefault('pdf_candidate_visits',[]).append(visits)
    for link in candidates:
        visits['attempted']+=1
        visits['remaining']-=1
        target=page.context.new_page()
        try:
            download_url=link['url']
            metrics=result.setdefault('collection_metrics',{})
            metrics['download_requests']=metrics.get('download_requests',0)+1
            response=page.context.request.get(link['url'],timeout=25000)
            data=response.body() if response else b''
            if not valid_pdf(data):
                target.goto(link['url'],wait_until='domcontentloaded',timeout=25000)
                nested=viewer_download_link(target)
                if nested:
                    download_url=nested
                    metrics['download_requests']+=1
                    data=page.context.request.get(nested,timeout=25000).body()
            if valid_pdf(data):
                with fitz.open(stream=data,filetype='pdf') as doc:
                    front='\n'.join(doc[i].get_text() for i in range(min(3,len(doc))))
                    pages=len(doc)
                title_ok=normalize_title(plain_title(paper['title'])) in normalize_title(front)
                author_ok=all(author_matches(a,front) for a in named_authors(paper))
                expected=paper.get('publication',{}).get('pages') or ''
                span=re.fullmatch(r'(\d+)\s*[-–]+\s*(\d+)',expected)
                total=re.fullmatch(r'(?:[ivxlcdm]+\+)?(\d+)',expected)
                full_span=(not span or pages>=int(span[2])-int(span[1])+1) and (not total or pages>=int(total[1]))
                if title_ok and author_ok and full_span:
                    result['fulltext']={'status':'found','artifacts':[artifact(pid,'fulltext.pdf',data,download_url,'fulltext','application/pdf')],'pdf_pages':pages,'validation':'PDF opens; first three pages contain target title and author; expected page span checked when numeric.'}
                    attempt(result,paper['title'],download_url,'Downloaded and verified complete PDF, '+str(pages)+' pages')
                    return
                result['evidence'].append(artifact(pid,'candidate-pdf-front.txt',front,download_url,'unconfirmed-pdf'))
                result['evidence'].append(artifact(pid,'candidate.pdf',data,download_url,'unconfirmed-pdf','application/pdf'))
                result['unvisited_link']=True
                attempt(result,paper['title'],download_url,f'PDF not counted: title={title_ok}, author={author_ok}, page_span={full_span}; pages={pages}')
            else:
                detail=capture_text(target)
                result['evidence'].append(artifact(pid,'download-response.txt',detail or 'Non-PDF response',link['url'],'download-failure'))
                attempt(result,paper['title'],link['url'],'Visible PDF link returned non-PDF page')
        except Exception as exc:
            result['unvisited_link']=True
            attempt(result,paper['title'],link['url'],'Download navigation failed: '+type(exc).__name__)
        finally:
            target.close()
    if publisher_restriction(text):
        result['fulltext']={'status':'unavailable','reason':'Target publisher page offers purchase or additional institutional/login access; no validated complete PDF was obtained.'}
    elif not candidates:
        result['fulltext']={'status':'not_found','reason':'Confirmed linked publisher detail has no visible complete-PDF download link; page evidence retained.'}
    attempt(result,paper['title'],url,'Inspected target publisher detail; PDF links discovered='+str(visits['discovered'])+', attempted='+str(visits['attempted'])+', remaining='+str(visits['remaining']))

def inspect_publisher(page,paper,result,byline=None,pdf_candidates=None):
    prior={k:result[k] for k in ['abstract','fulltext'] if result.get(k,{}).get('status')=='found'}
    started=time.monotonic()
    metrics=result.setdefault('collection_metrics',{})
    metrics['publisher_visits']=metrics.get('publisher_visits',0)+1
    try:
        return _inspect_publisher(page,paper,result,byline=byline,pdf_candidates=pdf_candidates)
    finally:
        metrics['publisher_seconds']=metrics.get('publisher_seconds',0)+time.monotonic()-started
        for key,value in prior.items():
            if result[key]['status']!='found':
                result[key]=value

def summon_query(page,paper,result,query,inspect_links=True):
    responses=[]
    def observe(response):
        if urlsplit(response.url).path=='/api/search':
            responses.append(response)
    def await_payload(expanded=False,page_number=None):
        deadline=time.monotonic()+35
        parsed={}
        while time.monotonic()<deadline:
            for response in reversed(responses):
                key=id(response)
                if key not in parsed:
                    try:
                        parsed[key]=response.json()
                    except Exception:
                        continue
                data=parsed[key]
                q=data.get('query',{})
                if q.get('original_query')!=query:
                    continue
                if expanded and parse_qs(q.get('query_string','')).get('s.ho')!=['f']:
                    continue
                if page_number is not None and q.get('page_number')!=page_number:
                    continue
                if response.status>=400:
                    raise RuntimeError('Actual UI search HTTP status '+str(response.status))
                return data
            page.wait_for_timeout(150)
        raise RuntimeError('No completed browser search response for the current query and required holdings scope')
    page.on('response',observe)
    try:
        page.goto(SUMMON,wait_until='domcontentloaded',timeout=30000)
        box=page.locator('input[name=q]:visible').first
        box.wait_for(timeout=30000)
        box.fill(query)
        box.press('Enter')
        data=await_payload()
        page.get_by_text('Done Loading Results',exact=True).wait_for(state='attached',timeout=25000)
        if parse_qs(data['query'].get('query_string','')).get('s.ho')!=['f']:
            if page.locator('#searchInfoBeyondHoldings').count():
                page.locator('#searchInfoBeyondHoldings').click()
            elif page.locator('#ho0').count():
                page.locator('#ho0').press('Space')
            else:
                raise RuntimeError('The holdings expansion UI is unavailable')
            data=await_payload(expanded=True)
        page.get_by_text('Done Loading Results',exact=True).wait_for(state='attached',timeout=25000)
        fields=['id','title','full_title','dois','isbns','authors','editors','corporate_authors','publication_years','content_type','abstracts','page_count','start_pages','end_pages','link','publication_title']
        if type(data.get('record_count')) is not int or not isinstance(data.get('documents'),list):
            raise RuntimeError('Actual UI response is missing record-count/document fields')
        pn=data['query'].get('page_number',1)
        capture={'original_query':query,'holdings_only':False,'record_count':data['record_count'],'page_numbers':[pn],'documents':[{k:d.get(k) for k in fields} for d in data['documents']]}
        def keep_capture():
            result['evidence'].append(artifact(paper['paper_id'],'summon-response.json',json.dumps(capture,ensure_ascii=False,indent=2),page.url,'ui-search-response','application/json'))
        keep_capture()
        identifiers=paper.get('identifiers',{}).get('doi',[])+paper.get('identifiers',{}).get('isbn',[])
        if query.startswith('(TitleCombined:') or query in identifiers:
            seen={tuple(d.get('id') for d in data['documents'])}
            while len(capture['documents'])<capture['record_count']:
                page.wait_for_timeout(600)
                next_link=page.locator('a[aria-label="다음"]:visible').first
                if not next_link.count() or next_link.get_attribute('aria-disabled')=='true':
                    raise RuntimeError('Declared search remainder has no enabled observed next-page link')
                next_link.click()
                pn+=1
                data=await_payload(expanded=True,page_number=pn)
                page.get_by_text('Done Loading Results',exact=True).first.wait_for(state='attached',timeout=25000)
                signature=tuple(d.get('id') for d in data.get('documents',[]))
                if not signature or signature in seen:
                    raise RuntimeError('Pagination returned an empty/repeated page before declared scope was covered')
                seen.add(signature)
                capture['page_numbers'].append(pn)
                capture['documents'].extend({k:d.get(k) for k in fields} for d in data['documents'])
                capture['record_count']=max(capture['record_count'],data['record_count'])
                keep_capture()
        result['evidence'].append(artifact(paper['paper_id'],'summon-search.txt',capture_text(page),page.url,'search-results'))
        result.setdefault('search_scope_checks',[]).append({'query':query,'url':page.url,'includes_non_subscribed':True,'original_query_verified':True})
        matches=response_documents(paper,capture)
        attempt(result,query,page.url,'Actual UI search response matched current query and ho=f; title/all named authors/year/available DOI/page boundaries matched '+str(len(matches))+' documents')
        for doc in matches:
            abstracts=doc.get('abstracts') or []
            for abstract in abstracts:
                preserve_database_abstract(paper,result,abstract,page.url,doc)
                value=abstract.get('abstract','').strip()
                if len(value)>80 and not abstract_quality_issue(value) and result['identity']['status']=='confirmed':
                    if paper.get('record_type') in {'book','proceedings'}:
                        continue # The saved DB abstract candidate requires content review, independent of record type.
                    component='abstract'
                    asset=artifact(paper['paper_id'],'summon-'+component+'.txt',value,page.url,component,'text/plain')
                    result[component]={'status':'found','source_kind':'Summon book-description field' if component=='description' else 'Summon full abstract field from observed UI response','artifacts':[asset],'attribution':abstract.get('attribution',''),'binding':{k:doc.get(k) for k in ['title','authors','publication_years','dois','start_pages','end_pages','content_type']}}
        link_docs=[]
        for doc in capture['documents']:
            authors=document_creators(doc)
            if normalize_title(doc.get('full_title') or doc.get('title') or '')==normalize_title(plain_title(paper['title'])) and all(author_matches(a,authors) for a in named_authors(paper)):
                link_docs.append(doc)
        for doc in (link_docs if inspect_links else []):
            link=doc.get('link')
            if link:
                target=page.context.new_page()
                try:
                    target.goto(link,wait_until='domcontentloaded',timeout=30000)
                    inspect_publisher(target,paper,result)
                except Exception as exc:
                    result['unvisited_link']=True
                    attempt(result,query,page.url,'Matched actual response link failed: '+type(exc).__name__)
                finally:
                    target.close()
    finally:
        page.remove_listener('response',observe)

def summon_search(page,paper,result):
    title_query='"'+plain_title(paper['title'])+'" '+(paper['authors'][0].split(',')[0] if paper['authors'] else '')
    for query in dict.fromkeys([first_query(paper),title_query]):
        summon_query(page,paper,result,query)
    result['summon_required_queries_complete']=True
    result['source_scope_version']='ui-response/1'

def collect(limit=None,stage='all',offset=0,stop_before=None,progress_name='progress.json'):
    papers=[json.loads(x) for x in (BASE/ASSIGNMENT['members_path']).read_text(encoding='utf-8-sig').splitlines()]
    (ROOT/'results').mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome',headless=True)
        ctx=browser.new_context(storage_state=ASSIGNMENT['browser_state'],accept_downloads=True)
        ctx.set_default_timeout(12000)
        page=ctx.new_page()
        page.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542',wait_until='domcontentloaded',timeout=30000)
        page.locator('#search_order').fill('MathSciNet')
        page.locator('#search_order').press('Enter')
        with ctx.expect_page(timeout=25000) as event:
            page.get_by_text('바로가기',exact=True).click()
        ms=event.value
        ms.wait_for_url('**/publications-search',timeout=40000)
        sm=ctx.new_page()
        count=0
        for paper in papers[offset:stop_before]:
            path=ROOT/'results'/f"{paper['paper_id']}.json"
            previous=json.loads(path.read_text(encoding='utf-8')) if path.exists() else None
            if previous and (stage=='mr' or (can_resume(previous) and previous.get('required_sources_complete') and previous.get('source_scope_version')=='ui-response/1' and previous.get('mr_link_scope_version')=='per-record/1')):
                continue
            pid=paper['paper_id']; mr=paper['publication']['source_record']['record_id']
            result={'schema_version':'kudos-recovery-result/1','paper_id':pid,'version_sha256':paper['version_sha256'],'identity':{'status':'unresolved','reason':'Live identity check pending'},'metadata':{k:paper.get(k) for k in ['title','authors','year','identifiers','publication','record_type']},'abstract':{'status':'unresolved','reason':'Detail and publisher inspection pending'},'fulltext':{'status':'unresolved','reason':'Original-article links and alternate search pending'},'attempts':[],'evidence':[]}
            if previous:
                result=json.loads(json.dumps(previous))
                result.pop('collection_error',None)
                result.pop('unvisited_link',None)
            try:
                ms.goto(MS_SEARCH,wait_until='domcontentloaded',timeout=30000)
                ms.locator('#searchTextInput').fill(mr)
                ms.locator('#searchTextInput').press('Enter')
                ms.wait_for_url('**/article?mr=*',timeout=22000)
                ms.locator('.bibliography').first.wait_for(timeout=22000)
                ms.wait_for_timeout(600)
                text=capture_text(ms)
                result['evidence'].append(artifact(pid,'mathscinet-detail.txt',text,ms.url))
                scope=article_scope(ms,mr)
                heading=read_heading(scope)
                bibliography=scope.locator('.bibliography').first.inner_text()
                result['evidence'].append(artifact(pid,'mathscinet-scoped-bibliography.txt',heading+'\n'+bibliography,ms.url,'mr-scoped-bibliography'))
                bound=bind_mr(paper,heading,bibliography)
                result['identity']={'status':'confirmed' if bound else 'unresolved','reason':'MR heading '+heading+'; bibliography author/year comparison '+str(bound),'observed_bibliography':bibliography}
                attempt(result,mr,ms.url,'MR search reached article; target identity comparison '+str(bound))
                grouped=ms.locator('div.article').count()>1
                review=ms.locator('.review-text').first
                if review.count():
                    review_text=review.inner_text()
                    result['review']={'source_kind':'MathSciNet grouped review' if grouped else 'MathSciNet review or source-labelled summary','grouped':grouped,'artifacts':[artifact(pid,'mathscinet-review.txt',review_text,ms.url,'review')]}
                    summary=None if grouped else abstract_from_review(review_text)
                    if summary and bound:
                        field='description' if paper.get('record_type') in {'book','proceedings'} else 'abstract'
                        result[field]={'status':'found','source_kind':'MathSciNet explicitly labelled Summary; translation qualifier retained in review evidence','artifacts':[artifact(pid,field+'.txt',summary,ms.url,media_type='text/plain')]}
                    else:
                        result['abstract']={'status':'unresolved','reason':'MathSciNet provides a review rather than an explicitly extractable author abstract; publisher/other source inspection pending.'}
                source_href=article_link(scope)
                button=scope.get_by_role('button',name='Article',exact=True)
                enabled=bool(source_href) or (button.count()>0 and button.first.is_enabled())
                result['mathscinet_article_link_enabled']=enabled
                result['mathscinet_article_href']=public_url(source_href) if source_href else None
                result['mr_link_scope_version']='per-record/1'
                if source_href and previous and not previous.get('mathscinet_article_link_enabled'):
                    result['mr_link_audit_correction']='The earlier button-only lookup did not inspect the enabled Article anchor. The per-record anchor is now explicitly inspected.'
                    for earlier in result['attempts']:
                        if earlier.get('outcome')=='Article button is disabled; MathSciNet supplies no original-article link':
                            earlier['outcome']='Superseded button-only parser inference: no enabled button was found; the actual Article anchor is checked by the per-record audit.'
                if stage=='all':
                    if enabled:
                        publisher=click_article(ms,scope)
                        if publisher:
                            try:
                                publisher.wait_for_load_state('domcontentloaded',timeout=25000)
                                inspect_publisher(publisher,paper,result)
                            finally:
                                if publisher is not ms:
                                    publisher.close()
                        else:
                            attempt(result,mr,ms.url,'Enabled Article button produced no new page')
                    else:
                        attempt(result,mr,ms.url,'Article button is disabled; MathSciNet supplies no original-article link')
                    if not previous or not previous.get('required_sources_complete') or previous.get('identity',{}).get('status')!='confirmed':
                        summon_search(sm,paper,result)
                    elif result.get('source_scope_version')!='ui-response/1':
                        summon_search(sm,paper,result)
                    for source_url in paper.get('source_urls',[]):
                        if previous and any(a.get('query')==source_url and a.get('outcome')=='Assigned source URL followed and resulting page inspected' for a in previous.get('attempts',[])):
                            continue
                        target=ctx.new_page()
                        try:
                            target.goto(source_url,wait_until='domcontentloaded',timeout=25000)
                            inspect_publisher(target,paper,result)
                            attempt(result,source_url,target.url,'Assigned source URL followed and resulting page inspected')
                        except Exception as exc:
                            result['unvisited_link']=True
                            attempt(result,source_url,source_url,'Assigned source URL did not finish: '+type(exc).__name__)
                        finally:
                            target.close()
                    result['required_sources_complete']=result.get('summon_required_queries_complete',False) and not result.get('unvisited_link',False)
                    if result['required_sources_complete'] and result['identity']['status']=='confirmed':
                        for component in ['abstract','fulltext']:
                            if result[component]['status']=='unresolved':
                                result[component]={'status':'not_found','reason':'MathSciNet MR detail, Summon including non-subscribed resources with available DOI/ISBN and title/author queries, assigned source URLs and observed matching source links were inspected; this component was not obtained within that required source scope. This is not a claim of absence on the entire internet.'}
                result['stage_completed']=stage
            except Exception as exc:
                detail='Browser collection exception: '+type(exc).__name__
                try:
                    text=capture_text(ms)
                    result['evidence'].append(artifact(pid,'exception-page.txt',text or detail,ms.url or MS_SEARCH,'failure-page'))
                except Exception:
                    result['evidence'].append(artifact(pid,'exception.txt',detail,MS_SEARCH,'failure'))
                attempt(result,mr,ms.url or MS_SEARCH,detail)
                result['collection_error']=detail
            if previous and result['identity']['status']=='confirmed':
                for component in ['abstract','fulltext']:
                    if previous[component]['status']=='found' and result[component]['status']!='found':
                        result[component]=previous[component]
            save_json(path,result)
            count+=1
            files=list((ROOT/'results').glob('*.json'))
            records=[json.loads(x.read_text(encoding='utf-8')) for x in files]
            progress={'stage':stage,'processed':len(records),'assigned':len(papers),'remaining':len(papers)-len(records),'abstract_found':sum(r['abstract']['status']=='found' for r in records),'fulltext_found':sum(r['fulltext']['status']=='found' for r in records),'unresolved':sum(any(r[c]['status']=='unresolved' for c in ['identity','abstract','fulltext']) for r in records),'last_paper_id':pid,'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g08/recover.py --stage all','updated_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())}
            save_json(ROOT/Path(progress_name).name,progress)
            print(json.dumps(progress,ensure_ascii=False),flush=True)
            if limit and count>=limit:
                break
            ms.wait_for_timeout(1000)
        browser.close()

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int)
    parser.add_argument('--stage',choices=['mr','all'],default='all')
    parser.add_argument('--offset',type=int,default=0)
    parser.add_argument('--stop-before',type=int)
    parser.add_argument('--progress-name',default='progress.json')
    args=parser.parse_args()
    collect(args.limit,args.stage,args.offset,args.stop_before,args.progress_name)
