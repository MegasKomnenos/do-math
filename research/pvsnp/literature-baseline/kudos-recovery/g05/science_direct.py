"""Native Firefox public ScienceDirect pages; preserve publisher MathML verbatim."""
import hashlib,html,json,re,sys
from pathlib import Path
from urllib.parse import urlsplit
import pymupdf
from collect import BASE,WORK,artifact,norm,pdf_valid,get_download,nonpdf_body,safe_url
from acm_collect import pdf_identity
sys.path.insert(0,str(WORK.parent))
from work_queue import component_basis

def abstract_html(fragment,title):
    return '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'; form-action \'none\'"><title>'+html.escape(title)+' — source abstract</title><style>body{max-width:900px;margin:2rem auto;padding:1rem;line-height:1.45}math{font-size:1em}</style></head><body>'+fragment+'</body></html>'

def publisher_identity(paper,meta,body):
    dois=paper.get('identifiers',{}).get('doi',[])
    if not dois or not {d.lower() for d in dois}&{d.lower() for d in meta.get('citation_doi',[])}:return False
    if norm(paper['title']) not in {norm(t) for t in meta.get('citation_title',[])}:return False
    years={d[:4] for k in ('citation_publication_date','citation_online_date') for d in meta.get(k,[])}
    if paper.get('year') and str(paper['year']) not in years:return False
    header=body.split('\nAbstract\n',1)[0]
    return all(norm(a.split(',')[0]) in norm(header) for a in paper.get('authors',[]))

def source_url(record,paper,institutional=False):
    if institutional:
        urls=[e.get('url','') for e in record.get('evidence',[]) if urlsplit(e.get('url','')).hostname=='www-sciencedirect-com.libproxy.knu.ac.kr' and re.search(r'/science/article/(?:abs/)?pii/[^/]+/?$',urlsplit(e.get('url','')).path)]
        return urls[-1] if urls else None
    urls=[e.get('url','') for e in record.get('evidence',[]) if urlsplit(e.get('url','')).hostname in {'www.sciencedirect.com','sciencedirect.com'} and re.search(r'/science/article/(?:abs/)?pii/[^/]+/?$',urlsplit(e.get('url','')).path)]
    if urls:return next((u for u in reversed(urls) if '/article/abs/' in u),urls[-1])
    return next(iter(paper.get('source_urls',[])),None)

def requires_browser_download(body):
    return 'preparing your download' in body.lower()

def browser_pdf_download(context,page,link,pid,record):
    responses=[];downloads=[];opened=[];assets=[]
    def response_seen(response):
        if response.status==200 and 'application/pdf' in response.headers.get('content-type',''):responses.append(response)
    def download_seen(download):downloads.append(download)
    def page_seen(new_page):
        opened.append(new_page);new_page.on('download',download_seen)
    context.on('response',response_seen);context.on('page',page_seen);page.on('download',download_seen)
    try:
        target=next((a for a in page.locator('a[href]:visible').all() if a.evaluate('(e)=>e.href')==link['url']),None)
        if target is None:return assets
        target.click(timeout=10000)
        page.wait_for_timeout(6500)
        for response in responses:
            try:
                data=response.body()
                if pdf_valid(data):assets.append(artifact(pid,'native-browser-fulltext.pdf',data,response.url,'application/pdf'))
            except Exception:pass
        for download in downloads:
            data=Path(download.path()).read_bytes()
            if pdf_valid(data):assets.append(artifact(pid,'native-browser-fulltext.pdf',data,download.url,'application/pdf'))
        for opened_page in opened:
            try:record['evidence'].append(artifact(pid,'native-pdf-popup.txt',opened_page.locator('body').inner_text(timeout=3000),opened_page.url,kind='actual-pdf-popup-body'))
            except Exception:pass
        record['attempts'].append({'method':'playwright','query':pid,'url':safe_url(link['url']),'outcome':f'Clicked actual initialized View PDF anchor; new tabs={len(opened)}, complete PDF responses={len(responses)}, downloads={len(downloads)}, readable PDFs={len(assets)}'})
    except Exception as error:
        record['attempts'].append({'method':'playwright','query':pid,'url':safe_url(link['url']),'outcome':'Actual initialized PDF click/continuation error: '+type(error).__name__})
    finally:
        context.remove_listener('response',response_seen);context.remove_listener('page',page_seen);page.remove_listener('download',download_seen)
        for opened_page in opened:
            if not opened_page.is_closed():opened_page.close()
    return assets

def is_pdf_control(item):
    return bool(re.match(r'^\s*(?:view|download)\s+pdf\b',item.get('text',''),re.I))

def matching_pdf_links(links,page_url):
    match=re.search(r'/pii/([^/?]+)',page_url)
    if not match:return []
    target='/pii/'+match.group(1)
    return [link for link in links if is_pdf_control(link) and re.search(re.escape(target)+r'(?:/|$|\?)',link.get('url',''))]

def body_ready(body):
    return bool(body.strip()) and body.strip().lower() not in {'loading','loading...','불러오는 중...'}

def access_notice(body):
    return bool(re.search(r'CPE00001|Access Denied|Verify you are human|Are you a robot|captcha challenge|보안 확인',body,re.I))

def visit_body(page,url):
    from playwright.sync_api import TimeoutError
    timed_out=False
    try:page.goto(url,wait_until='domcontentloaded',timeout=15000)
    except TimeoutError:timed_out=True
    page.wait_for_timeout(1600)
    return page.locator('body').inner_text(timeout=5000),timed_out

def institution_gateway(context):
    page=context.new_page();provider=None
    try:
        page.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542',wait_until='domcontentloaded',timeout=30000)
        page.locator('#search_order').fill('ScienceDirect');page.locator('#search_order').press('Enter')
        with context.expect_page(timeout=30000) as opened:page.get_by_text('바로가기',exact=True).click()
        provider=opened.value;provider.locator('#qs').wait_for(state='visible',timeout=40000)
        return {'url':safe_url(provider.url),'visible_search_input':True,'route':'Actual KUDOS academic DB search ScienceDirect and displayed 바로가기; native Firefox main-frame #qs visible','browser':'firefox'}
    finally:
        if provider:provider.close()
        page.close()

def collect(context,page,paper,institutional=False,source_target=None,html_only=False):
    pid=paper['paper_id'];record=json.loads((WORK/'results'/f'{pid}.json').read_text());url=source_target or source_url(record,paper,institutional=institutional)
    if not url:return record
    if html_only:
        from resource_snapshot import watch_images
        watch_images(page)
    body,navigation_timed_out=visit_body(page,url)
    if navigation_timed_out:record['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(url),'outcome':'DOM load event timed out; captured actual current visible body before deciding content/access status'})
    if not body_ready(body):
        record['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(url),'outcome':'Actual publisher/normal source page: visit attempted; current DOM remains empty/loading'})
        diagnostic={'request_url':safe_url(url),'current_url':safe_url(page.url),'body_text':body,'body_characters':len(body),'navigation_timed_out':navigation_timed_out,'outcome':'Uninitialized body is a retryable UI state, not a bibliography conflict or content unavailability'}
        record['evidence'].append(artifact(pid,'native-uninitialized-body.json',json.dumps(diagnostic,ensure_ascii=False,indent=2),page.url,'application/json','actual-ui-initialization-diagnostic'))
        record['native_source_outcome']={'retryable_ui':True,'reason':diagnostic['outcome']};return record
    source=artifact(pid,'native-publisher.txt',body,page.url,kind='publisher-page');record['evidence'].append(source)
    record['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(page.url),'outcome':'Actual publisher/normal source page: native '+page.context.browser.browser_type.name})
    if access_notice(body):
        record['native_source_outcome']='Provider content error/access notice still present on this individual page; no absence conclusion'
        return record
    if html_only:
        import native_article
        outcome=native_article.capture(context,page,paper,record)
        record['native_source_outcome']={'html_only':True,'html_result':outcome}
        if outcome['status']!='found' and record['fulltext']['status']!='found':record['fulltext']={'status':'unresolved','reason':outcome['reason']}
        return record
    meta={}
    for item in page.locator('meta[name^="citation_"]').evaluate_all('(es)=>es.filter(e=>/title|doi|date|volume|issue|journal|author/i.test(e.name)).map(e=>({name:e.name,content:e.content}))'):
        meta.setdefault(item['name'],[]).append(item['content'])
    metadata=artifact(pid,'native-publisher-metadata.json',json.dumps(meta,ensure_ascii=False,indent=2),page.url,'application/json','actual-publisher-metadata');record['evidence'].append(metadata)
    record['observed_publisher_metadata']=meta
    if not publisher_identity(paper,meta,body):
        record['native_source_outcome']='Observed title/DOI/date/byline requires reconciliation with assigned bibliography'
        return record
    identity_reason='Native publisher DOM citation_title/DOI and publication or online year match assigned bibliography; input author surnames occur in actual byline/header before abstract. Observed dates and metadata are retained independently.'
    record['identity']={'status':'confirmed','reason':identity_reason}
    proof=[source['path'],metadata['path']]
    def review(component,reason,paths):
        record['work_state']['reviews'][component]={'method':'deterministic','basis_sha256':component_basis(record,component),'reason':reason,'evidence_paths':paths,'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tests':'g05/test_science_direct.py; native publisher pilot'}
        for task in record['work_state']['tasks']:
            if task['key']=='review:'+component:task.update(status='done',reason=reason,evidence_paths=paths)
    review('identity',identity_reason,proof)
    heading=page.locator('#abstracts').get_by_role('heading',name='Abstract',exact=True)
    if heading.count()==1 and record['abstract']['status']!='found':
        node=heading.locator('xpath=..');fragment=node.inner_html();text=node.inner_text()
        original=artifact(pid,'publisher-abstract-original.html',fragment,page.url,'text/html','actual-publisher-abstract-dom');record['evidence'].append(original)
        if len(text)>40 and not re.search(r'No abstract available|Abstract\s+Not available',text,re.I) and not re.search(r'<(?:img|iframe|video|audio|object|embed)\b',fragment,re.I):
            ar=artifact(pid,'publisher-abstract.html',abstract_html(fragment,paper['title']),page.url,'text/html')
            for prior in record['abstract'].get('artifacts',[]):
                if prior['path'] not in {e['path'] for e in record['evidence']}:record['evidence'].append(dict(prior,kind='prior-abstract-source'))
            record.setdefault('abstract_source_history',[]).append(record['abstract'])
            reason='Actual publisher Abstract heading container isolated from Highlights/recommendations; complete source HTML and native MathML retained in self-contained UTF-8 HTML. No exponent/index flattening or invented transcription; no external media is required to render this container.'
            record['abstract']={'status':'found','artifacts':[ar],'source_kind':'publisher_abstract_html','extraction_quality':'original_mathml_preserved','validation':reason}
            review('abstract',reason,proof+[original['path'],ar['path']])
    controls=page.locator('a:visible,button:visible').evaluate_all(r'(es)=>es.filter(e=>/view\s+pdf|download\s+pdf/i.test(e.innerText)).map(e=>({text:e.innerText,href:e.href||null}))')
    pending_control=False
    if any(is_pdf_control(item) for item in controls):
        from playwright.sync_api import TimeoutError
        target=re.search(r'/pii/([^/?]+)',page.url)
        if target:
            try:page.wait_for_function(r'''(pii)=>Array.from(document.querySelectorAll('a[href]')).some(e=>e.offsetParent!==null&&/view\s+pdf|download\s+pdf/i.test(e.innerText)&&e.href.includes('/pii/'+pii+'/'))''',arg=target.group(1),timeout=20000)
            except TimeoutError:pending_control=True
    links=page.locator('a[href]:visible').evaluate_all(r'(es)=>es.filter(e=>/view\s+pdf|download\s+pdf/i.test(e.innerText)).map(e=>({text:e.innerText,url:e.href}))')
    links=matching_pdf_links(links,page.url)
    if pending_control:record['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(page.url),'outcome':'Visible PDF control has no initialized target href after bounded wait; unresolved UI initialization, not unavailable content'})
    link_record=artifact(pid,'native-pdf-links.json',json.dumps([dict(x,url=safe_url(x['url'])) for x in links],ensure_ascii=False,indent=2),page.url,'application/json','observed-source-links');record['evidence'].append(link_record)
    if record['fulltext']['status']!='found':
        for link in {x['url']:x for x in links}.values():
            try:
                response=get_download(context,link['url'],record['attempts'],paper['title']);data=response.body()
                if not pdf_valid(data):
                    nonpdf=nonpdf_body(data);record['evidence'].append(artifact(pid,'native-pdf-response.txt',nonpdf,link['url'],kind='nonpdf-download-response'))
                    if requires_browser_download(nonpdf):record['fulltext']={'status':'unresolved','reason':'Observed PDF link returns Preparing your download HTML; browser continuation must be inspected.'}
                    candidates=browser_pdf_download(context,page,link,pid,record)
                else:candidates=[artifact(pid,'native-fulltext.pdf',data,link['url'],'application/pdf')]
                for ar in candidates:
                    with pymupdf.open(BASE/ar['path']) as doc:first=doc[0].get_text();pages=len(doc)
                    if pdf_identity(paper,first,pages):
                        record['fulltext']={'status':'found','artifacts':[ar],'pages':pages,'validation':'Visible native publisher PDF link or its actual browser click; complete PDF opens and first-page title/authors/year plus assigned numeric page span match.'};review('fulltext',record['fulltext']['validation'],proof+[ar['path']]);break
                    record['evidence'].append(dict(ar,kind='pending-bibliographic-verification'))
                if record['fulltext']['status']=='found':break
            except Exception as error:record['attempts'].append({'method':'playwright','query':paper['title'],'url':safe_url(link['url']),'outcome':'Individual native PDF request error: '+type(error).__name__})
    record['native_source_outcome']={'pdf_control_pending':pending_control,'observed_pdf_links':len(links),'purchase_pdf_visible':'Purchase PDF' in body,'organization_access_visible':'Access through' in body,'abstract_heading_count':heading.count()}
    return record
