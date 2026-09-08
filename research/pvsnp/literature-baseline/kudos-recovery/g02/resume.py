"""Resume g02 from retained evidence and explicit remaining work."""
import argparse,hashlib,json,os,re,sys,time
from pathlib import Path
from urllib.parse import urlsplit,urljoin
import run
from run import BASE,ROOT,RAW,ASSIGN,store_json,capture
from response_recovery import search_ui,select_documents,selected_payload,document_matches
from abstract_kind import classify,database_abstract
from abstract_reclassify import valid_bytes
sys.path.insert(0,str(ROOT.parent))
from work_queue import pending_work,component_basis

def sha(data):return hashlib.sha256(data).hexdigest()

def new_result(p):
 return {'schema_version':'kudos-recovery-result/1','paper_id':p['paper_id'],'version_sha256':p['version_sha256'],'identity':{'status':'unresolved','reason':'Source identity still requires verification.'},'metadata':{k:p.get(k) for k in ('title','authors','year','identifiers','publication')},'abstract':{'status':'unresolved','reason':'Abstract sources remain to be assessed.'},'fulltext':{'status':'unresolved','reason':'Fulltext sources remain to be assessed.'},'attempts':[],'evidence':[]}

def task(r,kind,target,status='pending',reason='Required source scope remains to be examined.',evidence_paths=None,**extra):
 state=r.setdefault('work_state',{'version':'remaining-work/1','tasks':[],'reviews':{}})
 key=kind+':'+sha(target.encode())[:20]
 found=next((t for t in state['tasks'] if t['key']==key),None)
 if found:return found
 t={'key':key,'kind':kind,'target':target,'status':status,'reason':reason,**extra}
 if evidence_paths:t['evidence_paths']=evidence_paths
 state['tasks'].append(t);return t

def add_evidence(r,e):
 if not any(x['path']==e['path'] and x['sha256']==e['sha256'] for x in r['evidence']):r['evidence'].append(e)

def repair_empty_evidence(r):
 for e in list(r['evidence']):
  path=BASE/e['path']
  if e.get('kind')!='provider-page' or not path.exists() or path.stat().st_size:continue
  observation=capture(r['paper_id'],path.name+'.observation.json',json.dumps({'body_text_length':0,'original_empty_path':e['path'],'original_empty_sha256':e['sha256'],'outcome':'Empty rendered provider capture does not establish content or absence.'}),e['url'],'empty-page-observation');observation['media_type']='application/json'
  r.setdefault('superseded_capture_records',[]).append({'previous_reference':e,'status':'empty-capture-preserved-as-failed-observation','reason':'Empty bytes retained on disk; replace content evidence with explicit failed rendering observation.'})
  r['evidence'].remove(e);add_evidence(r,observation)
  for t in r.get('work_state',{}).get('tasks',[]):
   if e['path'] in t.get('evidence_paths',[]):t.update(status='retry',reason='Empty provider rendering must be revisited.',evidence_paths=[observation['path']])

def consume_response(p,r,payload,e,save=True):
 rows=select_documents(p,payload,payload['query']['original_query'])
 for d in rows:
  if not any(x.get('document')==d for x in r.setdefault('identity_candidates',[])):
   r['identity_candidates'].append({'document':d,'evidence_path':e['path']})
  for key in ('link','fulltext_link','link_to_html'):
   url=d.get(key)
   if isinstance(url,str) and url.startswith(('https://','http://')):task(r,'source',url)
  for a in d.get('abstracts') or []:
   text=a.get('abstract','').strip()
   if not text or classify(text)!='database_indexing_abstract':continue
   entry={'text':text,'evidence_path':e['path'],'provided_by':'Summon','attribution':a.get('attribution',''),'content_type':d.get('content_type'),'status':'needs_review'}
   if not any(x['text']==text for x in r.setdefault('abstract_candidates',[])):r['abstract_candidates'].append(entry)
 return rows

def inventory(p,r):
 repair_empty_evidence(r)
 state=r.setdefault('work_state',{'version':'remaining-work/1','tasks':[],'reviews':{}})
 identifiers=p.get('identifiers',{})
 queries=list(dict.fromkeys(identifiers.get('doi',[])+identifiers.get('isbn',[])))
 surname=p.get('authors',[''])[0].split(',')[0].split()[0] if p.get('authors') else ''
 queries.append(p['title']+' '+surname+' '+str(p.get('year') or ''))
 saved=[]
 for e in list(r.get('evidence',[])):
  if not e['path'].endswith('.json'):continue
  data=valid_bytes(e)
  if data is None:continue
  try:payload=json.loads(data)
  except (ValueError,UnicodeError):continue
  if 'documents' not in payload or 'query' not in payload:continue
  try:consume_response(p,r,payload,e)
  except ValueError:continue
  saved.append((payload,e))
 for q in dict.fromkeys(queries):
  evidence=next(((pl,e) for pl,e in saved if pl['query']['original_query']==q and int(pl['record_count'])<=len(pl['documents'])),None)
  if not evidence and q in identifiers.get('doi',[])+identifiers.get('isbn',[]):
   evidence=next(((pl,e) for pl,e in saved if json.dumps(q,ensure_ascii=False) in pl['query']['original_query'] and int(pl['record_count'])<=len(pl['documents'])),None)
  if evidence:task(r,'search',q,'done','Preserved complete observed UI response covers this query.',[evidence[1]['path']])
  else:task(r,'search',q)
 for s in p.get('source_records',[]):
  mr=s.get('record_id','')
  if not mr.startswith('MR'):continue
  evidence=next((e for e in r['evidence'] if 'mathscinet' in e['path'] and valid_bytes(e)),None)
  if evidence:
   task(r,'search',mr,'done','Preserved MathSciNet detail remains available for direct review.',[evidence['path']])
   from mr_fields import source_title
   from response_recovery import norm
   raw=valid_bytes(evidence).decode('utf-8-sig');actual=source_title(p,raw)
   if actual and norm(actual)!=norm(p['title']) and not norm(actual).startswith(norm(p['title'])+' ') and not norm(p['title']).startswith(norm(actual)+' '):
    task(r,'search','"'+actual+'" '+str(p.get('year') or ''),reason='Actual MR title differs from TeX/transliterated input; search the observed title and edition year.')
  else:task(r,'search',mr)
 links=list(p.get('source_urls',[]))+[r.get('provider_link')]+[v.get('url') for v in r.get('observed_source_links',[])]
 for link in links:
  if isinstance(link,str) and link.startswith(('http://','https://')):task(r,'source',link)
 for c in ('identity','abstract','fulltext'):
  if state.get('reviews',{}).get(c,{}).get('basis_sha256')!=component_basis(r,c):
   t=task(r,'review',c,'needs_review','Worker must inspect component evidence and record current semantic review.');t.update(status='needs_review',reason='Worker must inspect component evidence and record current semantic review.')
 return r

def record_review(r,component,reason,paths,scope_complete=False):
 value={'basis_sha256':component_basis(r,component),'reason':reason,'evidence_paths':list(dict.fromkeys(paths)),'rule_code_sha256':{name:sha((ROOT/name).read_bytes()) for name in ('response_recovery.py','abstract_kind.py','resume.py','pdf_review.py','source_kind.py','mr_fields.py')},'tests':['test_response.py','test_display_markup.py','test_abstract_kind.py','test_resume.py','test_live_responses.py','test_pdf_review.py','test_source_kind.py','test_mr_fields.py']}
 if scope_complete:value['scope_complete']=True
 r['work_state']['reviews'][component]=value
 for t in r['work_state']['tasks']:
  if t['kind']=='review' and t['target']==component:t.update(status='done',reason=reason,evidence_paths=value['evidence_paths'])

def adjudicate_saved(p,r):
 if r['abstract'].get('status')=='found':
  for artifact in r['abstract'].get('artifacts',[]):
   data=valid_bytes(artifact)
   if not data:continue
   try:text=data.decode('utf-8-sig')
   except UnicodeError:continue
   kind=classify(text)
   if kind!='database_indexing_abstract':
    r.setdefault('additional_content',[]).append({'kind':kind,'artifact':artifact,'previous_status':'found','withdrawal_reason':'Raw source preservation did not establish readable complete abstract content.'})
    r['abstract']={'status':'unresolved','reason':kind+' in stored abstract; compare another source or original region before confirming.'}
    r['work_state']['reviews'].pop('abstract',None)
    t=task(r,'review','abstract');t.update(status='needs_review',reason=r['abstract']['reason'])
    break
 from mr_review import inspect_mr
 for e in list(r['evidence']):
  if 'mathscinet' not in e['path'] or not e['path'].endswith('.txt'):continue
  data=valid_bytes(e)
  if not data:continue
  checked=inspect_mr(p,data.decode('utf-8-sig'))
  if not checked:continue
  if r['identity'].get('status')!='confirmed':r['identity']={'status':'confirmed','reason':checked['reason']}
  record_review(r,'identity',checked['reason'],[e['path']]);r['work_state']['reviews']['identity']['rule_code_sha256']['mr_review.py']=sha((ROOT/'mr_review.py').read_bytes());r['work_state']['reviews']['identity']['tests'].append('test_mr_review.py')
  if checked['abstract'] and r['abstract'].get('status')!='found':
   a=capture(p['paper_id'],'mathscinet-summary.txt',checked['abstract'],e['url'],'database-indexing-abstract');r['abstract']=database_abstract(checked['abstract'],a);r['abstract']['provided_by']='MathSciNet'
   record_review(r,'abstract','Corresponding single-MR detail explicitly supplies a complete quoted Summary; source excerpts and shared reviews are excluded by the tested boundary rule.',[e['path'],a['path']]);r['work_state']['reviews']['abstract']['rule_code_sha256']['mr_review.py']=sha((ROOT/'mr_review.py').read_bytes());r['work_state']['reviews']['abstract']['tests'].append('test_mr_review.py')
 matches=[]
 for e in r['evidence']:
  if not e['path'].endswith('.json'):continue
  data=valid_bytes(e)
  if not data:continue
  try:payload=json.loads(data)
  except ValueError:continue
  if 'query' not in payload or 'documents' not in payload:continue
  try:rows=select_documents(p,payload,payload['query']['original_query'])
  except ValueError:continue
  matches.extend((d,e) for d in rows)
 if matches:
  reason='Summon UI response rule: assigned title/subtitle, every author surname, publication year, type, DOI/ISBN conflicts and available volume/issue/start/end pages checked against actual response. MathML differences are not erased.'
  if r['identity'].get('status')!='confirmed':r['identity']={'status':'confirmed','reason':reason}
  record_review(r,'identity',reason,[e['path'] for d,e in matches])
  choices=[]
  for d,e in matches:
   for a in d.get('abstracts') or []:
    text=a.get('abstract','').strip()
    if classify(text)=='database_indexing_abstract':choices.append((text,d,e,a))
  if choices and r['abstract'].get('status')!='found':
   text,d,e,a=max(choices,key=lambda v:len(v[0]));artifact=capture(p['paper_id'],'database-abstract.txt',text,e['url'],'database-indexing-abstract')
   r['abstract']=database_abstract(text,artifact,d.get('content_type'),a.get('attribution',''))
  if r['abstract'].get('status')=='found':
   artifacts=r['abstract'].get('artifacts',[])
   if len(artifacts)==1:
    data=valid_bytes(artifacts[0])
    if data:
     try:actual=data.decode('utf-8-sig').strip()
     except UnicodeError:actual=None
     bound=[e['path'] for text,d,e,a in choices if text==actual]
     if bound:
      r['abstract'].setdefault('source_kind','database_indexing_abstract');r['abstract'].setdefault('provided_by','Summon');r['abstract'].setdefault('wording_author_status','not_verified')
      record_review(r,'abstract','Complete corresponding Summon abstract field preserved exactly. Tested classifier rejects placeholders, citation-only fields, reviews, preface/text excerpts, contents and trailing truncated snippets; no book-type exclusion.',bound+[artifacts[0]['path']])
 for c in r.get('fulltext_candidates',[]):
  url=c['artifact']['url'];data=valid_bytes(c['artifact'])
  if data and re.search(r'/content/pdf/b[fb]m:',url):
   c.update(status='not_fulltext',reason='Observed Springer bfm/bbm download is front/back matter, not the book body; pilot verified the distinct preliminary and reference/index PDF scopes.')
   for t in r['work_state']['tasks']:
    if t['kind']=='review' and t['target']==c['artifact']['path']:t.update(status='done',reason=c['reason'],evidence_paths=[c['artifact']['path'],c['front_text_path']])
  elif data and c.get('status')=='needs_review' and r['fulltext'].get('status')!='found':
   from pdf_review import book_match
   match=book_match(p,BASE/c['artifact']['path'])
   if match:
    if r['identity'].get('status')!='confirmed':r['identity']={'status':'confirmed','reason':match['reason']};record_review(r,'identity',match['reason'],[c['artifact']['path']])
    r['fulltext']={'status':'found','artifacts':[c['artifact']],**match};c.update(status='accepted',reason=match['reason']);record_review(r,'fulltext',match['reason'],[c['artifact']['path']])
    for t in r['work_state']['tasks']:
     if t['kind']=='review' and t['target']==c['artifact']['path']:t.update(status='done',reason=match['reason'],evidence_paths=[c['artifact']['path']])
  if data and c.get('status')=='needs_review' and p.get('record_type')=='article':
   from article_review import inspect_article
   match=inspect_article(p,BASE/c['artifact']['path'])
   if match:
    if r['identity'].get('status')!='confirmed':r['identity']={'status':'confirmed','reason':match['reason']};record_review(r,'identity',match['reason'],[c['artifact']['path']])
    r['fulltext']={'status':'found','artifacts':[c['artifact']],**{k:match[k] for k in ('page_count','page_range','reason')}};c.update(status='accepted',reason=match['reason']);record_review(r,'fulltext',match['reason'],[c['artifact']['path']]);r['work_state']['reviews']['fulltext']['rule_code_sha256']['article_review.py']=sha((ROOT/'article_review.py').read_bytes());r['work_state']['reviews']['fulltext']['tests'].append('test_article_review.py')
    if match['abstract_bbox'] and r['abstract'].get('status')!='found':
     import fitz
     with fitz.open(BASE/c['artifact']['path']) as doc:image_data=doc[0].get_pixmap(matrix=fitz.Matrix(2,2),clip=fitz.Rect(match['abstract_bbox'])).tobytes('png')
     image_path=RAW/p['paper_id']/('abstract-region-'+sha(image_data)[:16]+'.png')
     if not image_path.exists():image_path.write_bytes(image_data)
     a={'path':image_path.relative_to(BASE).as_posix(),'sha256':sha(image_data),'url':c['artifact']['url'],'media_type':'image/png','source_region':{'pdf':c['artifact']['path'],'pdf_sha256':c['artifact']['sha256'],'page':1,'bbox_points':match['abstract_bbox']}}
     r['abstract']={'status':'found','source_kind':'printed_author_abstract','artifacts':[a],'reason':'Printed first-page ABSTRACT heading and complete body retained as image; keywords excluded; preserves typography and diacritics without OCR correction.'};record_review(r,'abstract',r['abstract']['reason'],[c['artifact']['path'],a['path']]);r['work_state']['reviews']['abstract']['rule_code_sha256']['article_review.py']=sha((ROOT/'article_review.py').read_bytes());r['work_state']['reviews']['abstract']['tests'].append('test_article_review.py')
    for t in r['work_state']['tasks']:
     if t['kind']=='review' and t['target']==c['artifact']['path']:t.update(status='done',reason=match['reason'],evidence_paths=[c['artifact']['path']])
 close_restricted_fulltext(r)
 close_satisfied_work(r)
 return r

def close_satisfied_work(r):
 if r['identity'].get('status')!='confirmed' or any(r[c].get('status')!='found' for c in ('abstract','fulltext')):return
 reviews=r.get('work_state',{}).get('reviews',{})
 if any(reviews.get(c,{}).get('basis_sha256')!=component_basis(r,c) for c in ('identity','abstract','fulltext')):return
 paths=[a['path'] for c in ('abstract','fulltext') for a in r[c].get('artifacts',[])]
 reason='Requested abstract and complete fulltext are both acquired with current source-content and identity reviews; further acquisition work is unnecessary.'
 for t in r['work_state']['tasks']:
  if t['status'] in ('pending','retry','needs_review') and t['kind'] in ('search','source','pdf','review'):t.update(status='not_needed',reason=reason,evidence_paths=paths)
 for flag in ('unvisited_link','unvisited_search_pages','collection_error','needs_mathscinet_revisit'):
  if r.get(flag):r.setdefault('superseded_work_flags',[]).append({'flag':flag,'value':r.pop(flag),'reason':reason,'evidence_paths':paths})

def next_task(r,attempted):
 active=[t for t in r['work_state']['tasks'] if t['kind'] in ('search','source','pdf') and t['status'] in ('pending','retry') and t['key'] not in attempted]
 return min(active,key=lambda t:{'pdf':0,'source':1,'search':2}[t['kind']]) if active else None

def close_restricted_fulltext(r):
 if r['identity'].get('status')!='confirmed' or r['fulltext'].get('status')=='found':return
 scoped=[t for t in r['work_state']['tasks'] if t['kind'] in ('search','source','pdf')]
 sources=[t for t in scoped if t['kind']=='source']
 if not sources or any(t['status'] not in ('done','not_needed') for t in scoped):return
 if any(c.get('status') not in ('not_fulltext','rejected_other_work') for c in r.get('fulltext_candidates',[])):return
 evidence={e['path']:e for e in r['evidence']};paths=[]
 for t in sources:
  bodies=[]
  for path in t.get('evidence_paths',[]):
   e=evidence.get(path);data=valid_bytes(e) if e else None
   if data:
    try:bodies.append(data.decode('utf-8-sig'))
    except UnicodeError:pass
  if not any(re.search(r'Unusual Traffic Detected \(Error 418\)|preview of subscription content|이용가능한 전자자료가 없습니다',body,re.I) for body in bodies):return
  paths.extend(t['evidence_paths'])
 r['fulltext']={'status':'unavailable','reason':'All inventoried required searches and source/download links were visited; corresponding provider pages explicitly show traffic restriction, subscription preview or no available electronic resource. No complete fulltext PDF was obtained.'}
 record_review(r,'fulltext',r['fulltext']['reason'],paths,scope_complete=True)

def retry(fn,wait=time.sleep):
 for attempt in range(3):
  try:return fn()
  except Exception as exc:
   if attempt==2 or not re.search(r'429|50[0-9]|timeout|timed out|ERR_',str(exc),re.I):raise
   wait(2**attempt)

def page_progress(t,total,received,paths):
 t.update(discovered=total,attempted=received,remaining=max(0,total-received),evidence_paths=list(dict.fromkeys(paths)),status='done' if received>=total else 'pending',reason='Observed UI result documents processed; remaining count refers to documents, not pages.')

def fulltext_links(links):
 return [v for v in links if v.get('url','').startswith(('https://','http://')) and not re.search(r'review|reference|citation|supplement|cover|table.of.contents',v.get('text',''),re.I) and re.search(r'pdf|full.?text|download|view article|read article|^article$|원문',v.get('text','')+' '+v.get('url',''),re.I)]

def narrow_query(p,payload):
 from response_recovery import display_text
 matches=select_documents(p,payload,payload['query']['original_query'])
 if not matches:return None
 title=display_text(matches[0].get('full_title') or matches[0].get('title') or p['title'])
 surname=p.get('authors',[''])[0].split(',')[0].split()[0] if p.get('authors') else ''
 return json.dumps(title,ensure_ascii=False)+' '+surname+' '+str(p.get('year') or '')

def fielded_query(p,r):
 from fielded_search import title_author
 from response_recovery import display_text
 title=p['title'];author=p.get('authors',[''])[0].split(',')[0].split()[0] if p.get('authors') else ''
 for candidate in r.get('identity_candidates',[]):
  d=candidate['document']
  if document_matches(p,d):
   title=display_text(d.get('title') or d.get('full_title')).split(' / ')[0]
   if d.get('authors'):author=d['authors'][0].get('surname') or d['authors'][0].get('fullname','').split(',')[0]
   break
 return title_author(title,author) if author else None

def prefetch_identifiers(page,work,metrics):
 from response_recovery import primary_identifier,batch_truncated
 group=[]
 for p,r in work:
  identifier=primary_identifier(p)
  t=next((t for t in r['work_state']['tasks'] if t['kind']=='search' and t['target']==identifier and t['status'] in ('pending','retry')),None)
  if t:group.append((p,r,t))
 def fetch(items):
  query=' OR '.join(json.dumps(t['target'],ensure_ascii=False) for p,r,t in items)
  try:
   metrics['batch_searches']=metrics.get('batch_searches',0)+1
   payload=retry(lambda:search_ui(page,query))
  except Exception as exc:
   metrics['batch_errors']=metrics.get('batch_errors',0)+1
   for p,r,t in items:t['batch_failure']=type(exc).__name__
   return
  if batch_truncated(payload):
   if len(items)>1:
    metrics['batch_splits']=metrics.get('batch_splits',0)+1;mid=len(items)//2;fetch(items[:mid]);fetch(items[mid:])
   return
  e=capture('_batches','resume-'+sha(query.encode())[:16]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json'
  for p,r,t in items:
   add_evidence(r,e);consume_response(p,r,payload,e);t.update(status='done',reason='Complete actual UI identifier batch response examined for this identifier.',evidence_paths=[e['path']]);metrics['batch_candidate_reuse']=metrics.get('batch_candidate_reuse',0)+1;adjudicate_saved(p,r)
   store_json(ROOT/'results'/f"{p['paper_id']}.json",r)
 for offset in range(0,len(group),6):fetch(group[offset:offset+6])

def search_pages(page,p,r,t,metrics):
 identifiers=p.get('identifiers',{});identifier_values=identifiers.get('doi',[])+identifiers.get('isbn',[])
 if t['target'] not in identifier_values and not t['target'].startswith('(TitleCombined:'):
  query=fielded_query(p,r)
  if query:
   payload=retry(lambda:search_ui(page,query));metrics['searches']+=1
   e=capture(p['paper_id'],'fielded-'+sha(query.encode())[:12]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e);rows=consume_response(p,r,payload,e)
   ft=task(r,'search',query);page_progress(ft,int(payload['record_count']),len(payload['documents']),[e['path']])
   if ft['status']=='done' and (rows or r['identity'].get('status')=='confirmed'):
    t.update(status='not_needed',reason='Required title/author search performed in the actual indexed TitleCombined/AuthorCombined fields; publication year and edition are checked in returned bibliography. Fulltext-only citation search superseded.',evidence_paths=[e['path']]);return
 payload=retry(lambda:search_ui(page,t['target']))
 narrow=narrow_query(p,payload) if int(payload['record_count'])>100 else None
 if narrow and narrow!=t['target']:
  e=capture(p['paper_id'],'broad-'+sha(t['target'].encode())[:12]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e);consume_response(p,r,payload,e)
  narrow_payload=retry(lambda:search_ui(page,narrow));metrics['searches']+=2
  if int(narrow_payload['record_count'])<=len(narrow_payload['documents']) and select_documents(p,narrow_payload,narrow):
   ne=capture(p['paper_id'],'narrow-'+sha(narrow.encode())[:12]+'.json',json.dumps(selected_payload(narrow_payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');ne['media_type']='application/json';add_evidence(r,ne);consume_response(p,r,narrow_payload,ne)
   nt=task(r,'search',narrow);page_progress(nt,int(narrow_payload['record_count']),len(narrow_payload['documents']),[ne['path']])
   t.update(status='not_needed',reason='Exact observed title, author and year query confirms target bibliography in a complete narrower result set; broad fulltext term matches superseded.',evidence_paths=[e['path'],ne['path']],discovered=int(payload['record_count']),attempted=len(payload['documents']),remaining=int(payload['record_count'])-len(payload['documents']))
   return
  payload=retry(lambda:search_ui(page,t['target']))
 received=0;paths=[];page_number=0
 while True:
  page_number+=1;metrics['searches']+=1
  e=capture(p['paper_id'],f"search-{sha(t['target'].encode())[:12]}-{page_number}.json",json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e)
  consume_response(p,r,payload,e);paths.append(e['path']);received+=len(payload['documents'])
  page_progress(t,int(payload['record_count']),received,paths)
  store_json(ROOT/'results'/f"{p['paper_id']}.json",r)
  if not t['remaining']:break
  next_link=page.locator('a[aria-label="다음"]:visible').first
  next_link.wait_for(state='visible',timeout=15000)
  if next_link.get_attribute('aria-disabled')=='true':raise RuntimeError('Truncated UI search has no enabled observed next-page link')
  with page.expect_response(lambda response:'/api/search' in response.url,timeout=30000) as observed:next_link.click()
  response=observed.value
  if response.status!=200:raise RuntimeError('Observed UI page HTTP status '+str(response.status))
  payload=response.json()
  from response_recovery import validate_response
  validate_response(payload,t['target'])
  page.get_by_text('Done Loading Results',exact=True).first.wait_for(state='attached')

def save_pdf(p,r,data,url,metrics):
 from recovery import pdf_valid
 if not pdf_valid(data):return False
 import fitz
 digest=sha(data);path=RAW/p['paper_id']/('fulltext-candidate-'+digest[:16]+'.pdf');path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  import shutil
  if shutil.disk_usage(RAW).free<2*1024**3:raise RuntimeError('Disk free space below 2GB: defer new fulltext storage and notify root')
  path.write_bytes(data);metrics['new_pdf_files']=metrics.get('new_pdf_files',0)+1
 e={'path':path.relative_to(BASE).as_posix(),'sha256':digest,'url':url,'media_type':'application/pdf','kind':'fulltext-candidate'};add_evidence(r,e)
 with fitz.open(stream=data,filetype='pdf') as doc:
  pages=doc.page_count;text='\n'.join(doc[i].get_text() for i in range(min(pages,3)))
 extract=capture(p['paper_id'],'pdf-front-'+digest[:16]+'.txt',text,url,'pdf-front-text');add_evidence(r,extract)
 entry={'artifact':e,'page_count':pages,'front_text_path':extract['path'],'status':'needs_review'}
 if not any(x['artifact']['sha256']==digest for x in r.setdefault('fulltext_candidates',[])):r['fulltext_candidates'].append(entry)
 task(r,'review',e['path'],'needs_review','Read PDF identity, edition, page range, completeness and abstract boundary.',[e['path'],extract['path']]);metrics['pdf_responses']=metrics.get('pdf_responses',0)+1
 return e

def visit_source(context,p,r,t,metrics):
 page=context.new_page();metrics['source_visits']+=1
 try:
  observed=[]
  page.on('response',lambda response:observed.append(response) if 'application/pdf' in response.headers.get('content-type','').lower() else None)
  response=None
  try:response=page.goto(t['target'],wait_until='domcontentloaded',timeout=30000)
  except Exception:
   if not observed:raise
  for pdf in observed:
   try:
    e=save_pdf(p,r,pdf.body(),pdf.url,metrics)
    if not e:
     # Chrome can expose a small viewer document for an actual PDF response.
     # Re-fetch only the URL just observed in that browser response.
     metrics['download_attempts']=metrics.get('download_attempts',0)+1
     download=context.request.get(pdf.url,timeout=30000)
     e=save_pdf(p,r,download.body(),pdf.url,metrics)
   except Exception:continue
   if e:t.update(status='done',reason='Observed PDF saved for worker content review.',evidence_paths=[e['path']]);return
  page.wait_for_timeout(1000)
  body=page.locator('main').first if page.locator('main').count() else page.locator('body')
  text=body.inner_text(timeout=10000)
  status=response.status if response else None
  if text.strip():e=capture(p['paper_id'],'source-'+sha(t['target'].encode())[:16]+'.txt',text,page.url,'provider-page')
  else:e=capture(p['paper_id'],'source-'+sha(t['target'].encode())[:16]+'.observation.json',json.dumps({'body_text_length':0,'http_status':status,'outcome':'Empty rendered provider page; content not assessed.'}),page.url,'empty-page-observation')
  add_evidence(r,e)
  links=page.locator('a[href]').evaluate_all("es=>es.map(e=>({text:e.textContent.trim(),url:e.href})).filter(e=>/^https?:/.test(e.url))")
  for v in fulltext_links(links):
   nt=task(r,'pdf' if re.search(r'pdf|download',v['text']+' '+v['url'],re.I) else 'source',v['url']);nt.setdefault('discovered_from',e['path'])
  for selector in ('#Abs1','.c-article-section__content','#abstract','section.abstract','div.abstract','[data-test="abstract"]'):
   for node in page.locator(selector).all():
    value=node.inner_text().strip()
    if value and classify(value)=='database_indexing_abstract' and not any(x['text']==value for x in r.setdefault('abstract_candidates',[])):
     r['abstract_candidates'].append({'text':value,'evidence_path':e['path'],'provided_by':urlsplit(page.url).hostname,'status':'needs_review','selector':selector})
  t.update(status='done',reason=f'Actual source UI visited (HTTP {status}); displayed text and discovered fulltext links retained for content assessment.',evidence_paths=[e['path']])
  from source_kind import assess
  outcome=assess(text,status);t['source_outcome']=outcome
  if outcome=='retry':t.update(status='retry',reason=f'Actual source HTTP {status} or empty rendering needs retry; retained response is not a content conclusion.')
  elif outcome=='link_not_found':t['reason']='Actual handle resolver explicitly reports this requested handle cannot be found; only this link is unavailable.'
  r['attempts'].append({'method':'playwright','query':t['target'],'url':page.url,'outcome':t['reason']})
 finally:page.close()

def download_link(context,p,r,t,metrics):
 def request():
  metrics['download_attempts']=metrics.get('download_attempts',0)+1
  return context.request.get(t['target'],timeout=30000)
 response=retry(request)
 e=save_pdf(p,r,response.body(),response.url,metrics)
 if e:t.update(status='done',reason='Observed UI download link returned a readable PDF; content review remains.',evidence_paths=[e['path']])
 else:visit_source(context,p,r,t,metrics)

def mr_search(page,p,r,t,metrics):
 from recovery import mathscinet_section
 metrics['searches']+=1
 page.goto('https://mathscinet-ams-org.libproxy.knu.ac.kr/mathscinet/publications-search',wait_until='domcontentloaded')
 page.locator('#searchTextInput').fill(t['target']);page.locator('#searchTextInput').press('Enter');page.wait_for_url('**/article?mr=*')
 section=mathscinet_section(page,t['target']);body=section.inner_text()
 e=capture(p['paper_id'],'mathscinet-resume.txt',body,page.url,'mr-scoped-bibliography');add_evidence(r,e)
 link=section.get_by_role('link',name='Article',exact=True)
 if link.count():
  href=link.get_attribute('href')
  if href:task(r,'source',urljoin(page.url,href))
 t.update(status='done',reason='MathSciNet identifier detail opened using actual search UI; bibliography preserved.',evidence_paths=[e['path']])
 r['attempts'].append({'method':'playwright','query':t['target'],'url':page.url,'outcome':t['reason']})

def process_tasks(context,sp,mp,p,r,metrics):
 attempted=set()
 while True:
  active=next_task(r,attempted)
  if active is None:break
  attempted.add(active['key']);start=time.monotonic();before=tuple(len(r.get(k,[])) for k in ('identity_candidates','abstract_candidates','fulltext_candidates'))
  try:
   if active['kind']=='search':
    if re.fullmatch(r'MR\d+',active['target']):mr_search(mp,p,r,active,metrics)
    else:search_pages(sp,p,r,active,metrics)
   elif active['kind']=='pdf':download_link(context,p,r,active,metrics)
   else:visit_source(context,p,r,active,metrics)
  except Exception as exc:
   message=re.sub(r'https?://\S+','[URL omitted]',str(exc))[:1800]
   active.update(status='retry',reason=type(exc).__name__+': '+message)
   r.setdefault('execution_errors',[]).append({'task':active['key'],'type':type(exc).__name__,'detail':message,'time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
  active['elapsed_seconds']=round(time.monotonic()-start,3)
  after=tuple(len(r.get(k,[])) for k in ('identity_candidates','abstract_candidates','fulltext_candidates'))
  if after!=before:adjudicate_saved(p,r)
  store_json(ROOT/'results'/f"{p['paper_id']}.json",r)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);parser.add_argument('--saved-only',action='store_true');parser.add_argument('--paper-id',action='append');args=parser.parse_args()
 manifest_path,execution=manifest(sys.argv);start=time.monotonic();metrics=execution['metrics']
 papers=[json.loads(line) for line in (BASE/ASSIGN['members_path']).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
 if args.paper_id:papers=[p for p in papers if p['paper_id'] in args.paper_id]
 if args.limit is not None:papers=papers[:args.limit]
 work=[]
 for p in papers:
  path=ROOT/'results'/f"{p['paper_id']}.json"
  prior=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else None
  if args.saved_only and prior is None:continue
  if prior and not pending_work(prior):continue
  r=inventory(p,prior or new_result(p));adjudicate_saved(p,r);metrics['saved_evidence_reused']+=sum(t['status']=='done' for t in r['work_state']['tasks'])
  if prior:store_json(path,r)
  work.append((p,r))
 if not args.saved_only:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   browser=pw.chromium.launch(channel='chrome',headless=True);context=browser.new_context(storage_state=ASSIGN['browser_state']);context.set_default_timeout(15000)
   sp=context.new_page();sp.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=');sp.locator('#ho0').wait_for()
   if not sp.locator('#ho0').is_checked():sp.locator('#ho0').press('Space')
   sp.wait_for_function("document.querySelector('#ho0').checked");sp.wait_for_timeout(1500)
   mp=context.new_page()
   for index,(p,r) in enumerate(work):
    if index%6==0:prefetch_identifiers(sp,work[index:index+6],metrics)
    process_tasks(context,sp,mp,p,r,metrics)
    adjudicate_saved(p,r);store_json(ROOT/'results'/f"{p['paper_id']}.json",r)
    metrics['review_waiting']=sum(t['status']=='needs_review' for t in r['work_state']['tasks'])
    metrics['elapsed_seconds']=round(time.monotonic()-start,3);store_json(manifest_path,execution)
    run.progress('resume-content-review-and-browser',p['paper_id']);print(json.dumps({'paper_id':p['paper_id'],'open_tasks':len(pending_work(r)),'abstract_candidates':len(r.get('abstract_candidates',[])),'fulltext_candidates':len(r.get('fulltext_candidates',[]))}),flush=True)
   browser.close()
 metrics['elapsed_seconds']=round(time.monotonic()-start,3);execution['ended_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());store_json(manifest_path,execution)
 import subprocess
 execution['checker_at_launch']={'time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'code_sha256':{name:sha((ROOT.parent/name).read_bytes()) for name in ('check_recovery.py','work_queue.py')}};store_json(manifest_path,execution)
 check=subprocess.run([sys.executable,str(ROOT.parent/'check_recovery.py'),'--assignment',str(ROOT/'assignment.json'),'--partial'],capture_output=True,text=True,encoding='utf-8')
 (ROOT/'runs'/(manifest_path.stem+'-check.json')).write_text(check.stdout,encoding='utf-8');print(json.dumps({'saved_results':len(work),'check_exit_code':check.returncode,'run':str(manifest_path)}),flush=True)

def manifest(argv):
 now=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
 path=ROOT/'runs'/f'{now}-{os.getpid()}.json'
 code=list(ROOT.glob('*.py'))+[ROOT.parent/'work_queue.py',ROOT.parent/'check_recovery.py']
 value={'started_at':now,'pid':os.getpid(),'arguments':[sys.executable,*argv], 'code_sha256':{str(f.relative_to(ROOT.parent)):sha(f.read_bytes()) for f in code},'metrics':{'searches':0,'source_visits':0,'download_attempts':0,'pdf_responses':0,'new_pdf_files':0,'saved_evidence_reused':0,'review_waiting':0,'elapsed_seconds':0}}
 store_json(path,value);return path,value

if __name__=='__main__':
 main()
