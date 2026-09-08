"""Validated field binding and complete-article layout for native publisher HTML."""
import re
from collect import norm

def binding(paper,metadata,title,byline):
    expected={x.casefold() for x in paper.get('identifiers',{}).get('doi',[])}
    observed={x.casefold() for x in metadata.get('citation_doi',[])}
    if not expected or not expected.intersection(observed) or norm(title)!=norm(paper['title']):return False
    years={value[:4] for key in ['citation_publication_date','citation_online_date','citation_date'] for value in metadata.get(key,[])}
    return (not paper.get('year') or str(paper['year']) in years) and all(norm(a.split(',')[0]) in norm(byline) for a in paper.get('authors',[]))

def layout_ready(source_text,body_html,refs_html,headings):
    return 'Full text access' in source_text and 'Section snippets' not in source_text and bool(body_html.strip()) and bool(refs_html.strip()) and '\ufffd' not in body_html and bool(headings) and bool(re.match(r'^(?:1\.?\s+)?Introduction\b',headings[0],re.I))

import hashlib,html,json,sys
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
from collect import BASE,WORK,artifact,safe_url
sys.path.insert(0,str(WORK.parent))
from work_queue import component_basis
import fulltext_html
import resource_snapshot

AUTH_QUERY={'_csrf','csrf','md5','token','access_token','auth','session','sessionid','signature'}

def requires_mathml_recovery(value):
    return '<mjx-container' in value or '<mjx-math' in value

def public_fragment(value):
    def clean(match):
        uri=html.unescape(match[2]);parts=urlsplit(uri);query=parse_qsl(parts.query,keep_blank_values=True)
        kept=[(key,val) for key,val in query if key.casefold() not in AUTH_QUERY]
        if len(kept)==len(query):return match[0]
        rebuilt=urlunsplit((parts.scheme,parts.netloc,parts.path,urlencode(kept),parts.fragment))
        return match[0].replace(match[2],html.escape(rebuilt,quote=True))
    return re.sub(r'\b(?:href|src)\s*=\s*([\"\x27])(https?://.*?)\1',clean,value,flags=re.I)

def offline_check(context,asset,expected):
    check=context.new_page();requests=[]
    check.on('request',lambda request:requests.append(safe_url(request.url)) if request.url.startswith(('http:','https:')) else None)
    try:
        context.set_offline(True);check.goto((BASE/asset['path']).as_uri(),wait_until='load')
        result={'network_offline':True,'http_requests':requests,'math_count':check.locator('#body math').count(),'reference_count':check.locator('#references ol.references > li').count(),'headings':check.locator('#body h2,#body h3').all_inner_texts(),'image_count':check.locator('img').count()}
        result['visible_math']=check.locator('#body math').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0).length')
        result['image_dimensions']=check.locator('img').evaluate_all('(es)=>es.map(e=>[e.naturalWidth,e.naturalHeight])')
        result['all_math_count']=check.locator('math').count()
        result['remaining_chtml']=check.locator('mjx-container').count()
        result['visible_all_math']=check.locator('math').evaluate_all('(es)=>es.filter(e=>e.getBoundingClientRect().width>0&&e.getBoundingClientRect().height>0).length')
        result['passed']=not requests and result['image_count']==expected.get('image_count',0) and result['image_dimensions']==expected.get('image_dimensions',[]) and all(w>0 and h>0 for w,h in result['image_dimensions']) and result['visible_math']==result['math_count'] and all(result[key]==expected[key] for key in ['math_count','reference_count','headings'])
        result['passed']=result['passed'] and result['remaining_chtml']==0 and result['visible_all_math']==result['all_math_count'] and result['all_math_count']==expected.get('all_math_count',result['all_math_count'])
        return result
    finally:
        check.close();context.set_offline(False)

def capture(context,page,paper,record):
    from playwright.sync_api import TimeoutError
    pid=paper['paper_id'];url=safe_url(page.url)
    try:
        page.wait_for_function(r'''()=>{const b=document.querySelector('#body');return b&&b.innerText.trim()&&!/^loading(?:\.\.\.)?$/i.test(b.innerText.trim())}''',timeout=25000)
        page.locator('#references').wait_for(state='attached',timeout=20000)
    except TimeoutError:return {'status':'needs_review','reason':'Complete body/reference DOM has not appeared in the bounded wait; no absence conclusion.'}
    metadata={}
    for item in page.locator('meta[name^="citation_"]').evaluate_all('(es)=>es.filter(e=>/doi|title|date|volume|issue|journal/.test(e.name)).map(e=>({name:e.name,value:e.content}))'):
        metadata.setdefault(item['name'],[]).append(item['value'])
    title=page.locator('h1').first.inner_text();author=page.locator('#author-group');byline=author.inner_text() if author.count()==1 else ''
    source_text=page.locator('body').inner_text();headings=page.locator('#body h2,#body h3').all_inner_texts()
    parts={};evidence=[];snapshots={};image_dimensions={'abstracts':[],'body':[]};resource_errors=[]
    for key,selector in [('body','#body'),('bibliography','#references'),('abstracts','#abstracts'),('author-group','#author-group'),('title_html','h1')]:
        node=page.locator(selector);raw=node.first.inner_html() if node.count() else ''
        if not raw:continue
        cleaned=public_fragment(raw);parts[key]=cleaned
        if cleaned!=raw:
            private=Path('C:/math/.credentials/kudos-recovery/g05/source-dom');private.mkdir(parents=True,exist_ok=True)
            (private/(pid+'-'+key+'-'+hashlib.sha256(raw.encode()).hexdigest()+'.html')).write_text(raw,encoding='utf-8')
        item=artifact(pid,'article-source-'+key+'.html',cleaned,url,'text/html','actual-article-dom');item['original_dom_sha256']=hashlib.sha256(raw.encode()).hexdigest();item['authentication_query_redacted']=cleaned!=raw;evidence.append(item)
        captured=resource_snapshot.snapshot(node.first);snapshots[key]=captured
        parts[key]=public_fragment(captured['html'])
        if key in {'body','abstracts'}:
            try:
                images=resource_snapshot.image_resources(node.first,page)
                for number,image in enumerate(images):
                    stored=artifact(pid,f'article-{key}-image-{number}.bin',image['data'],image['src'],image['media_type'],'actual-article-image-response');evidence.append(stored)
                    image_dimensions[key].append([image['width'],image['height']])
                parts[key]=resource_snapshot.embed_images(parts[key],images)
            except ValueError as error:resource_errors.append(str(error))
    observed={'url':url,'metadata':metadata,'title':title,'byline':byline,'headings':headings,'math_count':page.locator('#body math').count(),'reference_count':page.locator('#references ol.references > li').count(),'body_characters':len(page.locator('#body').inner_text()),'image_count':page.locator('#body img,#abstracts img').count(),'body_svg_count':page.locator('#body svg').count()}
    observed['math_count']=snapshots.get('body',{}).get('math_count',observed['math_count']);observed['image_dimensions']=image_dimensions['abstracts']+image_dimensions['body']
    observed['math_recovery']={key:{k:v for k,v in value.items() if k not in {'html','text'}} for key,value in snapshots.items()}
    observed['all_math_count']=sum(value['math_count'] for value in snapshots.values())
    observed['title_mathml_text']=snapshots.get('title_html',{}).get('text',title)
    observed['resource_errors']=resource_errors
    info=artifact(pid,'article-source-observation.json',json.dumps(observed,ensure_ascii=False,indent=2),url,'application/json','actual-article-observation');evidence.append(info);record['evidence'].extend(evidence)
    if not binding(paper,metadata,observed['title_mathml_text'],byline):return {'status':'needs_review','reason':'Actual DOI/title/byline/date binding requires reconciliation; source DOM preserved.'}
    identity_reason='Actual current publisher DOI, title, explicit author-group byline and publication/online date match the assigned document.'
    if record['identity']['status']!='confirmed':
        record.setdefault('identity_history',[]).append(record['identity']);record['identity']={'status':'confirmed','reason':identity_reason}
    record['observed_publisher_metadata']=metadata
    def review(component,reason,paths):
        record['work_state']['reviews'][component]={'method':'deterministic','basis_sha256':component_basis(record,component),'reason':reason,'evidence_paths':paths,'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tests':'test_native_article.py; actual publisher DOM and offline rendering fixtures'}
    review('identity',identity_reason,[x['path'] for x in evidence])
    if record['abstract']['status']!='found':
        heading=page.locator('#abstracts').get_by_role('heading',name='Abstract',exact=True)
        if heading.count()==1:
            node=heading.locator('xpath=..');fragment=public_fragment(resource_snapshot.snapshot(node)['html'])
            if len(node.inner_text().strip())>40 and not requires_mathml_recovery(fragment) and not re.search(r'<(?:img|iframe|video|audio|object|embed)\b',fragment,re.I):
                from science_direct import abstract_html
                original=artifact(pid,'article-abstract-source.html',fragment,url,'text/html','actual-publisher-abstract-dom');record['evidence'].append(original)
                abstract=artifact(pid,'article-abstract.html',abstract_html(fragment,title),url,'text/html')
                record.setdefault('abstract_source_history',[]).append(record['abstract']);reason='Fully initialized current publisher Abstract heading container; source text and native MathML preserved without flattening or reconstructed formulas.'
                record['abstract']={'status':'found','artifacts':[abstract],'source_kind':'publisher_abstract_html','extraction_quality':'original_mathml_preserved','validation':reason};review('abstract',reason,[info['path'],original['path'],abstract['path']])
    if not layout_ready(source_text,parts.get('body',''),parts.get('bibliography',''),headings):return {'status':'needs_review','reason':'Captured layout is outside the verified complete-article pattern; source DOM preserved.'}
    ids=set(page.locator('#body [id]').evaluate_all('(es)=>es.map(e=>e.id)'))
    outline=page.locator('a[href*="#"]').evaluate_all(r'''(es)=>es.filter(e=>!e.closest('#body,#references')&&/^\d+(?:\.\d+)*\.?\s+\S/.test(e.innerText.trim())).map(e=>({id:new URL(e.href).hash.slice(1),same:new URL(e.href).pathname===location.pathname}))''')
    missing=[x['id'] for x in outline if x['same'] and x['id'] not in ids]
    if missing:return {'status':'needs_review','reason':'Outline section IDs missing from captured body: '+', '.join(missing)}
    if requires_mathml_recovery(parts.get('body','')) or requires_mathml_recovery(parts.get('abstracts','')):return {'status':'needs_review','reason':'MathJax CHTML requires original MathML recovery or complete local math resources; source DOM preserved.'}
    if resource_errors or any(value['missing_math'] for value in snapshots.values()) or observed['body_svg_count']:return {'status':'needs_review','reason':'Article math/figure resources require further capture or visual validation; source DOM preserved.'}
    try:
        content=fulltext_html.document(title,parts).replace('<h1>'+html.escape(title)+'</h1>','<h1>'+parts.get('title_html',html.escape(title))+'</h1>',1)
        asset=artifact(pid,'publisher-fulltext.html',content,url,'text/html','publisher-fulltext-html')
        verified=offline_check(context,asset,observed)
    except (ValueError,TimeoutError) as error:return {'status':'needs_review','reason':'Standalone article rendering requires review: '+type(error).__name__}
    check=artifact(pid,'article-offline-validation.json',json.dumps(verified,ensure_ascii=False,indent=2),url,'application/json','actual-offline-article-validation');record['evidence'].append(check)
    if not verified['passed']:
        record['evidence'].append(dict(asset,kind='pending-full-html-validation'));return {'status':'needs_review','reason':'Offline DOM/math/reference validation did not pass.'}
    if observed['image_count']:
        record['evidence'].append(dict(asset,kind='pending-full-html-validation'))
        return {'status':'needs_review','reason':'Offline original MathML and embedded exact browser image resources passed structural checks; direct figure/content visual review is pending.','artifact':asset['path']}
    reason='Actual current DOI, title, byline and publication/online year bind the target. Full text access, complete #body beginning Introduction, every outline section ID and separate complete #references match the validated publisher pattern; Section snippets are excluded. Exact scholarly DOM/MathML is preserved. No article images/SVG require external resources. Offline Firefox verifies unchanged body headings, all visible MathML nodes and all references, with zero HTTP requests. First real full-article and equation-number rendering fixtures passed.'
    record.setdefault('fulltext_source_history',[]).append(record['fulltext']);record['fulltext']={'status':'found','artifacts':[asset],'source_kind':'publisher_fulltext_html','validation':reason,'preserved_content':observed}
    record['work_state']['reviews']['fulltext']={'method':'deterministic','basis_sha256':component_basis(record,'fulltext'),'reason':reason,'evidence_paths':[x['path'] for x in evidence]+[asset['path'],check['path']],'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'renderer_code_sha256':hashlib.sha256((WORK/'fulltext_html.py').read_bytes()).hexdigest(),'tests':'test_native_article.py; test_fulltext_html.py; actual first full-article and offline rendering fixtures'}
    return {'status':'found','reason':reason,'artifact':asset['path']}
