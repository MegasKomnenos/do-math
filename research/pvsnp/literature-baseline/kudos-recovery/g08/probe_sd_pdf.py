import json,hashlib,os,re,time
from pathlib import Path
import recover as r
import resume,native_source

pid='VER-22d09f2a0e9222a1ac184678'
run_id=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+str(os.getpid())
manifest={'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pid':os.getpid(),'argv':['probe_sd_pdf.py'],'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),r.ROOT/'recover.py',r.ROOT/'native_source.py',r.ROOT/'resume.py']}}
r.save_json(r.ROOT/'runs'/f'{run_id}.json',manifest)
record=json.loads((r.ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
paper=next(json.loads(line) for line in (r.BASE/r.ASSIGNMENT['members_path']).read_text(encoding='utf-8').splitlines() if json.loads(line)['paper_id']==pid)
observed=[];downloads=[]
with r.sync_playwright() as pw:
    browser=pw.firefox.launch(headless=True);context=browser.new_context(storage_state=r.ASSIGNMENT['browser_state'],accept_downloads=True)
    gateway=native_source.institution_gateway(context)
    page=context.new_page();body,timed_out=native_source.visit_body(page,'https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/0022039684901050')
    source=r.artifact(pid,'native-view-pdf-dom.html',page.content(),page.url,'publisher-dom','text/html');record['evidence'].append(source)
    pdf_state=native_source.wait_pdf_links(page,page.url)
    controls=page.locator('button,a,[role="button"]').evaluate_all('(es)=>es.filter(e=>/view\\s+pdf/i.test(e.innerText)&&(e.offsetWidth||e.offsetHeight)).map(e=>({tag:e.tagName,text:e.innerText,html:e.outerHTML}))')
    def response_seen(response):
        if 'application/pdf' in response.headers.get('content-type','').lower():observed.append(response)
    context.on('response',response_seen)
    context.on('page',lambda p:p.on('download',lambda d:downloads.append(d)))
    page.on('download',lambda d:downloads.append(d))
    clicked=False
    if pdf_state['links']:
        for target in page.locator('a[href]').all():
            if target.is_visible() and target.evaluate('(e)=>e.href')==pdf_state['links'][0]['url']:
                target.click(timeout=10000);clicked=True;break
    page.wait_for_timeout(10000)
    report={'controls':controls,'pdf_state':pdf_state,'clicked_initialized_control':clicked,'pages':[r.public_url(p.url) for p in context.pages],'pdf_responses':[r.public_url(p.url) for p in observed],'downloads':len(downloads),'gateway_visible_search':gateway['visible_search_input']}
    for response in observed:
        try:resume.accept_linked_pdf(paper,record,response.body(),response.url)
        except Exception as exc:report.setdefault('pdf_body_errors',[]).append(type(exc).__name__)
    for i,download in enumerate(downloads):
        path=download.path()
        if path:resume.accept_linked_pdf(paper,record,Path(path).read_bytes(),download.url)
    for i,p in enumerate(context.pages):
        try:record['evidence'].append(r.artifact(pid,'view-pdf-page-'+str(i)+'.txt',p.locator('body').inner_text(timeout=3000),p.url,'pdf-ui-observation'))
        except Exception:pass
    proof=r.artifact(pid,'view-pdf-observation.json',json.dumps(report,ensure_ascii=False,indent=2),page.url,'pdf-ui-observation','application/json');record['evidence'].append(proof)
    r.save_json(r.ROOT/'results'/f'{pid}.json',record);print(json.dumps(report,ensure_ascii=False),flush=True)
    browser.close()
manifest['finished_utc']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());r.save_json(r.ROOT/'runs'/f'{run_id}.json',manifest)
