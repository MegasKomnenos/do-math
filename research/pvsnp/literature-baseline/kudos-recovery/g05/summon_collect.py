import argparse,html,json,re,time,unicodedata
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import pymupdf
from collect import BASE,WORK,artifact,save_json,save_progress,norm,pdf_valid,publisher_failure,safe_url,get_download
from acm_collect import pdf_identity

SUMMON='https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q='

def provider_candidate(prior,artifact_record):
    if prior.get('status')=='found':
        return dict(prior,provider_candidates=list(prior.get('provider_candidates',[]))+[artifact_record])
    return {'status':'unresolved','reason':'Provider abstract field requires content review; a field may contain a citation, excerpt or description rather than an actual abstract','candidate_artifacts':list(prior.get('candidate_artifacts',[]))+[artifact_record],'previous_judgment':prior.get('previous_judgment',prior)}

def clean(value):
    text=html.unescape(re.sub(r'</?mark(?:\s[^>]*)?>','',str(value),flags=re.I))
    return norm(''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c)))

def document_matches(paper,document):
    def title_key(value):return clean(value).removeprefix('technicalperspective').removesuffix('technicalperspective')
    if title_key(paper['title']) not in {title_key(document.get('title','')),title_key(document.get('full_title',''))}:return False
    dois=paper.get('identifiers',{}).get('doi',[])
    observed_dois=document.get('dois') or []
    if dois and not set(d.lower() for d in dois)&set(d.lower() for d in observed_dois):
        input_isbns={re.sub(r'[^0-9Xx]','',x).lower() for x in paper.get('identifiers',{}).get('isbn',[])}
        actual_isbns={re.sub(r'[^0-9Xx]','',x).lower() for x in (document.get('isbns') or [])}
        if observed_dois or not input_isbns&actual_isbns:return False
    if paper.get('year') and str(paper['year']) not in document.get('publication_years',[]):return False
    actual=' '.join(a.get('fullname','') for a in document.get('authors',[]))
    for author in paper.get('authors',[]):
        parts=[author.split(',')[0]] if ',' in author else author.split()
        if any(clean(part) not in clean(actual) for part in parts):return False
    kind=document.get('content_type','').lower();typ=paper.get('record_type')
    if typ=='book' and ('book' not in kind or 'chapter' in kind):return False
    if typ=='inbook' and 'chapter' not in kind:return False
    if typ=='article' and kind in {'book','book chapter','ebook','dissertation'}:return False
    return True

def choose_document(paper,documents):
    matches=[d for d in documents if document_matches(paper,d)]
    return next((d for d in matches if any(a.get('abstract','').strip() for a in d.get('abstracts',[]))),next(iter(matches),None))

def search(page,term):
    box=page.locator('input[name=q]:visible');box.fill(term)
    with page.expect_response(lambda r:urlsplit(r.url).path=='/api/search',timeout=30000) as info:box.press('Enter')
    data=info.value.json()
    if data.get('query',{}).get('original_query')!=term:raise ValueError('Observed response belongs to a different UI query')
    page.wait_for_timeout(550)
    return data

def ensure_scope(page):
    if 'ho=f' in urlsplit(page.url).fragment:return
    search(page,'kudosg05zzzxqvvnoexistingpaper20260908')
    with page.expect_response(lambda r:urlsplit(r.url).path=='/api/search',timeout=30000) as info:page.locator('#searchInfoBeyondHoldings').click()
    data=info.value.json();page.wait_for_timeout(550)
    if 'ho=f' not in urlsplit(page.url).fragment:raise ValueError('Beyond-holdings UI scope not active')
    return data

def next_search_page(page,term):
    page.wait_for_timeout(550)
    with page.expect_response(lambda r:urlsplit(r.url).path=='/api/search',timeout=30000) as info:
        page.locator('a[aria-label="다음"]:visible').first.click()
    data=info.value.json()
    if data.get('query',{}).get('original_query')!=term or 'ho=f' not in urlsplit(page.url).fragment:
        raise ValueError('Pagination changed query or required scope')
    page.wait_for_timeout(550)
    return data

def search_pages(page,term):
    data=search(page,term);seen=0;signatures=set()
    while True:
        docs=data.get('documents',[])
        signature=json.dumps(docs,sort_keys=True,ensure_ascii=False)
        if signature in signatures:raise ValueError('Pagination repeated the previous result page')
        signatures.add(signature);seen+=len(docs)
        yield data
        if seen>=int(data.get('record_count') or 0):return
        if not docs:raise ValueError('Empty page before declared result count was consumed')
        data=next_search_page(page,term)

def basic_record(paper):
    return {'schema_version':'kudos-recovery-result/1','paper_id':paper['paper_id'],'version_sha256':paper['version_sha256'],'metadata':{k:paper.get(k) for k in ['title','authors','year','identifiers']},'metadata_origin':'Base fields copied from assignment; observed_metadata contains independently observed UI response fields','identity':{'status':'unresolved','reason':'Target identity investigation pending'},'abstract':{'status':'unresolved','reason':'Target abstract investigation pending'},'fulltext':{'status':'unresolved','reason':'Target fulltext investigation pending'},'attempts':[],'evidence':[]}

def restriction_reason(marker):
    if marker.startswith('CPE'):return 'Actual source returned provider content-provision error '+marker+'; cause unconfirmed, not evidence of missing subscription rights.'
    return 'Actual source displayed an explicit access/security notice: '+marker

def publisher(c,r,paper,url,label):
    from link_scope import select_downloads,classify,observe_links
    page=c.new_page();pid=paper['paper_id']
    try:
        page.goto(url,wait_until='domcontentloaded',timeout=30000);page.wait_for_timeout(1500)
        loc=page.locator('main, article, #main-content').first
        body=loc.inner_text() if loc.count() else page.locator('body').inner_text()
        r['evidence'].append(artifact(pid,f'{label}-publisher.txt',body,page.url,kind='publisher-page'))
        r['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(page.url),'outcome':'Actual publisher/normal source page: '+page.title()})
        wall=re.search(r'CPE\d+|Unusual Traffic|Access Denied|보안 확인|Just a moment|Verify you are human|Cloudflare|403 Forbidden',body,re.I)
        if wall:
            if r['fulltext']['status']!='found' and r['identity']['status']=='confirmed':r['fulltext']={'status':'unavailable','reason':restriction_reason(wall.group())}
            return
        if r['fulltext']['status']=='found':return
        links=observe_links(page)
        heading=page.locator('h1');title_matches=heading.count()>0 and norm(paper['title']) in norm(heading.first.inner_text())
        observed=page.locator('meta[name="citation_doi"]').evaluate_all('(es)=>es.map(e=>e.content)');observed=[x for x in observed if isinstance(x,str)]
        scoped_paper=dict(paper)
        if not paper.get('identifiers',{}).get('doi') and r.get('discovered_identifiers',{}).get('doi') and r['identity']['status']=='confirmed':scoped_paper['identifiers']=dict(paper.get('identifiers',{}),doi=r['discovered_identifiers']['doi'])
        options={'title_matches':title_matches,'observed_dois':observed,'reviewed_parents':r.get('reviewed_parent_downloads',[])}
        decisions=[dict(x,url=safe_url(x['url']),scope_role=classify(scoped_paper,page.url,x,**options)[0],scope_reason=classify(scoped_paper,page.url,x,**options)[1]) for x in links]
        inventory=artifact(pid,f'{label}-download-scope.json',json.dumps({'source_url':safe_url(page.url),'links':decisions},ensure_ascii=False,indent=2),page.url,'application/json','target-download-scope');r['evidence'].append(inventory)
        if any(x['scope_role']=='needs_review' for x in decisions):
            task={'key':'download-scope:'+inventory['path'],'kind':'review','target':inventory['path'],'status':'needs_review','reason':'Unbound PDF controls require target/containing-volume context review; no arbitrary candidate cap is applied.','evidence_paths':[inventory['path']]}
            if r.get('work_state') and not any(t['key']==task['key'] for t in r['work_state']['tasks']):r['work_state']['tasks'].append(task)
        selected=select_downloads(scoped_paper,page.url,links,**options)
        seen=set()
        for link in selected:
            if link['url'] in seen or not link['url'].startswith('http'):continue
            seen.add(link['url'])
            try:response=get_download(c,link['url'],r['attempts'],paper['title']);data=response.body()
            except Exception as e:
                r['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(link['url']),'outcome':'Retryable individual download error: '+type(e).__name__})
                r.setdefault('download_errors',[]).append({'url':safe_url(link['url']),'error':type(e).__name__})
                continue
            r['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(link['url']),'outcome':f'UI-observed PDF/download link: HTTP {response.status}, valid_pdf={pdf_valid(data)}'})
            if not pdf_valid(data):continue
            with pymupdf.open(stream=data,filetype='pdf') as doc:
                first=doc[0].get_text();pages=len(doc)
                ar=artifact(pid,f'{label}-fulltext.pdf',data,link['url'],'application/pdf');ar['source_role']=link.get('scope_role','candidate')
                if link.get('scope_role')=='primary' and r['identity']['status']=='confirmed' and pdf_identity(paper,first,pages):
                    r['fulltext']={'status':'found','artifacts':[ar],'pages':pages,'validation':'Observed source link; first-page title/authors/year and available input page range match'}
                else:
                    r['evidence'].append(dict(ar,kind='pending-bibliographic-verification'))
                    r['fulltext']={'status':'unresolved','reason':'Acquired '+link.get('scope_role','candidate')+' PDF requires bibliographic/completeness or target-boundary verification; source preserved in evidence'}
                r['evidence'].append(artifact(pid,f'{label}-pdf-first.txt',first,link['url'],kind='pdf-extract'))
            if r['fulltext']['status']=='found':break
    except Exception as e:
        r['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(url),'outcome':'Retryable source UI/download error: '+type(e).__name__})
        if r['fulltext']['status']!='found':r['fulltext']=publisher_failure(e)
    finally:page.close()

def query_terms(paper,override=None):
    if override is not None:return override
    terms=paper.get('identifiers',{}).get('doi',[])[:1] or paper.get('identifiers',{}).get('isbn',[])[:1]
    author=' '.join(a.split(',')[0] for a in paper.get('authors',[]))
    return terms+['"'+paper['title']+'"'+(' '+author if author else '')]

def one(c,s,paper,terms_override=None,search_only=False):
    pid=paper['paper_id'];path=WORK/'results'/f'{pid}.json';r=json.loads(path.read_text()) if path.exists() else basic_record(paper)
    terms=query_terms(paper,terms_override)
    matched=None;links=[]
    for qi,term in enumerate(terms):
        pages=[];observed_anchors=[]
        for response in search_pages(s,term):
            pages.append(response)
            observed_anchors.extend(s.locator('a[href]').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))'))
        data=dict(pages[0],documents=[d for page_data in pages for d in page_data.get('documents',[])])
        if 'ho=f' not in urlsplit(s.url).fragment:raise ValueError('Search scope unexpectedly narrowed')
        docs=data.get('documents',[])
        fields=['title','full_title','dois','isbns','authors','publication_years','content_type','abstracts','pages','start_pages','end_pages','page_count','publication_title','volumes','issues','publisher']
        selected={'query':data['query'],'scope':'ho=f','record_count':data.get('record_count'),'pages_observed':len(pages),'documents':[{k:d.get(k) for k in fields if k in d} for d in docs]}
        r['evidence'].append(artifact(pid,f'summon-response-{qi}.json',json.dumps(selected,ensure_ascii=False,indent=2),s.url,'application/json','actual-ui-search-response'))
        r['evidence'].append(artifact(pid,f'summon-wide-{qi}.txt',s.locator('body').inner_text(),s.url,kind='search-results'))
        r['attempts'].append({'method':'playwright','query':term,'url':s.url,'outcome':f'Actual UI search ho=f; query.original_query matched; {len(docs)} returned documents, total={data.get("record_count")}'})
        matched=choose_document(paper,docs)
        if matched:
            r['identity']={'status':'confirmed','reason':'Actual Summon UI response title, returned target DOI or assigned ISBN when DOI is absent, year, author/editor name tokens and compatible document type match; complete observed metadata preserved'}
            r['observed_metadata']={k:matched.get(k) for k in fields if k in matched}
            r['observed_metadata_candidates']=[{k:d.get(k) for k in fields if k in d} for d in docs if document_matches(paper,d)]
            texts=[a.get('abstract','').strip() for a in matched.get('abstracts',[])]
            texts=[t for t in texts if t and t.casefold().strip(' .') not in {'no abstract available','no abstract','abstract','n/a'} and not t.startswith('[...]') and not t.endswith('...')]
            if texts:
                candidate=artifact(pid,'summon-abstract.txt','\n\n'.join(texts),s.url)
                r['evidence'].append(dict(candidate,kind='provider-abstract-candidate'))
                r['abstract']=provider_candidate(r['abstract'],candidate)
            anchors=observed_anchors
            link=next((a['url'] for a in anchors if a['url']==matched.get('link')),None)
            if not link:link=next((a['url'] for a in anchors if clean(a['text'])==clean(matched.get('full_title',''))),None)
            if link:links.append(link)
            break
    if search_only:
        r.setdefault('additional_search_scope',[]).append({'queries':terms[:qi+1],'scope':'ho=f','all_pages_received':True,'documents_received':len(docs),'total_documents':data.get('record_count')})
        return r
    # Valid acquired originals are preserved; source investigation continues for unresolved/fulltext-limited records.
    sources_attempted=[];preserved_original=r['fulltext']['status']=='found'
    if not preserved_original:
        sources=list(dict.fromkeys(links+paper.get('source_urls',[])))
        for j,url in enumerate(sources):
            publisher(c,r,paper,url,'wide-'+str(j))
            sources_attempted.append(safe_url(url))
            if r['fulltext']['status']=='found':break
    r['scope_review']={'summon_beyond_holdings':True,'queries':terms[:qi+1],'matched':matched is not None,'normal_source_link_count_observed':len(links),'source_urls_attempted_this_pass':sources_attempted,'preserved_acquired_original':preserved_original,'remaining':'Unresolved states require link, identity or content review; no blanket absence conclusion'}
    return r

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);ap.add_argument('--start',type=int,default=0);args=ap.parse_args()
    a=json.loads((WORK/'assignment.json').read_text());papers=[json.loads(x) for x in (BASE/a['members_path']).read_text().splitlines()]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state=a['browser_state']);s=c.new_page();s.goto(SUMMON);ensure_scope(s);n=0
        for i,paper in enumerate(papers):
            if i<args.start:continue
            path=WORK/'results'/f"{paper['paper_id']}.json"
            if path.exists() and json.loads(path.read_text()).get('scope_review',{}).get('summon_beyond_holdings'):continue
            save_progress('Summon ho=f collection',i,paper,len(papers),'python research/pvsnp/literature-baseline/kudos-recovery/g05/summon_collect.py')
            try:r=one(c,s,paper);save_json(path,r);n+=1;print(json.dumps({'index':i,'paper_id':paper['paper_id'],'identity':r['identity']['status'],'abstract':r['abstract']['status'],'fulltext':r['fulltext']['status']}),flush=True)
            except Exception as e:
                print(json.dumps({'index':i,'retryable_error':type(e).__name__}),flush=True);s.goto(SUMMON);ensure_scope(s)
            if args.limit and n>=args.limit:break
        b.close()

if __name__=='__main__':main()
