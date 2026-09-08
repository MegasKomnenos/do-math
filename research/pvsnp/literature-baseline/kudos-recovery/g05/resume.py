"""Resume g05; content review remains the worker's explicit responsibility."""
import argparse,hashlib,json,os,re,sys,time
import pymupdf
from pathlib import Path
from urllib.parse import urlsplit
from collect import BASE,WORK,save_json,artifact
sys.path.insert(0,str(WORK.parent))
from work_queue import build_queue,pending_work,component_basis,VERSION
from check_recovery import check_assignment
import summon_collect,acm_collect,regions,book_collect,science_direct

def inventory(record,paper,external):
    tasks=[]
    def add(key,kind,target,status='needs_review',reason='Read preserved evidence and decide the remaining action'):
        if not any(t['key']==key for t in tasks):tasks.append(dict(key=key,kind=kind,target=target,status=status,reason=reason))
    for c in ('identity','abstract','fulltext'):
        add('review:'+c,'review',c)
    for e in record.get('evidence',[]):
        if e.get('kind') in {'pending-identity','pending-bibliographic-verification','provider-abstract-candidate'}:
            add('candidate:'+e['path'],'review',e['path'])
    for x in external:add('external:'+x['artifact']['path'],'review',x['artifact']['path'])
    for e in record.get('abstract',{}).get('candidate_artifacts',[]):add('candidate:'+e['path'],'review',e['path'])
    complete_positive=all(record.get(c,{}).get('status')=='found' for c in ('abstract','fulltext'))
    if record.get('fulltext',{}).get('status')!='found' and any(d.startswith('10.1145/') for d in paper.get('identifiers',{}).get('doi',[])):
        pending_pdf=any(e.get('kind') in {'pending-identity','pending-bibliographic-verification'} for e in record.get('evidence',[]))
        if not pending_pdf:add('acm','source',acm_collect.SEED,'pending','Use observed institutional ACM search/detail/PDF path after public-source restriction')
    if not complete_positive:
        responses=[e for e in record.get('evidence',[]) if e.get('kind')=='actual-ui-search-response']
        if responses:
            for e in responses:add('search:'+e['path'],'search',e['path'])
        else:add('summon','search',paper.get('title') or record.get('metadata',{}).get('title','target'),'pending','No preserved beyond-holdings UI response')
        for url in paper.get('source_urls',[]):
            prior=[a for a in record.get('attempts',[]) if a.get('url')==url]
            captured=False
            for index,attempted in enumerate(record.get('scope_review',{}).get('source_urls_attempted_this_pass',[])):
                if attempted==summon_collect.safe_url(url) and any(Path(e['path']).name.startswith(f'wide-{index}-publisher') for e in record.get('evidence',[])):
                    captured=True
            add('source:'+url,'source',url,'needs_review' if prior or captured else 'pending','Assess observed source path or visit missing input source')
    return tasks

def external_items():
    items=[]
    for name in ('region-review.json','pending-pdf-review.json','root-pdf-review.json'):
        value=json.loads((WORK/name).read_text());items.extend(value.get('items',[]) if isinstance(value,dict) else value)
    return items

def refresh_inventory(record,paper,external):
    state=record.setdefault('work_state',{'version':VERSION,'tasks':[],'reviews':{}})
    known={t['key'] for t in state['tasks']}
    for task in inventory(record,paper,external):
        if task['key'] not in known:state['tasks'].append(task);known.add(task['key'])
        else:
            previous=next(t for t in state['tasks'] if t['key']==task['key'])
            if previous['status']=='pending' and previous.get('reason')=='Assess observed source path or visit missing input source' and task['status']=='needs_review':
                previous.update(status='needs_review',reason='Recorded source attempt has a corresponding preserved publisher capture; inspect that evidence before replaying the browser.')
    for task in pending_work(record):
        if task['key'] not in known:
            state['tasks'].append(dict(task,target=task['key'],status='needs_review'))
            known.add(task['key'])
        elif task['key'].startswith('review:'):
            previous=next(t for t in state['tasks'] if t['key']==task['key'])
            if previous['status'] in {'done','not_needed'}:previous.update(status='needs_review',reason=task['reason'])

def provider_parts(text):
    lines=text.splitlines()
    return {'body':'\n'.join(line for line in lines if not line.lstrip().startswith('•')).strip(),
            'highlights':'\n'.join(line for line in lines if line.lstrip().startswith('•')).strip()}

def complete_provider_variant(values):
    values=[v for v in values if v]
    if not values:return None
    longest=max(values,key=len);compact=re.sub(r'\s+','',longest)
    return longest if all(compact.startswith(re.sub(r'\s+','',v)) for v in values) else None

def provider_text_issue(text):
    if '\ufffd' in text or 'â\x80' in text or re.search(r'[A-Za-z]\?[A-Za-z]',text):return 'Replacement/mojibake or intraword missing-character marker in provider text'
    if re.search(r'\b\d+O\(|[ΣΠ]\d{2,}',text):return 'Ambiguous flattened mathematical indices or exponent structure; compare actual formatted source'
    return None

def retry_step(operation,wait=time.sleep):
    from playwright.sync_api import TimeoutError as BrowserTimeout
    for attempt in range(3):
        try:return operation()
        except (TimeoutError,BrowserTimeout):
            if attempt==2:raise
            wait(2*(attempt+1))

def finish_run(path):
    report=check_assignment(WORK/'assignment.json')
    save_json(path/'check.json',report)
    metrics=json.loads((path/'metrics.json').read_text()) if (path/'metrics.json').exists() else {}
    save_json(WORK/'progress.json',{'stage':'complete' if report['complete'] else 'remaining collection and content review',
        'total':report['assigned'],'processed':report['processed'],'unprocessed':report['missing'],
        'abstract_found':report['counts'].get('abstract:found',0),'fulltext_found':report['counts'].get('fulltext:found',0),
        'remaining':report['papers_with_remaining_work'],'component_counts':report['counts'],'complete':report['complete'],
        'last_paper_id':metrics.get('last_paper_id'),'checked_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g05/resume.py'})
    return report

def count_actions(attempts):
    outcomes=[a.get('outcome','') for a in attempts]
    return {'searches':sum('Actual ACM search UI' in s or 'Actual Springer search UI' in s or 'Actual UI search ho=f' in s for s in outcomes),
            'source_visits':sum(s.startswith(('Opened target title link','Actual publisher/normal source page')) for s in outcomes),
            'downloads':sum(s.startswith(('Observed download request attempt','Observed download timeout attempt')) for s in outcomes)}

def browser_type(pw,engine):
    return getattr(pw,engine)

def restricted_scope_evidence(record,paper):
    """Only individual complete queries and actually captured restricted routes."""
    if record.get('fulltext',{}).get('status')!='unavailable':return []
    for task in record.get('work_state',{}).get('tasks',[]):
        if task.get('status') in {'pending','retry'} and (task.get('kind') in {'search','pdf','repair'} or task.get('kind')=='source' and task.get('target','').startswith(('http://','https://'))):return []
    if any(record.get(k) for k in ('unvisited_link','unvisited_search_pages','collection_error')):return []
    if any(e.get('kind') in {'pending-identity','pending-bibliographic-verification'} for e in record.get('evidence',[])):return []
    scope=record.get('scope_review',{});attempted=scope.get('source_urls_attempted_this_pass',[])
    required=paper.get('source_urls',[])
    if not required or not all(summon_collect.safe_url(u) in attempted for u in required):return []
    if len(attempted)<len(set(required))+scope.get('normal_source_link_count_observed',0):return []
    searches=[];matched=False
    for e in record.get('evidence',[]):
        if e.get('kind')!='actual-ui-search-response':continue
        data=json.loads((BASE/e['path']).read_text());docs=data.get('documents',[])
        if data.get('scope')!='ho=f' or len(docs)<int(data.get('record_count') or 0):return []
        if summon_collect.choose_document(paper,docs):matched=True
        searches.append(e['path'])
    if not matched:return []
    latest={}
    for e in record.get('evidence',[]):
        if e.get('kind')=='publisher-page':latest[e['url']]=e
    if not latest or not any('.libproxy.knu.ac.kr' in urlsplit(u).hostname for u in latest):return []
    if any(urlsplit(u).hostname.endswith('search.serialssolutions.com') for u in latest):return []
    evidence=[]
    for e in latest.values():
        body=(BASE/e['path']).read_text()
        if not re.search(r'CPE\d+|Access Denied|보안 확인|Just a moment|Verify you are human|Unusual Traffic|403 Forbidden',body,re.I):return []
        evidence.append(e['path'])
    return searches+evidence

def review_saved(record,paper,external):
    """Apply bounded, tested source checks; uncertain content stays open."""
    state=record.setdefault('work_state',{'version':VERSION,'tasks':[],'reviews':{}})
    def intact(ar):
        p=BASE/ar['path']
        return p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==ar.get('sha256')
    def review(c,reason,paths):
        state['reviews'][c]={'basis_sha256':component_basis(record,c),'reason':reason,'evidence_paths':list(dict.fromkeys(paths)),
            'rule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'tests':'g05/test_restart.py; g05/test_collect.py; g05/test_summon.py; g05/test_regions.py'}
        for task in state['tasks']:
            if task['key']=='review:'+c:task.update(status='done',reason=reason,evidence_paths=list(dict.fromkeys(paths)))
    identity_paths=[];matched=None;documents=[]
    for ev in record.get('evidence',[]):
        if ev.get('kind')=='actual-ui-search-response' and intact(ev):
            data=json.loads((BASE/ev['path']).read_text())
            found=summon_collect.choose_document(paper,data.get('documents',[]))
            if found:identity_paths.append(ev['path']);matched=found
            documents.extend(data.get('documents',[]))
    matched=summon_collect.choose_document(paper,documents)
    if matched and identity_paths:
        if record.get('identity',{}).get('status')!='confirmed':record['identity']={'status':'confirmed','reason':'Actual saved UI response now passes validated complete title/DOI-or-ISBN, author/editor, year and document-type matching; original mismatch remains in preserved source history.'}
        review('identity','Saved actual UI response passes document_matches: complete title, matching returned DOI or matching assigned ISBN when returned DOI is absent, year, author/editor name tokens and compatible document type; highlighted-title, wrong-document and ISBN/editor-order fixtures passed.',identity_paths)
    f=record['fulltext'];a=record['abstract']
    if f.get('status')=='found' and f.get('artifacts') and intact(f['artifacts'][0]):
        src=f['artifacts'][0]
        try:
            with pymupdf.open(BASE/src['path']) as doc:
                if acm_collect.pdf_identity(paper,doc[0].get_text(),len(doc)):
                    review('fulltext','Actual preserved PDF opens; first-page title before references, author surnames, year and numeric target page-span length pass pdf_identity. Wrong-reference and truncated-page fixtures passed.',[src['path']])
                    if not identity_paths and record['identity']['status']=='confirmed':review('identity','Target title, input author surnames and year occur on actual PDF first page; target numeric span agrees with complete PDF length.',[src['path']])
        except Exception:pass
    prior_abstract_review=state['reviews'].get('abstract',{})
    manual_abstract=prior_abstract_review.get('method')=='manual' and prior_abstract_review.get('basis_sha256')==component_basis(record,'abstract')
    if not manual_abstract and (a.get('status')!='found' or a.get('source_kind')=='database_indexing_abstract') and matched and identity_paths and not a.get('candidate_review',{}).get('status')=='rejected':
        source_texts=[x.get('abstract','').strip() for x in matched.get('abstracts',[])]
        candidates=a.get('raw_provider_artifacts',[]) or a.get('candidate_artifacts',[]) or (a.get('artifacts',[]) if a.get('source_kind')=='database_indexing_abstract' else [])
        if not candidates and any(source_texts):
            source=next(e for e in record['evidence'] if e['path']==identity_paths[-1])
            candidate=artifact(record['paper_id'],'saved-provider-abstract.txt','\n\n'.join(t for t in source_texts if t),source['url'],kind='provider-abstract-candidate')
            record['evidence'].append(candidate);candidates=[candidate];a['candidate_artifacts']=candidates
        for candidate in candidates:
            if not intact(candidate):continue
            text=(BASE/candidate['path']).read_text().strip()
            bound=text=='\n\n'.join(t for t in source_texts if t)
            issue=provider_text_issue(text)
            if bound and issue:
                for old in a.get('artifacts',[]):
                    if old['path'] not in {e['path'] for e in record['evidence']}:record['evidence'].append(dict(old,kind='provider-quality-review-candidate'))
                record['abstract']={'status':'unresolved','candidate_artifacts':candidates,'reason':issue,'quality_review_required':True}
                break
            # A field must contain a complete multi-sentence research summary.
            # Citations, explicit truncation and short ambiguous fields go to the worker.
            is_summary=len(text)>200 and len(re.findall(r'[.!?](?:\s|$)',text))>=2 and bool(re.search(r'[.!?]$',text))
            is_summary=is_summary and not any(x in text for x in ('[...]','…','...')) and not re.search(r'\bv\.\d+\s+n\.\d+|\bp\.\d+\s*[-–]\s*\d+',text)
            if is_summary and bound:
                selected=complete_provider_variant(source_texts)
                if selected is None:
                    record['abstract']={'status':'unresolved','candidate_artifacts':candidates,'reason':'Multiple distinct provider abstract variants require comparison; raw array and combined original preserved.'}
                    break
                parts=provider_parts(selected);body=artifact(record['paper_id'],'summon-abstract-body.txt',parts['body'],candidate['url']) if parts['highlights'] or selected!=text else candidate
                highlights=[]
                if parts['highlights']:
                    h=artifact(record['paper_id'],'summon-highlights.txt',parts['highlights'],candidate['url'],kind='provider-highlights');record['evidence'].append(h);highlights=[h]
                record['abstract']={'status':'found','artifacts':[body],'raw_provider_artifacts':candidates,'additional_highlights':highlights,'source_kind':'database_indexing_abstract','authorship':'unknown',
                    'provider':'Summon actual UI response','attribution':[x.get('attribution') for x in matched.get('abstracts',[])],
                    'source_quality':'Verbatim DB text representation; publisher mathematical typesetting has not been inferred or silently restored.',
                    'validation':'Complete multi-sentence research summary in bibliographically matched actual UI abstract field; separate bullet-highlight lines stored as additional information. Attribution does not establish authorship.'}
                review('abstract',record['abstract']['validation'],identity_paths+[candidate['path'],body['path']]);break
    a=record['abstract']
    if a.get('status')=='found' and a.get('extraction_quality') in {'source_region_verified','visually_corrected'}:
        arts=a.get('artifacts',[])
        previous=[x for x in external if x.get('review_status')=='verified' and x.get('artifact',{}).get('sha256') in {v.get('sha256') for v in arts}]
        if arts and all(intact(ar) for ar in arts) and previous:
            reason='Reuse prior explicit visual boundary review bound to the unchanged actual artifact SHA256: '+previous[0].get('review_note','')
            review('abstract',reason,[x['path'] for x in arts])
        visual=[e for e in record.get('evidence',[]) if 'visual-verification' in e.get('kind','')]
        raw=a.get('raw_ocr_artifacts',[])
        prior_note=a.get('transcription_note') or (a.get('source_kind') if re.search(r'checked|transcribed|inspected',a.get('source_kind',''),re.I) else None)
        if a.get('extraction_quality')=='visually_corrected' and prior_note and arts and raw and visual and all(intact(ar) for ar in arts+raw+visual) and state['reviews'].get('fulltext',{}).get('basis_sha256')==component_basis(record,'fulltext'):
            try:
                for e in visual:
                    im=pymupdf.Pixmap(str(BASE/e['path']))
                    if not im.width or not im.height:raise ValueError('Empty visual evidence')
                reason='Reuse documented prior manual transcription, with unchanged corrected text, raw OCR and actual source-image evidence, and independently checked target original. '+prior_note
                review('abstract',reason,[e['path'] for e in arts+visual]+[e['path'] for e in record['fulltext']['artifacts']])
            except (OSError,ValueError):pass
    scope_paths=restricted_scope_evidence(record,paper)
    if scope_paths and state['reviews'].get('identity',{}).get('basis_sha256')==component_basis(record,'identity'):
        reason='All preserved ho=f query result counts are complete and include a bibliographically matched target; every input and observed normal source was attempted. Individual captured source pages, including an institutional route, display persistent CPE content-provision errors or explicit access/security notices. CPE does not establish a subscription denial; its cause is unconfirmed. No unresolved acquired PDF or unvisited-link flag exists.'
        review('fulltext',reason,scope_paths);state['reviews']['fulltext']['scope_complete']=True
        if record['abstract']['status']=='unresolved' and matched and not matched.get('abstracts') and not record['abstract'].get('candidate_artifacts'):
            record['abstract']={'status':'unavailable','reason':'Matched complete DB result provides no abstract; actually visited target publisher/institutional routes prevent retrieval of the original, so an embedded abstract cannot be checked and its existence remains unconfirmed. Provider failure and explicit access notices are distinguished in the source evidence.'}
            review('abstract',record['abstract']['reason']+' '+reason,scope_paths);state['reviews']['abstract']['scope_complete']=True
        if all(state['reviews'].get(c,{}).get('basis_sha256')==component_basis(record,c) for c in ('identity','abstract','fulltext')):
            for task in state['tasks']:
                if not task['key'].startswith('legacy:'):task.update(status='done',reason=reason,evidence_paths=scope_paths)
    if all(record[c].get('status')=='found' and state['reviews'].get(c,{}).get('basis_sha256')==component_basis(record,c) for c in ('abstract','fulltext')) and state['reviews'].get('identity',{}).get('basis_sha256')==component_basis(record,'identity'):
        paths=[x['path'] for c in ('abstract','fulltext') for x in record[c]['artifacts']]
        for task in state['tasks']:
            if task['status'] in {'pending','retry','needs_review'}:
                task.update(status='not_needed',reason='Target abstract and original fulltext both verified and preserved; additional acquisition candidates cannot improve the missing-component count.',evidence_paths=paths)

def native_mode(key):
    return key in {'sciencedirect-institution-native','sciencedirect-html'},key=='sciencedirect-html'

def fresh_source_page(context,page):
    page.close()
    return context.new_page()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);ap.add_argument('--offline',action='store_true');ap.add_argument('--reassess',action='store_true');ap.add_argument('--only',action='append');ap.add_argument('--engine',choices=['chromium','firefox'],default='chromium');args=ap.parse_args()
    started=time.time();run=WORK/'runs'/time.strftime('%Y%m%d-%H%M%S');run.mkdir(parents=True,exist_ok=True)
    manifest={'started_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'pid':os.getpid(),'argv':sys.argv,'code_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in list(WORK.glob('*.py'))+[WORK.parent/'work_queue.py',WORK.parent/'check_recovery.py']}}
    save_json(run/'manifest.json',manifest)
    a=json.loads((WORK/'assignment.json').read_text());papers={p['paper_id']:p for p in map(json.loads,(BASE/a['members_path']).read_text().splitlines())};extras=external_items()
    queue=build_queue(WORK/'assignment.json');save_json(WORK/'work-queue.json',queue)
    entries=[{'paper_id':pid} for pid in papers] if args.reassess else queue['entries']
    selected=[e for e in entries if not args.only or e['paper_id'] in args.only]
    if args.limit:selected=selected[:args.limit]
    metrics={'papers':0,'saved_evidence_reused':0,'searches':0,'source_visits':0,'downloads':0,'review_waiting':0,'errors':[]}
    browser=context=page=pw=None;gateway_proof=None
    try:
        for entry in selected:
            pid=entry['paper_id'];paper=papers[pid];path=WORK/'results'/f'{pid}.json';r=json.loads(path.read_text())
            if r.get('work_state',{}).get('version')!=VERSION:
                r['work_state']={'version':VERSION,'tasks':inventory(r,paper,[x for x in extras if x['paper_id']==pid]),'reviews':{}}
                metrics['saved_evidence_reused']+=len(r.get('evidence',[]))
            refresh_inventory(r,paper,[x for x in extras if x['paper_id']==pid])
            review_saved(r,paper,[x for x in extras if x['paper_id']==pid])
            for task in r['work_state']['tasks']:
                if args.offline or task['status'] not in {'pending','retry'} or task['kind'] not in {'search','source'}:continue
                try:
                    if context is None:
                        from playwright.sync_api import sync_playwright
                        pw=sync_playwright().start();launch={'headless':True}
                        if args.engine=='chromium':launch['channel']='chrome'
                        browser=browser_type(pw,args.engine).launch(**launch);context=browser.new_context(storage_state=a['browser_state']);page=context.new_page()
                    before=len(r['attempts']);tick=time.time()
                    if task['key'] in {'sciencedirect-native','sciencedirect-institution-native','sciencedirect-html'}:
                        institutional,html_only=native_mode(task['key'])
                        if institutional and gateway_proof is None:
                            observed=retry_step(lambda:science_direct.institution_gateway(context))
                            gateway_proof=artifact('service-probes','native-institution-gateway.json',json.dumps(observed,ensure_ascii=False,indent=2),observed['url'],'application/json','actual-institution-gateway')
                        if institutional and gateway_proof['path'] not in {e['path'] for e in r['evidence']}:r['evidence'].append(gateway_proof)
                        page=fresh_source_page(context,page)
                        save_json(path,r);r=retry_step(lambda:science_direct.collect(context,page,paper,institutional=institutional,source_target=task['target'],html_only=html_only))
                    elif task['key'].startswith('summon_query:'):
                        if urlsplit(page.url).hostname!='knu.summon.serialssolutions.com':page.goto(summon_collect.SUMMON);summon_collect.ensure_scope(page)
                        save_json(path,r);r=retry_step(lambda:summon_collect.one(context,page,paper,terms_override=[task['target']],search_only=True))
                    elif task['key']=='springer':
                        save_json(path,r);r=retry_step(lambda:book_collect.collect(context,page,paper))
                    elif task['key']=='acm':
                        save_json(path,r);r=retry_step(lambda:acm_collect.collect(context,page,paper))
                    elif task['kind']=='search':
                        if urlsplit(page.url).hostname!='knu.summon.serialssolutions.com':page.goto(summon_collect.SUMMON);summon_collect.ensure_scope(page)
                        save_json(path,r);r=retry_step(lambda:summon_collect.one(context,page,paper))
                    else:
                        summon_collect.publisher(context,r,paper,task['target'],'resume')
                    current=next(t for t in r['work_state']['tasks'] if t['key']==task['key'])
                    native_outcome=r.get('native_source_outcome',{})
                    ui_retry=task['key'].startswith('sciencedirect-') and isinstance(native_outcome,dict) and native_outcome.get('retryable_ui')
                    current.update(status='retry' if ui_retry else 'needs_review',reason=native_outcome.get('reason') if ui_retry else 'Actual UI step completed; assess preserved scope and content',elapsed_seconds=time.time()-tick)
                    for key,value in count_actions(r['attempts'][before:]).items():metrics[key]+=value
                except Exception as e:
                    task.update(status='retry',reason='Retryable UI error: '+type(e).__name__)
                    metrics['errors'].append({'paper_id':pid,'task':task['key'],'error':type(e).__name__})
                save_json(path,r)
            refresh_inventory(r,paper,[x for x in extras if x['paper_id']==pid])
            save_json(path,r);metrics['papers']+=1;metrics['last_paper_id']=pid
            metrics['review_waiting']+=sum(t['status']=='needs_review' for t in r['work_state']['tasks'])
            save_json(run/'metrics.json',dict(metrics,elapsed_seconds=time.time()-started))
            print(json.dumps({'paper_id':pid,'pending':len(pending_work(r))}),flush=True)
    finally:
        if browser:browser.close()
        if pw:pw.stop()
        save_json(WORK/'work-queue.json',build_queue(WORK/'assignment.json'))
        save_json(run/'metrics.json',dict(metrics,elapsed_seconds=time.time()-started))
        report=finish_run(run)
        metrics['complete']=report['complete'];metrics['check_passed']=report['passed']
        save_json(run/'metrics.json',dict(metrics,elapsed_seconds=time.time()-started))
    print(json.dumps(metrics))

if __name__=='__main__':main()
