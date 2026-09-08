import argparse, hashlib, html, json, re, time, unicodedata
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import pymupdf
from playwright.sync_api import sync_playwright

BASE=Path('C:/math/research/pvsnp/literature-baseline')
WORK=BASE/'kudos-recovery/g05'
RAW=BASE/'intake/kudos-recovery/g05'
SUMMON='https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q='

def norm(value):
    value=re.sub(r'\\+[Hv]\s+([A-Za-z])',r'\1',value)
    value=re.sub(r'\\+texttimes\b','×',value).replace('Ł','L').replace('ł','l')
    value=''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c))
    return re.sub(r'[^\w]','',value.casefold())

def identity_matches(paper, text):
    dois=paper.get('identifiers',{}).get('doi',[])
    if dois:
        return any(d.casefold() in text.casefold() for d in dois) and norm(paper['title']) in norm(text)
    return norm(paper['title']) in norm(text) and str(paper.get('year','MISSING')) in text and all(norm(a.split(',')[0]) in norm(text) for a in paper.get('authors',[]))

def pdf_valid(data):
    if not data.startswith(b'%PDF-'): return False
    try:
        with pymupdf.open(stream=data,filetype='pdf') as doc: return len(doc)>0
    except Exception: return False

def completed(record):
    return record.get('identity',{}).get('status') in {'confirmed','not_found'} and all(record.get(c,{}).get('status') in {'found','not_found','unavailable'} for c in ['abstract','fulltext'])

def publisher_failure(error):
    return {'status':'unresolved','reason':'Retryable publisher navigation/download failure: '+type(error).__name__}

def nonpdf_body(data):
    raw=data.decode('utf-8',errors='replace')
    main=re.search(r'<main\b[^>]*>(.*?)</main>',raw,re.S|re.I)
    if main:raw=main.group(1)
    raw=re.sub(r'<(script|style|nav|header|form)\b[^>]*>.*?</\1>','',raw,flags=re.S|re.I)
    text=html.unescape(re.sub('<[^>]+>','\n',raw))
    return '\n'.join(line.strip() for line in text.splitlines() if line.strip())

def get_download(context,url,attempts=None,query='',wait=time.sleep):
    from playwright.sync_api import TimeoutError as BrowserTimeout
    for attempt in range(3):
        try:
            response=context.request.get(url,timeout=30000)
            if attempts is not None:attempts.append({'method':'playwright','query':query,'url':safe_url(url),'outcome':f'Observed download request attempt {attempt+1}: HTTP {response.status}'})
            if response.status!=429 and not 500<=response.status<600:return response
            if attempt==2:return response
            retry=response.headers.get('retry-after','')
            delay=int(retry) if retry.isdigit() else 2*(attempt+1)
            if delay>60:raise RuntimeError('Server Retry-After exceeds this run wait; preserve and reschedule')
            wait(delay)
        except (TimeoutError,BrowserTimeout):
            if attempts is not None:attempts.append({'method':'playwright','query':query,'url':safe_url(url),'outcome':f'Observed download timeout attempt {attempt+1}'})
            if attempt==2:raise
            wait(2*(attempt+1))

def click_pdf_link(page,link):
    for element in page.locator('a[href]').all():
        if element.evaluate('(e)=>e.href')==link['url']:
            element.click(timeout=5000)
            return
    raise ValueError('Observed PDF link no longer present')

def safe_url(url):
    s=urlsplit(url)
    if 'summon.serialssolutions.com' in s.netloc and '/link/' in s.path: return SUMMON
    return urlunsplit((s.scheme,s.netloc,s.path,s.query if 'summon.serialssolutions.com' in s.netloc and '/search' in s.path else '', ''))

def save_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for attempt in range(6):
        try:tmp.replace(path);break
        except PermissionError:
            if attempt==5:raise
            time.sleep(.02*(2**attempt))

def save_progress(stage,index,paper,total,resume):
    records=[json.loads(p.read_text(encoding='utf-8')) for p in (WORK/'results').glob('*.json')]
    save_json(WORK/'progress.json',{'stage':stage,'current_index':index,'last_paper_id':paper['paper_id'],'total':total,'processed':len(records),'abstract_found':sum(r['abstract']['status']=='found' for r in records),'fulltext_found':sum(r['fulltext']['status']=='found' for r in records),'unresolved':sum(any(r[c]['status']=='unresolved' for c in ['identity','abstract','fulltext']) for r in records),'remaining':total-len(records),'resume_command':resume})

def artifact(pid,name,data,url,media='text/plain',kind=None):
    path=RAW/pid/name;path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(data,str): data=data.encode('utf-8')
    if path.exists() and path.read_bytes()!=data:
        path=path.with_name(path.stem+'-'+hashlib.sha256(data).hexdigest()[:16]+path.suffix)
    path.write_bytes(data)
    result={'path':path.relative_to(BASE).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'url':safe_url(url),'media_type':media}
    if kind: result['kind']=kind
    return result

def query(s,term):
    s.locator('input[name=q]:visible').fill(term)
    s.locator('input[name=q]:visible').press('Enter')
    s.wait_for_timeout(2200)
    s.locator('button[data-aid=quick-look-button]:visible').first.or_(s.get_by_text(re.compile('관련된 검색결과가 없습니다')).filter(visible=True)).first.wait_for(timeout=20000)
    s.wait_for_timeout(500)

def collect_one(c,s,paper):
    pid=paper['paper_id'];result={'schema_version':'kudos-recovery-result/1','paper_id':pid,'version_sha256':paper['version_sha256'],'metadata':{k:paper.get(k) for k in ['title','authors','year','identifiers']},'identity':{'status':'unresolved','reason':'Target detail not yet confirmed'},'abstract':{'status':'unresolved','reason':'Target detail not yet confirmed'},'fulltext':{'status':'unresolved','reason':'Target detail not yet confirmed'},'attempts':[],'evidence':[]}
    target_link=None;detail='';abstract=''
    terms=paper.get('identifiers',{}).get('doi',[])[:1]+[paper['title']]
    for qi,term in enumerate(terms):
        try:
            query(s,term)
            body=s.locator('body').inner_text()
            result['evidence'].append(artifact(pid,f'search-{qi}.txt',body,s.url,kind='search-results'))
            count=s.locator('button[data-aid=quick-look-button]:visible').count()
            result['attempts'].append({'method':'playwright','query':term,'url':safe_url(s.url),'outcome':f'{count} visible Quick Look controls; actual search results preserved'})
            for i in range(min(count,5)):
                s.locator('button[data-aid=quick-look-button]:visible').nth(i).click(timeout=5000)
                modal=s.locator('.modal.quick-look[role=dialog]');modal.wait_for();detail=modal.inner_text()
                result['evidence'].append(artifact(pid,f'detail-{qi}-{i}.txt',detail,s.url,kind='detail-page'))
                match=identity_matches(paper,detail)
                if match:
                    result['identity']={'status':'confirmed','reason':'Summon Quick Look title and target DOI match; publication details preserved in detail evidence' if paper.get('identifiers',{}).get('doi') else 'Summon title, authors and year match; publication details preserved in detail evidence'}
                    aloc=modal.locator('[data-aid=abstract]')
                    abstract=aloc.first.inner_text().strip() if aloc.count() else ''
                    links=modal.locator('a[href]').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))')
                    target_link=next((l['url'] for l in links if norm(paper['title']) in norm(l['text'])),None)
                    modal.press('Escape');break
                modal.press('Escape')
            if result['identity']['status']=='confirmed': break
        except Exception as e:
            result['attempts'].append({'method':'playwright','query':term,'url':safe_url(s.url),'outcome':'UI error: '+type(e).__name__})
            try: s.keyboard.press('Escape')
            except Exception: pass
    if result['identity']['status']=='confirmed':
        if abstract and len(abstract)>30 and abstract.casefold() not in {'no abstract available','no abstract'}:
            result['abstract']={'status':'found','artifacts':[artifact(pid,'abstract.txt',abstract,s.url)],'source_kind':'Summon full abstract in Quick Look, not result snippet'}
        else: result['abstract']={'status':'not_found','reason':'Confirmed Summon detail provides no non-placeholder abstract; publisher page also investigated below'}
    source=target_link or next(iter(paper.get('source_urls',[])),None)
    if source:
        page=c.new_page();pdfs=[]
        def response(resp):
            if 'application/pdf' in resp.headers.get('content-type',''):
                try:
                    data=resp.body()
                    if pdf_valid(data): pdfs.append((data,resp.url))
                except Exception: pass
        page.on('response',response)
        try:
            page.goto(source,wait_until='domcontentloaded',timeout=25000);page.wait_for_timeout(1800)
            body=page.locator('body').inner_text(timeout=5000)
            # Publisher pages are public bibliographic views; do not record account UI or hidden inputs.
            main=page.locator('main').first
            content=main.inner_text() if main.count() else body
            result['evidence'].append(artifact(pid,'publisher.txt',content,page.url,kind='publisher-page'))
            result['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(page.url),'outcome':page.title()+'; visible publisher page preserved'})
            blocked=bool(re.search('보안 확인|Cloudflare|Access Denied|Unusual Traffic|Just a moment|Robot|Checking your browser|403 Forbidden|Verify you are human',body,re.I))
            if not blocked and result['identity']['status']=='confirmed':
                links=page.locator('a[href]').evaluate_all('(es)=>es.filter(e=>/pdf|download/i.test(e.innerText+e.getAttribute("href"))).map(e=>({text:e.innerText,url:e.href}))')
                for j,l in enumerate(links[:2]):
                    try:
                        # Follow only links actually present in the observed publisher UI.
                        with page.expect_download(timeout=10000) as di:
                            click_pdf_link(page,l)
                        down=di.value;data=Path(down.path()).read_bytes()
                        if pdf_valid(data): pdfs.append((data,down.url))
                    except Exception: pass
                    if pdfs: break
            if not pdfs and result['identity']['status']=='confirmed':
                result['fulltext']={'status':'unavailable','reason':'Publisher access blocked by displayed security/access challenge' if blocked else 'Observed publisher page and visible PDF download controls did not yield a readable full-text PDF; actual page preserved'}
        except Exception as e:
            result['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(source),'outcome':'Publisher navigation/download: '+type(e).__name__})
            if result['identity']['status']=='confirmed': result['fulltext']=publisher_failure(e)
        finally:
            if pdfs:
                for data,url in pdfs:
                    with pymupdf.open(stream=data,filetype='pdf') as doc:
                        first='\n'.join(p.get_text() for p in list(doc)[:3]);pages=len(doc)
                    if norm(paper['title']) in norm(first):
                        result['fulltext']={'status':'found','artifacts':[artifact(pid,'fulltext.pdf',data,url,'application/pdf')],'pages':pages,'validation':'PDF opens; target title present in first three pages; candidate version identified by linked target DOI'}
                        break
            page.close()
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);ap.add_argument('--start',type=int,default=0);args=ap.parse_args()
    a=json.loads((WORK/'assignment.json').read_text(encoding='utf-8-sig'));papers=[json.loads(x) for x in (BASE/a['members_path']).read_text(encoding='utf-8-sig').splitlines()]
    with sync_playwright() as p:
        b=p.chromium.launch(channel='chrome',headless=True);c=b.new_context(storage_state=a['browser_state'],accept_downloads=True);s=c.new_page();s.goto(SUMMON);s.locator('input[name=q]:visible').wait_for(timeout=30000)
        n=0
        for index,paper in enumerate(papers):
            if index<args.start:continue
            out=WORK/'results'/f"{paper['paper_id']}.json"
            if out.exists() and completed(json.loads(out.read_text(encoding='utf-8'))):continue
            save_progress('collecting',index,paper,len(papers),'python research/pvsnp/literature-baseline/kudos-recovery/g05/collect.py')
            result=collect_one(c,s,paper);save_json(out,result);n+=1
            print(json.dumps({'index':index,'paper_id':paper['paper_id'],'identity':result['identity']['status'],'abstract':result['abstract']['status'],'fulltext':result['fulltext']['status']},ensure_ascii=False),flush=True)
            if args.limit and n>=args.limit:break
        b.close()

if __name__=='__main__':main()
