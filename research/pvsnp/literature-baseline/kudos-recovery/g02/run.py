"""Sequential UI recovery; all unresolved components remain explicit for subsequent repair."""
import argparse, hashlib, json, re, time, uuid, sys
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright
from recovery import doi_key, words, barrier, review_kind, summon_abstract, zero_results, source_links, mathscinet_section
from response_recovery import search_ui, select_documents, selected_payload, FIELDS, primary_identifier, batch_query, batch_truncated
BASE=Path(__file__).resolve().parents[2]
ROOT=Path(__file__).resolve().parent
ASSIGN=json.loads((ROOT/'assignment.json').read_text(encoding='utf-8-sig'))
RAW=BASE/ASSIGN['raw_root']
_STATUS_ROWS=None
OWNED_IDS=None
SHARD_INDEX=0
SHARD_COUNT=1
PROGRESS_PATH=ROOT/'progress.json'

def configure_scope(papers,index,count):
 global OWNED_IDS,SHARD_INDEX,SHARD_COUNT,PROGRESS_PATH,_STATUS_ROWS
 OWNED_IDS={p['paper_id'] for p in papers};SHARD_INDEX=index;SHARD_COUNT=count;_STATUS_ROWS=None
 PROGRESS_PATH=ROOT/('progress.json' if count==1 else f'progress-shard-{index}-of-{count}.json')

def status_tuple(record):
 if str(Path(__file__).resolve().parent.parent) not in sys.path:sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
 from work_queue import pending_work
 return tuple(record.get(k,{}).get('status') for k in ('identity','abstract','fulltext'))+(bool(pending_work(record)),)

def store_json(path,value):
 if path.parent==ROOT/'results' and OWNED_IDS is not None and path.stem not in OWNED_IDS:raise ValueError('Result belongs to another fixed shard.')
 path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix('.tmp'); temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8'); temp.replace(path)
 if _STATUS_ROWS is not None and path.parent==ROOT/'results':_STATUS_ROWS[path.stem]=status_tuple(value)

def capture(pid,name,text,url,kind='detail-page'):
 path=RAW/pid/name; path.parent.mkdir(parents=True,exist_ok=True)
 data=text.encode('utf-8')
 if not path.exists() or path.read_bytes()!=data:path=path.with_name(path.stem+'-'+hashlib.sha256(data).hexdigest()[:16]+path.suffix)
 if path.exists() and path.read_bytes()!=data:raise ValueError('Content-addressed evidence collision.')
 if not path.exists():
  temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');temporary.write_bytes(data);temporary.replace(path)
 return {'path':path.relative_to(BASE).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'url':url,'kind':kind,'media_type':'text/plain'}

def progress(stage,pid=None):
 global _STATUS_ROWS
 if _STATUS_ROWS is None:
  _STATUS_ROWS={f.stem:status_tuple(json.loads(f.read_text(encoding='utf-8'))) for f in (ROOT/'results').glob('*.json') if OWNED_IDS is None or f.stem in OWNED_IDS}
 rs=list(_STATUS_ROWS.values())
 assigned=len(OWNED_IDS) if OWNED_IDS is not None else ASSIGN['count'];unprocessed=assigned-len(rs);pending=sum(r[3] for r in rs)
 store_json(ROOT/('progress.json' if SHARD_COUNT==1 else f'progress-shard-{SHARD_INDEX}-of-{SHARD_COUNT}.json'),{'stage':stage,'shard_index':SHARD_INDEX,'shard_count':SHARD_COUNT,'assigned':assigned,'processed':len(rs),'abstract_found':sum(r[1]=='found' for r in rs),'fulltext_found':sum(r[2]=='found' for r in rs),'unresolved':sum('unresolved' in r for r in rs),'remaining':unprocessed,'unprocessed':unprocessed,'saved_with_remaining_work':pending,'total_remaining_papers':pending+unprocessed,'last_paper_id':pid,'updated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g02/resume.py'})

def search_summon(page,query):
 if page.locator('[role=dialog]:visible').count():
  close=page.get_by_role('button',name='닫기',exact=True)
  if close.count():
   close.click(); close.wait_for(state='hidden')
 box=page.locator('input[id^=searchBox_]:visible').first
 old=page.url
 box.fill(query); box.press('Enter')
 page.wait_for_timeout(1300)
 page.wait_for_function("() => !document.querySelector('[data-aid=search-results-loading]')",timeout=15000)
 page.wait_for_timeout(900)
 return page.locator('body').inner_text()

def modal_matches(p,body):
 lines=[v.strip() for v in body.splitlines() if v.strip()]
 marker=next((i for i,v in enumerate(lines) if re.fullmatch(r'\d+ of [\d,]+ results',v)),None)
 if marker is None or len(lines)<=marker+2: return False
 actual_title=words(lines[marker+1]); expected_title=words(p['title'])
 # Summon may separate an article subtitle from the title, as in the first real positive.
 if not actual_title or not (actual_title==expected_title or expected_title.startswith(actual_title+' ') or actual_title.startswith(expected_title+' ')): return False
 author_line=words(lines[marker+2])
 authors=p.get('authors',[])
 if not authors: return False
 for author in authors:
  surname=words(author.split(',')[0] if ',' in author else author.split()[0])
  if not surname or not re.search(r'(?<!\w)'+re.escape(surname)+r'(?!\w)',author_line): return False
 if not p.get('year') or not re.search(r'발행일자\s*[^\n]*?'+str(p['year'])+r'\b',body): return False
 ds=p.get('identifiers',{}).get('doi',[])
 if ds:
  observed={doi_key(v) for v in re.findall(r'10\.\d{4,9}/[^\s]+',body)}
  return any(doi_key(d) in observed for d in ds)
 isbn=p.get('identifiers',{}).get('isbn',[])
 values=re.findall(r'(?:ISBN|EISBN)\s*\n([^\n]+)',body)
 ids={re.sub('[^0-9Xx]','',v) for line in values for v in line.split(',')}
 return bool(isbn and any(re.sub('[^0-9Xx]','',v) in ids for v in isbn))

DONE_UI={'mathscinet-and-summon-ui-expanded-identity-v2','summon-ui-response-v1'}

def iter_batches(page,papers,limit=None):
 pending=[]
 for paper in papers:
  path=ROOT/'results'/(paper['paper_id']+'.json')
  if path.exists() and not __import__('recovery').needs_work(json.loads(path.read_text(encoding='utf-8'))):continue
  pending.append(paper)
 if limit is not None:pending=pending[:limit]
 def search_group(group):
  query=batch_query(group)
  progress('searching-ui-identifier-batch',group[0]['paper_id'])
  try:payload=search_ui(page,query)
  except Exception as exc:
   store_json(ROOT/'blocker.json',{'kind':'repairable-batch-ui-error','paper_ids':[p['paper_id'] for p in group],'query':query,'exception_type':type(exc).__name__,'detail':re.sub(r'https?://\S+','[URL omitted]',str(exc))[:2500],'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g02/run.py'})
   progress('needs-batch-ui-repair',group[0]['paper_id']);print(json.dumps({'error':type(exc).__name__,'stage':'batch-ui-search'}),flush=True)
   for paper in group:yield paper,None,None,None
   return
  artifact=capture('_batches',hashlib.sha256(query.encode()).hexdigest()[:16]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');artifact['media_type']='application/json'
  if batch_truncated(payload) and len(group)>1:
   middle=len(group)//2
   yield from search_group(group[:middle]);yield from search_group(group[middle:]);return
  for paper in group:yield paper,payload,query,artifact
 group=[]
 for paper in pending:
  if primary_identifier(paper):
   group.append(paper)
   if len(group)==6:yield from search_group(group);group=[]
  else:
   if group:yield from search_group(group);group=[]
   yield paper,None,None,None
 if group:yield from search_group(group)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int); args=ap.parse_args()
 papers=[json.loads(l) for l in (BASE/ASSIGN['members_path']).read_text(encoding='utf-8-sig').splitlines() if l.strip()]
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  context=browser.new_context(storage_state=ASSIGN['browser_state'])
  context.set_default_timeout(15000)
  kp=context.new_page(); kp.goto('https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542'); kp.locator('#search_order').fill('MathSciNet'); kp.locator('#search_order').press('Enter')
  with context.expect_page() as opened: kp.get_by_text('바로가기',exact=True).click()
  mp=opened.value; mp.wait_for_url('**/publications-search')
  sp=context.new_page(); sp.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q='); sp.locator('input[id^=searchBox_]:visible').first.wait_for(); sp.locator('#ho0').focus(); sp.locator('#ho0').press('Space'); sp.wait_for_function("document.querySelector('#ho0').checked"); sp.wait_for_timeout(1500)
  count=0
  for p,cached_response,cached_query,cached_artifact in iter_batches(sp,papers,args.limit):
   pid=p['paper_id']; rp=ROOT/'results'/f'{pid}.json'
   prior=json.loads(rp.read_text(encoding='utf-8')) if rp.exists() else None
   if prior and prior.get('collection_stage') in ('mathscinet-and-summon-ui-expanded-identity-v2','summon-ui-response-v1'): continue
   if args.limit is not None and count>=args.limit: break
   progress('collecting-mathscinet-and-summon',pid)
   r=prior or {'schema_version':'kudos-recovery-result/1','paper_id':pid,'version_sha256':p['version_sha256'],'identity':{'status':'unresolved','reason':'Corresponding source identity has not yet been established.'},'metadata':{k:p.get(k) for k in ['title','authors','year','identifiers','publication']},'abstract':{'status':'unresolved','reason':'Abstract recovery pending.'},'fulltext':{'status':'unresolved','reason':'Normal fulltext provider paths remain to be investigated.'},'attempts':[],'evidence':[]}
   try:
    mr=next((s['record_id'] for s in p['source_records'] if s['record_id'].startswith('MR')),None)
    queries=list(p.get('identifiers',{}).get('doi',[]))[:1]
    queries+=list(p.get('identifiers',{}).get('isbn',[]))[:1]
    surname=(p['authors'][0].split(',')[0] if ',' in p['authors'][0] else p['authors'][0].split()[0]) if p.get('authors') else ''
    queries.append(p['title']+' '+surname+' '+str(p.get('year') or ''))
    matched=False
    for qi,q in enumerate(dict.fromkeys(queries)):
     if qi==0 and cached_response is not None:
      payload=cached_response;q=cached_query;su=cached_artifact['url'];art=cached_artifact
     else:
      payload=search_ui(sp,q);su=sp.url
      art=capture(pid,f'summon-response-{qi}.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),su,'observed-ui-search-response');art['media_type']='application/json'
     r['evidence'].append(art)
     if batch_truncated(payload):r.setdefault('unvisited_search_pages',[]).append({'query':q,'url':su,'record_count':payload['record_count'],'received':len(payload['documents']),'reason':'Single-identifier first UI response is incomplete; other narrower queries or remaining UI pages require review if this response does not resolve the requested document.'})
     rows=select_documents(p,payload,q)
     r['attempts'].append({'method':'playwright','query':q,'url':su,'outcome':f"UI search-input fill and form submit-button click produced search response for exact query with s.ho=f; {payload['record_count']} results; {len(rows)} documents matched title, authors, year, type, identifiers and available volume/page fields."})
     if not rows:continue
     d=max(rows,key=lambda d:sum(len(a.get('abstract','')) for a in d.get('abstracts',[])))
     matched=True; r.pop('needs_mathscinet_revisit',None)
     r['identity']={'status':'confirmed','reason':'Actual Summon UI response matched assigned title (allowing separated subtitle), all author surnames, publication year, document type, DOI/ISBN and available volume/issue/page-range fields. Selected bibliographic values and full search response fields preserved.'}
     r['observed_bibliography']={k:d[k] for k in FIELDS if k in d and k not in ('abstracts','link','fulltext_link','link_to_html')}
     r['observed_source_links']=[{'text':key,'url':d[key]} for key in ('link','fulltext_link','link_to_html') if isinstance(d.get(key),str) and d[key].startswith(('http://','https://'))]
     abstracts=[a for a in d.get('abstracts',[]) if a.get('abstract','').strip()]
     if abstracts:
      ab=max(abstracts,key=lambda a:len(a['abstract']))
      if p['record_type'] in ('article','incollection','inproceedings'):
       r['abstract']={'status':'found','artifacts':[capture(pid,'abstract.txt',ab['abstract'],su,'summon-response-abstract')],'source_content_type':d.get('content_type'),'attribution':ab.get('attribution','')}
      else:r.setdefault('additional_content',[]).append({'kind':'summon-book-description','artifact':capture(pid,'summon-description.txt',ab['abstract'],su,'summon-response-description'),'attribution':ab.get('attribution','')})
     break
    if mr and not matched and not (prior and prior.get('collection_stage')):
     mp.goto('https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/publications-search')
     mp.locator('#searchTextInput').fill(mr); mp.locator('#searchTextInput').press('Enter'); mp.wait_for_url('**/article?mr=*'); mp.locator('main').wait_for(); mp.wait_for_function("expected=>{const text=document.querySelector('main')?.innerText||'';return text.includes(expected)&&text.includes('Classifications')}",arg='MR'+str(int(mr[2:])).zfill(7))
     fullbody=mp.locator('main').inner_text(); section=mathscinet_section(mp,mr); body=section.inner_text(); url=mp.url; r.pop('needs_mathscinet_revisit',None)
     whole=capture(pid,'mathscinet.txt',fullbody,url);r['evidence'].append(whole)
     r['evidence'].append(capture(pid,'mathscinet-bibliography.txt',body,url,'mr-scoped-bibliography'))
     link=section.get_by_role('link',name='Article',exact=True)
     article=link.get_attribute('href') if link.count() else None
     r['provider_link']=article
     title_match=words(p['title']) in words(body)
     if mr[2:].lstrip('0')==re.search(r'mr=(\d+)',url).group(1).lstrip('0') and title_match and str(p['year']) in body:
      r['identity']={'status':'confirmed','reason':f'MathSciNet {mr}, normalized title and publication year match assigned source record. Complete bibliographic detail preserved for version inspection.'}
     r.setdefault('additional_content',[]).append({'kind':'shared-review-page' if mp.locator('div.article').count()>1 else review_kind(fullbody),'artifact':whole})
     r['attempts'].append({'method':'playwright','query':mr,'url':url,'outcome':'Searched MR identifier using UI and opened corresponding detail; preserved full displayed bibliographic/review text.'})
    if r['abstract']['status']!='found': r['abstract']={'status':'unresolved','reason':'MathSciNet and Summon were searched; no authenticated corresponding article abstract secured in these views. Publisher and alternate source investigation remains.'}
    r['collection_stage']='summon-ui-response-v1'
    store_json(rp,r); count+=1; progress('collecting-mathscinet-and-summon',pid)
    print(json.dumps({'paper_id':pid,'processed_this_run':count,'abstract':r['abstract']['status']},ensure_ascii=False),flush=True)
   except Exception as exc:
    # Do not log exception URLs, which can carry authentication redirect parameters.
    r['last_error_type']=type(exc).__name__; r['last_error_message']=re.sub(r'https?://\S+','[URL omitted]',str(exc))[:2500]
    if r['evidence']: store_json(rp,r)
    store_json(ROOT/'blocker.json',{'kind':'repairable-collector-error','paper_id':pid,'exception_type':type(exc).__name__,'detail':re.sub(r'https?://\S+','[URL omitted]',str(exc))[:2500],'resume_command':'python research/pvsnp/literature-baseline/kudos-recovery/g02/run.py','note':'Inspect live UI and repair; this is not a corpus-wide access verdict.'})
    progress('needs-collector-repair',pid)
    print(json.dumps({'error':type(exc).__name__,'paper_id':pid,'detail':r['last_error_message']}),flush=True)
    raise SystemExit(1)
  progress('ui-pass-ended')
  browser.close()
if __name__=='__main__': main()
