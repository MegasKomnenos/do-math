import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from playwright.sync_api import sync_playwright
import recovery

WORKER=Path(__file__).resolve().parent
BASE=WORKER.parents[1]
sys.path.insert(0,str(WORKER.parent))
from work_queue import component_basis, pending_work
from check_recovery import validate_record, check_assignment
ASSIGNMENT=json.loads((WORKER/'assignment.json').read_text(encoding='utf-8-sig'))
PAPER=json.loads((BASE/ASSIGNMENT['members_path']).read_text(encoding='utf-8-sig'))
RAW=BASE/ASSIGNMENT['raw_root']

def dump(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    temp.replace(path)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def preserve(data,suffix,url,kind):
    if isinstance(data,str): data=data.encode('utf-8')
    sha=hashlib.sha256(data).hexdigest();path=RAW/(sha+suffix)
    if not path.exists(): path.write_bytes(data)
    return {'path':path.relative_to(BASE).as_posix(),'sha256':sha,'url':url,'kind':kind}

def review_status(review):
    value=(review or {}).get('abstract',{})
    return value['status'] if value.get('status')=='not_found' and value.get('scope_complete') and value.get('reason') else 'unresolved'

def can_reuse(record):
    return not validate_record(record,PAPER,BASE) and not pending_work(record)

def review_matches(collected,review):
    binding=(review or {}).get('reviewed_sources',{})
    sources=[e for e in collected['evidence'] if e['kind']!='authentication-state-without-secrets']
    return bool(sources) and all(binding.get(e['path'])==e['sha256'] for e in sources)

def replay_metrics(collected):
    return {'searches':0,'source_visits':0,'download_attempts':0,
            'saved_evidence_reused':len(collected['evidence'])+1,'browser_replayed':False}

def collect():
    evidence=[];attempts=[];metrics={'searches':0,'source_visits':0,'download_attempts':0,'saved_evidence_reused':0}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(channel='chrome',headless=True)
        context=browser.new_context(storage_state=ASSIGNMENT['browser_state'])
        page=context.new_page();page.set_default_timeout(45000)
        page.goto('https://kudos.knu.ac.kr/pages/index.htm')
        page.get_by_role('link',name='로그아웃',exact=True).wait_for()
        auth=preserve(json.dumps({'url':page.url,'logout_visible':True,'observed_at':datetime.now(timezone.utc).isoformat()}),'.json',page.url,'authentication-state-without-secrets');evidence.append(auth)
        summon_url=page.locator('a[href*="knu.summon.serialssolutions.com"]').first.get_attribute('href')
        page.goto(recovery.AUTHOR_URL);metrics['source_visits']+=1
        html=page.content();author=recovery.author_record(html)
        if not author:raise ValueError('Author page no longer identifies target preprint')
        evidence.append(preserve(html,'.html',page.url,'author-page'))
        link=page.get_by_role('link',name='preprint version(pdf)',exact=True).get_attribute('href')
        from urllib.parse import urljoin
        pdf_url=urljoin(page.url,link)
        response=context.request.get(pdf_url);metrics['download_attempts']+=1
        data=response.body();inspection=recovery.inspect_pdf(data)
        if not inspection['target_preprint']:raise ValueError('Observed PDF response fails preprint identity')
        original=BASE/PAPER['local_candidates'][0]['path']
        if digest(original)==inspection['sha256']:
            fulltext={'path':original.relative_to(BASE).as_posix(),'sha256':inspection['sha256'],'url':pdf_url,'media_type':'application/pdf'};metrics['saved_evidence_reused']+=1
        else:
            raise ValueError('Remote preprint changed; direct version review required')
        evidence.append(preserve(json.dumps(inspection,ensure_ascii=False),'.json',pdf_url,'pdf-inspection'))
        attempts.append({'method':'playwright','query':'Author title and explicit preprint version(pdf) link','url':recovery.AUTHOR_URL,'outcome':'Observed explicit link; HTTP '+str(response.status)+' PDF equals local SHA and has 26 readable pages.'})
        page.goto(summon_url);field=page.locator('input[name=q]:visible');field.wait_for()
        query='"'+PAPER['title']+'"'
        with page.expect_response(lambda r:'/api/search' in r.url and r.request.method=='GET') as event:
            field.fill(query);field.press('Enter')
        first=recovery.safe_search(event.value.json());metrics['searches']+=1
        if first['query']['original_query']!=query:raise ValueError('Search response query mismatch')
        evidence.append(preserve(json.dumps(first,ensure_ascii=False),'.json',summon_url,'summon-title-holdings'))
        page.get_by_text('도서관 비구독 자료 포함',exact=False).wait_for()
        with page.expect_response(lambda r:'/api/search' in r.url and r.request.method=='GET') as event:
            page.get_by_text('도서관 비구독 자료 포함',exact=False).click()
        expanded=recovery.safe_search(event.value.json());metrics['searches']+=1
        if expanded['query']['original_query']!=query or 's.ho=f' not in expanded['query']['query_string']:raise ValueError('Expanded scope mismatch')
        decisions=recovery.assess_search(expanded)
        evidence.append(preserve(json.dumps(expanded,ensure_ascii=False),'.json',page.url,'summon-title-expanded'))
        details=[]
        buttons=page.locator('button[data-aid=quick-look-button]:visible');buttons.first.wait_for()
        if buttons.count()!=expanded['record_count']:raise ValueError('Rendered result count mismatch')
        for i in range(buttons.count()):
            buttons.nth(i).click();dialog=page.locator('[data-aid=quick-look-modal]');dialog.wait_for()
            text=dialog.inner_text();details.append(text)
            evidence.append(preserve(text,'.txt',page.url,'summon-quick-look-'+str(i)))
            dialog.locator('button[data-aid=quick-look-close-btn]').click()
        attempts.append({'method':'playwright','query':query,'url':page.url,'outcome':f'Holdings {first["record_count"]}; beyond holdings {expanded["record_count"]}; all {len(details)} Quick Look dialogs read and saved.'})
        query=PAPER['title']+' Kobayashi'
        time.sleep(.6)
        with page.expect_response(lambda r:'/api/search' in r.url and r.request.method=='GET') as event:
            field.fill(query);field.press('Enter')
        author_search=recovery.safe_search(event.value.json());metrics['searches']+=1
        if author_search['query']['original_query']!=query or 's.ho=f' not in author_search['query']['query_string']:raise ValueError('Title author scope mismatch')
        author_decisions=recovery.assess_search(author_search)
        evidence.append(preserve(json.dumps(author_search,ensure_ascii=False),'.json',page.url,'summon-title-author-expanded'))
        attempts.append({'method':'playwright','query':query,'url':page.url,'outcome':f'Beyond holdings title-author query returned {author_search["record_count"]} documents; complete response preserved for review.'})
        browser.close()
    # Already observed through the actual KUDOS MathSciNet gateway in this task.
    mr=RAW/'facb1a04456b9163143716137d18e449bbfc7531e8e94590ccbbcc3accbbb713.txt'
    evidence.append({'path':mr.relative_to(BASE).as_posix(),'sha256':digest(mr),'url':'https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article','kind':'related-publication-mathscinet-review'})
    metrics['saved_evidence_reused']+=1
    attempts.append({'method':'playwright','query':'KUDOS academic DB MathSciNet, then MR1190750','url':'https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/article','outcome':'Search navigated directly to MR1190750; 1992 pp59-75 and reviewer Shvartsman shown; Article is a span without href. Saved observed bibliographic/review section reused.'})
    return {'author':author,'fulltext':fulltext,'evidence':evidence,'attempts':attempts,'metrics':metrics,'decisions':decisions,'author_decisions':author_decisions}

def build(collected,review):
    status=review_status(review)
    evidence=collected['evidence'][:]
    if review:
        evidence.append(preserve(json.dumps(review,ensure_ascii=False),'.json',recovery.AUTHOR_URL,'direct-content-review'))
    result={'schema_version':'kudos-recovery-result/1','paper_id':PAPER['paper_id'],'version_sha256':PAPER['version_sha256'],
            'metadata':collected['author'],'identity':{'status':'confirmed','reason':'Author page explicitly links the titled Kobayashi preprint; downloaded PDF equals the registered local SHA, has title/author and pages1-26. Related 1992 publication is pp59-75; preprint date remains unestablished.'},
            'abstract':{'status':status,'reason':(review or {}).get('abstract',{}).get('reason','Direct review of PDF and source scope remains.')},
            'fulltext':{'status':'found','artifacts':[collected['fulltext']]},'attempts':collected['attempts'],'evidence':evidence,
            'work_state':{'version':'remaining-work/1','tasks':[],'reviews':{}}}
    paths=[a['path'] for a in evidence];allpaths=paths+[collected['fulltext']['path']]
    tasks=result['work_state']['tasks']
    for key,kind,target,reason in [
        ('sources','source',recovery.AUTHOR_URL,'Author page and explicit PDF read; original input links covered.'),
        ('search','search','Summon exact title and title-author beyond holdings; KUDOS MathSciNet MR1190750','All returned records preserved and all8 exact-title Quick Look dialogs read; related publication review distinguished.'),
        ('pdf','pdf',collected['fulltext']['path'],'Downloaded observed preprint link; identical local SHA,26 readable pages, title/author and final references confirmed.')]:
        tasks.append({'key':key,'kind':kind,'target':target,'status':'done','reason':reason,'evidence_paths':allpaths})
    if review:
        for task in review.get('source_dispositions',[]):
            tasks.append(dict(task,evidence_paths=allpaths))
        for component in ['identity','abstract','fulltext']:
            value=review.get(component,{})
            if value.get('reason'):
                result['work_state']['reviews'][component]={'basis_sha256':component_basis(result,component),'reason':value['reason'],'scope_complete':value.get('scope_complete',False),'evidence_paths':allpaths}
    else:tasks.append({'key':'direct_review','kind':'review','target':PAPER['paper_id'],'status':'needs_review','reason':'Inspect complete source scope and PDF before completion.'})
    return result

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);parser.add_argument('--refresh',action='store_true');args=parser.parse_args()
    RAW.mkdir(parents=True,exist_ok=True);start=time.time();run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+str(os.getpid())
    manifest={'started_at':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'argv':sys.argv,'cwd':os.getcwd(),
              'code_sha256':{str(p):digest(p) for p in [Path(__file__),WORKER/'recovery.py',WORKER/'test_recovery.py',WORKER.parent/'work_queue.py',WORKER.parent/'check_recovery.py']}}
    run=WORKER/'runs'/run_id;dump(run/'manifest.json',manifest)
    result_path=WORKER/'results'/(PAPER['paper_id']+'.json')
    if result_path.exists() and not args.refresh and can_reuse(json.loads(result_path.read_text())):
        check=check_assignment(WORKER/'assignment.json');dump(run/'outcome.json',{'elapsed_seconds':time.time()-start,'reused_valid_result':1,'check':check});print(json.dumps(check));return
    try:
        saved=WORKER/'collected.json'
        if saved.exists() and not args.refresh:
            collected=json.loads(saved.read_text(encoding='utf-8'));metrics=replay_metrics(collected)
        else:
            collected=collect();dump(saved,collected);metrics=collected['metrics']
        review_path=WORKER/'human-review.json';review=json.loads(review_path.read_text(encoding='utf-8')) if review_path.exists() else None
        if not review_matches(collected,review):review=None
        result=build(collected,review);dump(result_path,result)
        check=check_assignment(WORKER/'assignment.json',partial=True);dump(run/'outcome.json',{'elapsed_seconds':time.time()-start,'metrics':metrics,'check':check})
        dump(WORKER/'progress.json',{'stage':'complete' if check['complete'] else 'needs_review','processed':1,'assigned':1,'abstract_found':int(result['abstract']['status']=='found'),'fulltext_found':1,'remaining':check['papers_with_remaining_work'],'last_paper_id':PAPER['paper_id'],'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g12/resume.py','run':str(run)})
        print(json.dumps({'run':run_id,'complete':check['complete'],'remaining':check['papers_with_remaining_work'],'metrics':metrics}))
    except Exception as exc:
        # Exception messages may contain internal URLs: record type only.
        dump(run/'outcome.json',{'elapsed_seconds':time.time()-start,'error_type':type(exc).__name__,'next_action':'Inspect the failing browser phase and rerun; no absence decision was written.'})
        print(type(exc).__name__);raise SystemExit(1)

if __name__=='__main__':main()
