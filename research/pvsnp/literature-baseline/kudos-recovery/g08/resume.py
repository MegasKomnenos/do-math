"""Resume g08 from preserved evidence and the shared remaining-work queue."""
import argparse
import hashlib
import json
import os
import sys
import subprocess
import time
from pathlib import Path
import recover as r
import reconcile
import content_review
import scope_review
import source_inventory

sys.path.insert(0,str(r.ROOT.parent))
import work_queue

def task(kind,target,status,reason,paths=(),**extra):
    return dict(key=kind+':'+hashlib.sha256(target.encode()).hexdigest()[:16],kind=kind,target=target,status=status,reason=reason,evidence_paths=list(paths),**extra)

def narrow_query(query,paper):
    return query+' '+str(paper['year']) if paper.get('year') and str(paper['year']) not in query else query

def fielded_query(paper):
    def value(s):return ' '.join(r.re.sub(r'[():{}"\\\[\]]',' ',r.plain_title(s)).split())
    title=value(paper['title'])
    names=r.named_authors(paper)
    author=value(names[0].split(',')[0]) if names else ''
    return '(TitleCombined:('+title+'))'+(' AND (AuthorCombined:('+author+'))' if author else '')

def verify_results(partial=True):
    command=[sys.executable,str(r.ROOT.parent/'check_recovery.py'),'--assignment',str(r.ROOT/'assignment.json')]
    if partial:command.append('--partial')
    checked=subprocess.run(command,capture_output=True,text=True,encoding='utf-8')
    output=json.loads(checked.stdout) if checked.stdout.strip() else {'stderr':checked.stderr}
    r.save_json(r.ROOT/'latest-check.json',output)
    return {'command':command,'exit_code':checked.returncode,'passed':output.get('passed'),'complete':output.get('complete')}

def accept_linked_pdf(paper,record,data,url):
    if not r.valid_pdf(data):return False
    asset=r.artifact(paper['paper_id'],'linked-source.pdf',data,url,'unconfirmed-pdf','application/pdf')
    if (asset['path'],asset['url']) not in {(a['path'],a.get('url')) for a in record['evidence']}:
        record['evidence'].append(asset)
    t=task('pdf',asset['path'],'needs_review','Observed source URL yielded a readable PDF. Verify target identity, edition, article boundaries and abstract before counting it.',[asset['path']])
    if not any(x['key']==t['key'] for x in record['work_state']['tasks']):record['work_state']['tasks'].append(t)
    return True

def pending_ui_tasks(record,attempted=(),engine='chrome'):
    return [t for t in record['work_state']['tasks'] if t['key'] not in attempted and t['status'] in {'pending','retry'} and t['kind'] in {'search','source'} and t.get('engine')!='public_web' and t.get('browser','chrome')==engine]

def parse_duplicate_stub(text,paper):
    lines=[x.strip() for x in text.splitlines() if x.strip()]
    if len(lines)<3 or lines[1]!='Duplicate':return None
    observed=r.re.search(r'MR0*(\d+)',lines[0])
    expected=paper['publication']['source_record']['record_id'].removeprefix('MR')
    if not observed or int(observed[1])!=int(expected):return None
    if r.normalize_title(' '.join(lines[2:]))!=r.normalize_title(r.plain_title(paper['title'])):return None
    return {'record_id':lines[0],'title':' '.join(lines[2:])}

def visit_mathscinet(ctx,paper,record,t):
    pages=[]
    try:
        gateway=ctx.new_page();pages.append(gateway)
        gateway.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542',wait_until='domcontentloaded',timeout=30000)
        gateway.locator('#search_order').fill('MathSciNet');gateway.locator('#search_order').press('Enter')
        with ctx.expect_page(timeout=30000) as opened:
            gateway.get_by_text('바로가기',exact=True).click()
        page=opened.value;pages.append(page)
        page.wait_for_url('**/publications-search',timeout=40000)
        mr=paper['publication']['source_record']['record_id']
        page.locator('#searchTextInput').fill(mr);page.locator('#searchTextInput').press('Enter')
        page.wait_for_url('**/article?mr=*',timeout=30000)
        page.locator('.bibliography').first.or_(page.get_by_text('Duplicate',exact=True)).first.wait_for(timeout=30000)
        text=r.capture_text(page)
        duplicate=parse_duplicate_stub(text,paper)
        if duplicate:
            main=page.locator('main').first if page.locator('main').count() else page.locator('body')
            links=main.locator('a[href]').evaluate_all('(es)=>es.map(e=>({text:e.innerText,url:e.href}))')
            a=r.artifact(paper['paper_id'],'mathscinet-duplicate-stub.json',json.dumps({'text':text,'url':r.public_url(page.url),'links':[{**x,'url':r.public_url(x['url'])} for x in links]},ensure_ascii=False,indent=2),page.url,'mr-duplicate-stub','application/json')
            record['evidence'].append(a);record['duplicate_stub']=duplicate
            record['mathscinet_article_link_enabled']=bool(r.article_link(main))
            record['mathscinet_article_href']=r.article_link(main)
            record['mr_link_scope_version']='per-record/1'
            t.update(status='done',reason='Actual MR duplicate stub and its visible links inspected. It has no bibliography; independent title/author/edition resolution remains open.',evidence_paths=[a['path']])
            r.attempt(record,mr,page.url,'Observed Duplicate stub; did not invent bibliography or an alias')
            return
        scope=r.article_scope(page,mr);heading=r.read_heading(scope)
        bibliography=scope.locator('.bibliography').first.inner_text()
        body=r.artifact(paper['paper_id'],'mathscinet-detail.txt',r.capture_text(page),page.url)
        scoped=r.artifact(paper['paper_id'],'mathscinet-scoped-bibliography.txt',heading+'\n'+bibliography,page.url,'mr-scoped-bibliography')
        record['evidence'].extend([body,scoped])
        bound=r.bind_mr(paper,heading,bibliography)
        record['identity']={'status':'confirmed' if bound else 'unresolved','reason':'New actual KUDOS MathSciNet UI: scoped MR/title/all named authors/year comparison '+str(bound),'observed_bibliography':bibliography}
        review=page.locator('.review-text').first
        if review.count():
            a=r.artifact(paper['paper_id'],'mathscinet-review.txt',review.inner_text(),page.url,'review')
            record['review']={'grouped':page.locator('div.article').count()>1,'source_kind':'MathSciNet review or explicitly labelled summary','artifacts':[a]}
            record['evidence'].append(a)
        href=r.article_link(scope)
        button=scope.get_by_role('button',name='Article',exact=True)
        enabled=bool(href) or bool(button.count() and button.first.is_enabled())
        if enabled and not href:
            destination=r.click_article(page,scope)
            if destination:
                href=destination.url
                if destination is not page:pages.append(destination)
        record.update(mathscinet_article_link_enabled=enabled,mathscinet_article_href=r.public_url(href) if href else None,mr_link_scope_version='per-record/1')
        if href:
            new=task('source',r.public_url(href),'pending','Actual per-record MathSciNet Article link.')
            if not any(x['key']==new['key'] for x in record['work_state']['tasks']):record['work_state']['tasks'].append(new)
        t.update(status='done',reason='Actual KUDOS gateway and per-record MathSciNet UI inspected; scoped bibliography and Article availability retained.',evidence_paths=[body['path'],scoped['path']])
        if record.get('collection_error'):
            record.setdefault('superseded_flags',[]).append({'flag':'collection_error','value':record.pop('collection_error'),'reason':'Previously incomplete MathSciNet retrieval now completed through actual institution UI.','evidence_paths':t['evidence_paths']})
        r.attempt(record,mr,page.url,'Completed resumed per-record MR UI inspection')
    except Exception as exc:
        a=r.artifact(paper['paper_id'],'mathscinet-resume-error.txt',type(exc).__name__+': '+str(exc).split('Call log:')[0],r.MS_SEARCH,'failure')
        record['evidence'].append(a)
        t.update(status='retry',reason='Actual MR UI retry failed: '+type(exc).__name__,evidence_paths=[a['path']])
    finally:
        for page in pages:
            if not page.is_closed():page.close()

def deduplicate_sources(record):
    groups={}
    for asset in record['evidence']:
        if asset.get('kind')!='ui-search-response':continue
        payload=json.loads((r.BASE/asset['path']).read_text(encoding='utf-8'))
        for doc in payload.get('documents',[]):
            if not doc.get('id') or not doc.get('link'):continue
            key=(doc['id'],r.normalize_title(doc.get('full_title') or doc.get('title') or ''),r.normalize_title(r.document_creators(doc)),tuple(doc.get('publication_years') or []),tuple(doc.get('dois') or []),tuple(doc.get('start_pages') or []),tuple(doc.get('end_pages') or []),doc.get('content_type'))
            groups.setdefault(key,{}).setdefault(doc['link'],[]).append(asset['path'])
    tasks=record['work_state']['tasks']
    for key,links in groups.items():
        matching=[t for t in tasks if t['kind']=='source' and t['target'] in links]
        if len(matching)<2:continue
        representative=next((t for t in matching if t['status']=='done'),matching[0])
        for t in matching:
            if t is representative or t['status']=='done':continue
            if representative['status']=='done':
                t.update(status='not_needed',reason='Same observed Summon document id, normalized complete title/creators, year, DOI, page span and content type as the representative whose actual destination and outgoing links were visited.',evidence_paths=list(dict.fromkeys(links[t['target']]+representative['evidence_paths'])),representative=representative['key'])
            else:
                t.update(status='needs_review',reason='Same verified UI document fields as pending representative; await its actual source visit before closing this link variant.',representative=representative['key'])
    deduplicate_resolver_sources(record)

def deduplicate_resolver_sources(record):
    evidence={a['path']:a for a in record['evidence']}
    captures={p:json.loads((r.BASE/p).read_text(encoding='utf-8')) for p,a in evidence.items() if a.get('kind')=='source-link-inventory'}
    groups={}
    for t in record['work_state']['tasks']:
        if t['kind']!='source':continue
        u=r.urlsplit(t['target']);q=r.parse_qs(u.query)
        if not u.netloc.endswith('search.serialssolutions.com') or not q.get('SS_jc') or not q.get('SS_V'):continue
        key=(u.netloc,tuple(q['SS_jc']),tuple(q['SS_V']),tuple(q.get('SS_LibHash',[])))
        groups.setdefault(key,[]).append(t)
    for group in groups.values():
        visited=[t for t in group if t['status']=='done']
        if len(visited)<2:continue
        destinations=set();paths=[];unknown=False
        for t in visited:
            matched=False
            for p in t.get('evidence_paths',[]):
                if p not in captures:continue
                u=r.urlsplit(captures[p].get('url',''));q=r.parse_qs(u.query)
                specific={k:v for k,v in q.items() if k.lower() in {'docid','doi','isbn'}}
                if not specific and '/search/details/' not in u.path:
                    unknown=True;continue
                destinations.add((u.netloc,u.path,json.dumps(specific,sort_keys=True)))
                paths.append(p);matched=True
            if not matched:unknown=True
        if unknown or len(destinations)!=1:continue
        for t in group:
            if t['status'] not in work_queue.OPEN:continue
            origins=[p for p,c in captures.items() if any(link.get('url')==t['target'] for link in c.get('links',[]))]
            t.update(status='not_needed',reason='Same observed resolver coverage identifier and edition variant; at least two distinct link variants already reached the identical document-specific provider URL. Generic home/login destinations are excluded from this rule.',evidence_paths=list(dict.fromkeys(paths+origins)),representative=visited[0]['key'])

def inventory(record,paper):
    existing={t['key']:t for t in record.get('work_state',{}).get('tasks',[])}
    tasks=[]
    def add(t):
        if any(x['key']==t['key'] for x in tasks):return
        old=existing.get(t['key'])
        tasks.append(old if old and (old.get('status') in work_queue.CLOSED or (old.get('kind')=='source' and old.get('status') in work_queue.OPEN)) else t)
    evidence=record['evidence']
    mr=[a['path'] for a in evidence if a.get('kind') in {'mr-scoped-bibliography','mr-duplicate-stub'}]
    add(task('source','MathSciNet detail','done' if mr else 'pending','Saved per-record bibliography or explicitly inspected duplicate stub available; identity is reviewed separately.' if mr else 'MR scoped bibliography must be recovered.',mr[-1:]))
    queries=dict.fromkeys([r.first_query(paper),'"'+r.plain_title(paper['title'])+'" '+(paper['authors'][0].split(',')[0] if paper['authors'] else '')])
    captures={}
    source_links=set(paper.get('source_urls',[]))
    if record.get('mathscinet_article_href'):
        source_links.add(record['mathscinet_article_href'])
    for a in evidence:
        if a.get('kind')=='source-link-inventory':
            payload=json.loads((r.BASE/a['path']).read_text(encoding='utf-8'))
            source_links.update(x['url'] for x in source_inventory.followups(payload))
        if a.get('kind')=='ui-search-response':
            data=json.loads((r.BASE/a['path']).read_text(encoding='utf-8'))
            if data.get('holdings_only') is False:
                captures[data.get('original_query')]=(a,data)
                for doc in data.get('documents',[]):
                    if doc.get('link') and r.normalize_title(doc.get('full_title') or doc.get('title') or '')==r.normalize_title(r.plain_title(paper['title'])) and all(r.author_matches(n,r.document_creators(doc)) for n in r.named_authors(paper)):
                        source_links.add(doc['link'])
                source_links.update(doc['link'] for doc in r.response_documents(paper,data) if doc.get('link'))
    for query in queries:
        a,data=captures.get(query,({},{}))
        count=data.get('record_count') or 0
        got=len(data.get('documents',[]))
        truncated=count>got
        narrowed=[x for x in record.get('narrowed_searches',[]) if x['broad_query']==query]
        status='needs_review' if narrowed or truncated else ('pending' if not a else 'done')
        add(task('search',query,status,'Retained narrowed UI search needs scope review.' if narrowed else ('Search capture needs missing result pages.' if truncated else ('Current ho=f UI search response retained.' if a else 'Required query has no ho=f capture.')),[a['path']] if a else [],discovered=max(count,got),attempted=got,remaining=max(0,count-got)))
        if truncated:
            refined=fielded_query(paper)
            fa,fd=captures.get(refined,({},{}))
            fc=fd.get('record_count') or 0;fg=len(fd.get('documents',[]))
            add(task('search',refined,'done' if fa and fc<=fg else 'pending','Actual indexed title/author query covers its complete returned record set.' if fa and fc<=fg else 'Refine fulltext/citation matches with observed TitleCombined/AuthorCombined UI query syntax.',[fa['path']] if fa else [],discovered=max(fc,fg),attempted=fg,remaining=max(0,fc-fg)))
            identifiers=paper.get('identifiers',{}).get('doi',[])+paper.get('identifiers',{}).get('isbn',[])
            if fa and fc<=fg and query not in identifiers:
                for current in tasks:
                    if current['kind']=='search' and current['target']==query:
                        current.update(status='not_needed',reason='Complete actual indexed title/author search supersedes broad fulltext and citation matches. Edition/identity of returned candidates is assessed separately.',evidence_paths=[fa['path'],a['path']])
    for url in sorted(source_links):
        # A resolver landing page is an intermediate source, not a failed publisher identity.
        captures_for_url=[a for a in evidence if a.get('url')==url and a.get('kind') in {'detail-page','source-link-inventory','failure-page','empty-page-observation'}]
        proven=[a for a in captures_for_url if a.get('kind')=='source-link-inventory' and not source_inventory.incomplete_body(json.loads((r.BASE/a['path']).read_text(encoding='utf-8')).get('text',''))]
        add(task('source',url,'done' if proven else 'pending','Actual source links and source body inventoried.' if proven else 'Follow the observed source and inventory its actual outgoing fulltext links.',[a['path'] for a in proven[-1:]]))
    accepted={a['path'] for a in record.get('fulltext',{}).get('artifacts',[]) if record['fulltext']['status']=='found'}
    for a in evidence:
        if a.get('kind')=='unconfirmed-pdf' and a.get('media_type')=='application/pdf' and a['path'] not in accepted:
            add(task('pdf',a['path'],'needs_review','Actual publisher download yielded a PDF whose identity/edition/complete range still needs content review.',[a['path']]))
    for component in work_queue.COMPONENTS:
        if record.get('work_state',{}).get('reviews',{}).get(component,{}).get('basis_sha256')!=work_queue.component_basis(record,component):
            add(task('review',component,'needs_review','Inspect current component content, identity and required search/source scope.'))
    keys={t['key'] for t in tasks}
    tasks.extend(t for key,t in existing.items() if key not in keys)
    return tasks

def attach_source_evidence(record):
    known={a['path'] for a in record['evidence']}
    for component in ('review','description'):
        for asset in record.get(component,{}).get('artifacts',[]):
            data=(r.BASE/asset['path']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=asset['sha256']:
                raise ValueError('Auxiliary source artifact digest mismatch: '+asset['path'])
            if asset['path'] not in known:
                record['evidence'].append(dict(asset));known.add(asset['path'])

def offline():
    papers={p['paper_id']:p for p in map(json.loads,(r.BASE/r.ASSIGNMENT['members_path']).read_text(encoding='utf-8-sig').splitlines())}
    reused=0
    for pid,paper in papers.items():
        path=r.ROOT/'results'/f'{pid}.json'
        record=json.loads(path.read_text(encoding='utf-8'))
        fixed=reconcile.reconcile(record,paper,r.BASE)
        attach_source_evidence(fixed)
        for a in list(fixed['evidence']):
            if a.get('kind')=='ui-search-response':
                data=json.loads((r.BASE/a['path']).read_text(encoding='utf-8'))
                for doc in r.response_documents(paper,data):
                    for abstract in doc.get('abstracts') or []:
                        r.preserve_database_abstract(paper,fixed,abstract,a['url'],doc)
        tasks=inventory(fixed,paper)
        state=fixed.setdefault('work_state',{'version':work_queue.VERSION,'reviews':{}})
        state['version']=work_queue.VERSION
        state['tasks']=tasks
        deduplicate_sources(fixed)
        state.setdefault('reviews',{}).update(content_review.assess(fixed,paper))
        state['reviews'].update(scope_review.assess_absence(fixed,paper))
        for t in state['tasks']:
            if t['kind']=='review' and t['target'] in state['reviews']:
                review=state['reviews'][t['target']]
                if review['basis_sha256']==work_queue.component_basis(fixed,t['target']):
                    t.update(status='done',reason=review['reason'],evidence_paths=review['evidence_paths'])
        if all(fixed[c]['status']=='found' and state['reviews'].get(c,{}).get('basis_sha256')==work_queue.component_basis(fixed,c) for c in ('abstract','fulltext')):
            paths=list(dict.fromkeys(state['reviews']['abstract']['evidence_paths']+state['reviews']['fulltext']['evidence_paths']))
            for t in state['tasks']:
                if t['status'] in work_queue.OPEN and t['kind'] in {'search','source','pdf'}:
                    t.update(status='not_needed',reason='Both target abstract and complete fulltext are content-verified; additional retrieval does not improve these fulfilled collection goals.',evidence_paths=paths)
            for flag in ('unvisited_link','unvisited_search_pages','collection_error','needs_mathscinet_revisit'):
                if fixed.get(flag):
                    fixed.setdefault('superseded_flags',[]).append({'flag':flag,'value':fixed.pop(flag),'reason':'Both collection goals now content-verified.','evidence_paths':paths})
        reused+=sum(t['status']=='done' for t in tasks)
        if fixed!=record:
            r.save_json(path,fixed)
    return papers,reused

def visit_source(ctx,paper,record,t):
    page=ctx.new_page()
    before=len(record['evidence'])
    try:
        if r.urlsplit(t['target']).path.lower().endswith('.pdf') or t.get('media_type')=='application/pdf':
            metrics=record.setdefault('collection_metrics',{})
            metrics['download_requests']=metrics.get('download_requests',0)+1
            response=ctx.request.get(t['target'],timeout=45000)
            if accept_linked_pdf(paper,record,response.body(),t['target']):
                t.update(status='done',reason='Downloaded actual observed source PDF; its content/region review is a separate PDF task.',evidence_paths=[a['path'] for a in record['evidence'][before:]] or [next(a['path'] for a in record['evidence'] if a.get('url')==t['target'] and a.get('media_type')=='application/pdf')])
                return
        response=page.goto(t['target'],wait_until='domcontentloaded',timeout=30000)
        page.wait_for_timeout(1500)
        if t.get('wait_text'):page.get_by_text(t['wait_text'],exact=False).first.wait_for(state='visible',timeout=25000)
        expansion={}
        text=source_inventory.capture_ready(page,expand_label=t.get('expand_label'),observation=expansion)
        links=page.locator('a[href]').evaluate_all('(es)=>es.filter(e=>e.offsetWidth||e.offsetHeight).map(e=>({text:e.innerText,url:e.href}))')
        asset=r.artifact(paper['paper_id'],'source-links.json',json.dumps({'url':r.public_url(page.url),'status':response.status if response else None,'text':text,'links':[{**x,'url':r.public_url(x['url'])} for x in links],'expansion':expansion},ensure_ascii=False,indent=2),t['target'],'source-link-inventory','application/json')
        record['evidence'].append(asset)
        r.inspect_publisher(page,paper,record)
        onward=source_inventory.followups({'url':page.url,'links':links})
        if onward:
            known={x['target'] for x in record['work_state']['tasks']}
            for x in onward:
                if x['url'] not in known:
                    record['work_state']['tasks'].append(task('source',x['url'],'pending','Observed outgoing link from institutional resolver.'))
        if source_inventory.incomplete_body(text) or 'Observation: the page body was empty' in text:
            t.update(status='retry',reason='Source body empty after navigation; direct PDF or delayed rendering still needs inspection.')
        else:
            t.update(status='done',reason='Navigated actual source; preserved full visible body and outgoing link inventory.',evidence_paths=[a['path'] for a in record['evidence'][before:]])
        r.attempt(record,t['target'],page.url,'Resumed source inspection and preserved actual outgoing link inventory')
    except Exception as exc:
        asset=r.artifact(paper['paper_id'],'resume-source-failure.txt',type(exc).__name__+': '+str(exc).split('Call log:')[0],t['target'],'failure')
        record['evidence'].append(asset)
        t.update(status='retry',reason='Actual source navigation failed: '+type(exc).__name__,evidence_paths=[asset['path']])
    finally:
        page.close()

def run(limit=None,offline_only=False,paper_id=None,engine='chrome'):
    import native_source
    started=time.time()
    run_id=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+str(os.getpid())
    manifest={'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pid':os.getpid(),'argv':sys.argv,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),r.ROOT/'recover.py',r.ROOT/'reconcile.py',r.ROOT/'content_review.py',r.ROOT/'scope_review.py',r.ROOT/'source_inventory.py',r.ROOT/'native_source.py',r.ROOT.parent/'work_queue.py',r.ROOT.parent/'check_recovery.py']}}
    r.save_json(r.ROOT/'runs'/f'{run_id}.json',manifest)
    papers,reused=offline()
    queue=work_queue.build_queue(r.ROOT/'assignment.json')
    r.save_json(r.ROOT/'work-queue.json',queue)
    metrics={'saved_evidence_reused':reused,'searches':0,'source_visits':0,'downloads':0,'papers_changed':0}
    if not offline_only:
        with r.sync_playwright() as pw:
            browser=pw.firefox.launch(headless=True) if engine=='firefox' else pw.chromium.launch(channel='chrome',headless=True)
            ctx=browser.new_context(storage_state=r.ASSIGNMENT['browser_state'],accept_downloads=True)
            ctx.set_default_timeout(12000)
            gateway=native_source.institution_gateway(ctx) if engine=='firefox' else {}
            if gateway:r.save_json(r.ROOT/'runs'/f'{run_id}-provider-gateway.json',gateway)
            selected=0
            for item in queue['entries']:
                if paper_id and item['paper_id']!=paper_id:continue
                path=r.ROOT/'results'/f"{item['paper_id']}.json"
                record=json.loads(path.read_text(encoding='utf-8'))
                active=pending_ui_tasks(record,engine=engine)
                if not active:
                    continue
                paper=papers[item['paper_id']]
                attempted=set()
                while pending_ui_tasks(record,attempted,engine):
                    t=pending_ui_tasks(record,attempted,engine)[0]
                    attempted.add(t['key'])
                    tick=time.monotonic()
                    before_metrics=dict(record.get('collection_metrics',{}))
                    if t['kind']=='source':
                        if engine=='firefox':native_source.collect(ctx,paper,record,t,gateway)
                        elif t['target']=='MathSciNet detail':visit_mathscinet(ctx,paper,record,t)
                        else:visit_source(ctx,paper,record,t)
                        metrics['source_visits']+=1
                    else:
                        page=ctx.new_page()
                        try:
                            query=t['target']
                            r.summon_query(page,paper,record,query,inspect_links=False)
                            if query!=t['target']:
                                evidence=[a for a in record['evidence'] if a.get('kind')=='ui-search-response'][-1]
                                data=json.loads((r.BASE/evidence['path']).read_text(encoding='utf-8'))
                                record.setdefault('narrowed_searches',[]).append({'broad_query':t['target'],'narrow_query':query,'evidence_path':evidence['path'],'record_count':data['record_count'],'saved_count':len(data['documents'])})
                            t.update(status='needs_review',reason='New UI response retained; inspect result coverage before closing query.')
                        except Exception as exc:
                            t.update(status='retry',reason='Summon UI failed: '+type(exc).__name__)
                        finally:
                            page.close()
                        metrics['searches']+=1
                    t['elapsed_seconds']=round(time.monotonic()-tick,3)
                    after_metrics=record.get('collection_metrics',{})
                    metrics['downloads']+=after_metrics.get('download_requests',0)-before_metrics.get('download_requests',0)
                    metrics['publisher_visits']=metrics.get('publisher_visits',0)+after_metrics.get('publisher_visits',0)-before_metrics.get('publisher_visits',0)
                    metrics['publisher_seconds']=round(metrics.get('publisher_seconds',0)+after_metrics.get('publisher_seconds',0)-before_metrics.get('publisher_seconds',0),3)
                    if t['kind']=='search' or t['target']=='MathSciNet detail':
                        record['work_state']['tasks']=inventory(record,paper)
                    deduplicate_sources(record)
                    r.save_json(path,record)
                metrics['papers_changed']+=1
                selected+=1
                r.save_json(r.ROOT/'progress-resume.json',dict(metrics,last_paper_id=paper['paper_id'],elapsed_seconds=round(time.time()-started,2)))
                print(json.dumps(dict(metrics,last_paper_id=paper['paper_id']),ensure_ascii=False),flush=True)
                if limit and selected>=limit:
                    break
            browser.close()
    queue=work_queue.build_queue(r.ROOT/'assignment.json')
    r.save_json(r.ROOT/'work-queue.json',queue)
    check=verify_results(partial=bool(queue['counts']['papers_with_remaining_work']))
    manifest.update(finished_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),elapsed_seconds=round(time.time()-started,3),metrics=metrics,queue_counts=queue['counts'],check=check)
    r.save_json(r.ROOT/'runs'/f'{run_id}.json',manifest)
    print(json.dumps(manifest,ensure_ascii=False),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--limit',type=int)
    parser.add_argument('--offline-only',action='store_true')
    parser.add_argument('--paper-id')
    parser.add_argument('--engine',choices=['chrome','firefox'],default='chrome')
    args=parser.parse_args()
    run(args.limit,args.offline_only,args.paper_id,args.engine)
