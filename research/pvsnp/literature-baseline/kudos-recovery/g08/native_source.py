"""Reuse the observed Firefox provider route and retain native mathematical DOM."""
import hashlib
import html
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import TimeoutError
import recover as r
sys.path.insert(0,str(r.ROOT.parent))
import work_queue

def abstract_html(fragment,title):
    return '<!doctype html><html><head><meta charset="utf-8"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src data:; base-uri \'none\'; form-action \'none\'"><title>'+html.escape(title)+'</title><style>body{max-width:900px;margin:2rem auto;line-height:1.5}math{font-size:1em}</style></head><body>'+fragment+'</body></html>'

def visit_body(page,url):
    from playwright.sync_api import TimeoutError
    timed_out=False
    try:page.goto(url,wait_until='domcontentloaded',timeout=20000)
    except TimeoutError:timed_out=True
    page.wait_for_timeout(1800)
    return page.locator('body').inner_text(timeout=5000),timed_out

def observed_byline(metadata,body):
    authors='; '.join(x['value'] for x in metadata if x['name']=='citation_author')
    if authors:return authors
    match=re.search(r'Author links open overlay panel\s*\n(.*?)(?:\nShow more|\nAdd to Mendeley)',body,re.S)
    return match[1].strip() if match else ''

def provider_identity(paper,metadata,body,url):
    values=lambda name:'; '.join(x['value'] for x in metadata if x['name']==name)
    dates='; '.join(values(name) for name in ['citation_date','citation_publication_date','citation_online_date','citation_year'])
    if not r.publisher_identity(paper,values('citation_title'),observed_byline(metadata,body),dates,url):return False
    expected={d.lower() for d in paper.get('identifiers',{}).get('doi',[])}
    observed={x['value'].lower() for x in metadata if x['name']=='citation_doi'}
    return not expected or bool(expected.intersection(observed))

def wait_pdf_links(page,url,timeout=20000):
    target=re.search(r'/pii/([^/?]+)',url)
    read=lambda:page.locator('a:visible,button:visible').evaluate_all('(es)=>es.filter(e=>/^(view|download)\\s+pdf\\b/i.test(e.innerText.trim())).map(e=>({text:e.innerText,url:e.href||null,disabled:e.getAttribute("aria-disabled")}))')
    before=read()
    if before and target:
        try:page.wait_for_function('(pii)=>Array.from(document.querySelectorAll("a[href]")).some(e=>(e.offsetWidth||e.offsetHeight)&&/^(view|download)\\s+pdf\\b/i.test(e.innerText.trim())&&e.getAttribute("aria-disabled")!=="true"&&e.href.includes("/pii/"+pii+"/"))',arg=target[1],timeout=timeout)
        except TimeoutError:pass
    after=read()
    links=[{'text':x['text'],'url':x['url']} for x in after if target and x['url'] and x['disabled']!='true' and re.search(r'/pii/'+re.escape(target[1])+r'(?:/|$|\?)',x['url'])]
    links=list({x['url']:x for x in links}.values())
    return {'before':before,'after':after,'links':links,'pending':bool(before and not links)}

def institution_gateway(context):
    page=context.new_page()
    page.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542',wait_until='domcontentloaded',timeout=30000)
    page.locator('#search_order').fill('ScienceDirect');page.locator('#search_order').press('Enter')
    with context.expect_page(timeout=30000) as opened:page.get_by_text('바로가기',exact=True).click()
    provider=opened.value
    provider.locator('#qs').wait_for(state='visible',timeout=40000)
    result={'url':r.public_url(provider.url),'visible_search_input':True,'body':provider.locator('body').inner_text(),'browser':'firefox'}
    provider.close();page.close()
    return result

def collect(context,paper,record,task,gateway):
    page=context.new_page();before=len(record['evidence'])
    try:
        gateway_asset=r.artifact(paper['paper_id'],'firefox-provider-gateway.json',json.dumps(gateway,ensure_ascii=False,indent=2),gateway['url'],'provider-gateway','application/json')
        if gateway_asset['path'] not in {a['path'] for a in record['evidence']}:record['evidence'].append(gateway_asset)
        body,timed_out=visit_body(page,task['target'])
        links=page.locator('a[href]:visible').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))')
        payload={'url':r.public_url(page.url),'text':body,'links':[{**x,'url':r.public_url(x['url'])} for x in links],'browser':'firefox','navigation_timed_out':timed_out,'institution_gateway_visible_search':gateway.get('visible_search_input',False),'gateway_evidence_path':gateway_asset['path']}
        source=r.artifact(paper['paper_id'],'firefox-source-links.json',json.dumps(payload,ensure_ascii=False,indent=2),task['target'],'source-link-inventory','application/json');record['evidence'].append(source)
        r.attempt(record,task['target'],page.url,'Native Firefox actual visible provider body retained; navigation timeout='+str(timed_out))
        if not body.strip() or body.strip().lower() in {'loading','loading...','불러오는 중...'}:
            task.update(status='retry',reason='Native provider body is still empty/loading; no availability conclusion.',evidence_paths=[source['path']]);return
        if re.search(r'CPE00001|captcha|Are you a robot|보안 확인|Verify you are human|Access Denied',body,re.I):
            task.update(status='done',reason='Actual native Firefox individual provider page still presents content failure or human-verification barrier; source evidence is retained for independent availability review.',evidence_paths=[source['path']]);return
        metadata=page.locator('meta[name^="citation_"]').evaluate_all('(es)=>es.map(e=>({name:e.name,value:e.content}))')
        ma=r.artifact(paper['paper_id'],'firefox-citation-metadata.json',json.dumps(metadata,ensure_ascii=False,indent=2),page.url,'publisher-metadata','application/json');record['evidence'].append(ma)
        values=lambda name:'; '.join(x['value'] for x in metadata if x['name']==name)
        title=values('citation_title');authors=observed_byline(metadata,body);dates='; '.join(values(name) for name in ['citation_date','citation_publication_date','citation_online_date','citation_year'])
        bound=provider_identity(paper,metadata,body,page.url)
        record.setdefault('native_provider_bindings',[]).append({'url':r.public_url(page.url),'title':title,'authors':authors,'dates':dates,'target_match':bound})
        if bound:
            prior=record['abstract'] if record['abstract']['status']=='found' else None
            pdf_state=wait_pdf_links(page,page.url)
            pdf_proof=r.artifact(paper['paper_id'],'native-pdf-control.json',json.dumps(pdf_state,ensure_ascii=False,indent=2),page.url,'pdf-control-observation','application/json');record['evidence'].append(pdf_proof)
            r.inspect_publisher(page,paper,record,byline=authors,pdf_candidates=pdf_state['links'])
            if pdf_state['pending'] and record['fulltext']['status']!='found':
                record['fulltext']={'status':'unresolved','reason':'Visible target View PDF control still has no initialized href after actual bounded wait.'}
            if prior:record['abstract']=prior
            heading=page.locator('#abstracts').get_by_role('heading',name='Abstract',exact=True)
            if heading.count()==1 and not prior:
                node=heading.locator('xpath=..');fragment=node.inner_html();text=node.inner_text()
                raw=r.artifact(paper['paper_id'],'firefox-abstract-original.html',fragment,page.url,'publisher-abstract-dom','text/html');record['evidence'].append(raw)
                if len(text)>40 and not re.search(r'No abstract available|Abstract\s+Not available',text,re.I) and not re.search(r'<(?:img|iframe|video|audio|object|embed)\b',fragment,re.I):
                    asset=r.artifact(paper['paper_id'],'firefox-abstract.html',abstract_html(fragment,title),page.url,'publisher-abstract','text/html')
                    record.setdefault('abstract_source_history',[]).append(record['abstract'])
                    record['abstract']={'status':'found','source_kind':'publisher_abstract_html','artifacts':[asset],'extraction_quality':'original_mathml_preserved'}
                    record['work_state']['reviews']['abstract']={'basis_sha256':work_queue.component_basis(record,'abstract'),'reason':'Actual publisher citation title, authors, year and available DOI bind the target. Exact Abstract heading container is isolated; its source HTML/MathML is preserved without flattening indices or exponents, and no external media is needed.','evidence_paths':[source['path'],ma['path'],raw['path'],asset['path']],'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'test':'kudos-recovery/g08/test_native_source.py'}
        pending=bound and pdf_state['pending'] and record['fulltext']['status']!='found'
        task.update(status='retry' if pending else 'done',reason='Target PDF control still awaits initialized href; no absence/access conclusion.' if pending else 'Actual native Firefox source body, citation metadata and visible links inspected. Target binding='+str(bound)+'; unresolved content/edition review remains separate.',evidence_paths=[a['path'] for a in record['evidence'][before:]])
    except Exception as exc:
        a=r.artifact(paper['paper_id'],'firefox-source-error.txt',type(exc).__name__+': '+str(exc).split('Call log:')[0],task['target'],'failure');record['evidence'].append(a)
        task.update(status='retry',reason='Native provider navigation/UI failed: '+type(exc).__name__,evidence_paths=[a['path']])
    finally:page.close()
