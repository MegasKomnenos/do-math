"""Resume g02 from retained evidence and explicit remaining work."""
import argparse,hashlib,json,os,re,sys,time,copy
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

def observe_response(response,metrics):
 metrics['all_http_responses']=metrics.get('all_http_responses',0)+1
 if response.status==429:metrics['all_http_429']=metrics.get('all_http_429',0)+1
 if response.status>=500:metrics['all_http_5xx']=metrics.get('all_http_5xx',0)+1
 if response.status==429 or response.status>=500:
  url=urlsplit(response.url)
  metrics.setdefault('http_failures',[]).append({'status':response.status,'host':url.hostname,'path':url.path,'resource_type':response.request.resource_type})

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

def response_attempt(r,payload,e,action):
 r['attempts'].append({'method':'playwright','query':payload['query']['original_query'],'url':e['url'],'outcome':action+f"; observed {len(payload['documents'])} documents from {payload['record_count']} reported results.",'evidence_path':e['path']})

def repair_empty_evidence(r):
 for e in list(r['evidence']):
  path=BASE/e['path']
  if e.get('kind')!='provider-page' or not path.exists() or path.stat().st_size:continue
  observation=capture(r['paper_id'],path.name+'.observation.json',json.dumps({'body_text_length':0,'original_empty_path':e['path'],'original_empty_sha256':e['sha256'],'outcome':'Empty rendered provider capture does not establish content or absence.'}),e['url'],'empty-page-observation');observation['media_type']='application/json'
  r.setdefault('superseded_capture_records',[]).append({'previous_reference':e,'status':'empty-capture-preserved-as-failed-observation','reason':'Empty bytes retained on disk; replace content evidence with explicit failed rendering observation.'})
  r['evidence'].remove(e);add_evidence(r,observation)
  for t in r.get('work_state',{}).get('tasks',[]):
   if e['path'] in t.get('evidence_paths',[]):t.update(status='retry',reason='Empty provider rendering must be revisited.',evidence_paths=[observation['path']])

def document_links(d):
 links=[]
 for key in ('link','fulltext_link','link_to_html','uris','open_access_link'):
  values=d.get(key) or []
  if isinstance(values,str):values=[values]
  for value in values:
   if isinstance(value,str) and value.startswith(('https://','http://')) and value not in links:links.append(value)
 return links

def consume_response(p,r,payload,e,save=True):
 rows=select_documents(p,payload,payload['query']['original_query'])
 for d in rows:
  if not any(x.get('document')==d for x in r.setdefault('identity_candidates',[])):
   r['identity_candidates'].append({'document':d,'evidence_path':e['path']})
  for url in document_links(d):task(r,'source',url)
  for a in d.get('abstracts') or []:
   text=a.get('abstract','').strip()
   if not text or classify(text)!='database_indexing_abstract':continue
   entry={'text':text,'evidence_path':e['path'],'provided_by':'Summon','attribution':a.get('attribution',''),'content_type':d.get('content_type'),'status':'needs_review'}
   if not any(x['text']==text for x in r.setdefault('abstract_candidates',[])):r['abstract_candidates'].append(entry)
 return rows

def inventory(p,r):
 repair_empty_evidence(r)
 state=r.setdefault('work_state',{'version':'remaining-work/1','tasks':[],'reviews':{}})
 from scope_prune import prune
 scope_change=prune(r)
 if scope_change['newly_closed_tasks']:r.setdefault('scope_repair_history',[]).append(scope_change)
 from source_kind import assess
 evidence_index={e['path']:e for e in r['evidence']}
 for existing in state['tasks']:
  if existing.get('scope_relation')=='unrelated':continue
  if existing['kind']!='source':continue
  for path in existing.get('evidence_paths',[]):
   e=evidence_index.get(path);data=valid_bytes(e) if e else None
   if not data:continue
   try:body=data.decode('utf-8-sig')
   except UnicodeError:continue
   if assess(body,None)=='retry' and existing['status'] in ('done','not_needed'):
    existing.update(status='retry',reason='Stored initialization shell or loading message did not establish source content; reopen under actual rendering-readiness rule.')
   if assess(body,None)=='no_resource':
    existing.update(source_outcome='no_resource',reason='Observed resolver offers no electronic resource; this does not establish access restriction or exhaustive content absence.')
 # Earlier selected responses omitted URI fields, but full observed documents
 # survived in identity_candidates. Reuse those bytes with explicit provenance.
 for candidate in list(r.get('identity_candidates',[])):
  d=candidate.get('document',{})
  if not document_matches(p,d):continue
  links=document_links(d)
  if not links:continue
  if any(not any(t['kind']=='source' and t['target']==url for t in state['tasks']) for url in links):
   e=capture(p['paper_id'],'retained-document-'+sha(json.dumps(d,sort_keys=True).encode())[:16]+'.json',json.dumps({'document':d,'origin_evidence_path':candidate.get('evidence_path'),'provenance':'Full observed Summon document preserved in result identity_candidates before selected-field projection.'},ensure_ascii=False),next((item['url'] for item in r['evidence'] if item['path']==candidate.get('evidence_path')),'https://knu.summon.serialssolutions.com/'),'retained-observed-document');e['media_type']='application/json';add_evidence(r,e)
   for url in links:task(r,'source',url,reason='Observed matching document content URI requires inspection.',evidence_paths=[e['path']])
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
 value={'basis_sha256':component_basis(r,component),'reason':reason,'evidence_paths':list(dict.fromkeys(paths)),'rule_code_sha256':{name:sha((ROOT/name).read_bytes()) for name in ('response_recovery.py','abstract_kind.py','abstract-content-decisions.json','resume.py','pdf_review.py','source_kind.py','mr_fields.py')},'tests':['test_response.py','test_display_markup.py','test_abstract_kind.py','test_abstract_notices.py','test_resume.py','test_live_responses.py','test_pdf_review.py','test_source_kind.py','test_mr_fields.py']}
 if scope_complete:value['scope_complete']=True
 value['method']='manual' if reason.startswith('Direct') else 'rule'
 r['work_state']['reviews'][component]=value
 for t in r['work_state']['tasks']:
  if t['kind']=='review' and t['target']==component:t.update(status='done',reason=reason,evidence_paths=value['evidence_paths'])

def should_process(prior,reassess=False):return bool(reassess or pending_work(prior))

def reassess_saved(p,r):
 old={c:copy.deepcopy(r[c]) for c in ('identity','abstract','fulltext')};reviews=copy.deepcopy(r['work_state'].get('reviews',{}))
 automatic=[c for c in old if reviews.get(c,{}).get('method')!='manual' and not reviews.get(c,{}).get('reason','').startswith('Direct')]
 for c in automatic:
  r['work_state']['reviews'].pop(c,None)
  if c!='identity' and r[c].get('status')=='found':
   for a in r[c].get('artifacts',[]):
    evidence=dict(a);evidence.setdefault('kind','previously-accepted-component');add_evidence(r,evidence)
   r[c]={'status':'unresolved','reason':'Explicit saved-evidence reassessment under current semantic rules.'}
  task(r,'review',c).update(status='needs_review',reason='Explicitly recheck current component under current semantic rules.')
 if 'fulltext' in automatic or ('abstract' in automatic and p.get('record_type')=='article'):
  for c in r.get('fulltext_candidates',[]):
   if c.get('status')=='accepted':c['status']='needs_review'
 adjudicate_saved(p,r)
 for c in automatic:
  current=r['work_state']['reviews'].get(c,{})
  if current.get('basis_sha256')!=component_basis(r,c):
   if c!='identity' or not any(v.get('method')=='manual' or v.get('reason','').startswith('Direct') for v in reviews.values()):r[c]={'status':'unresolved','reason':'Previous automatic conclusion was not reconfirmed; original artifacts retained for direct review.'}
   task(r,'review',c).update(status='needs_review',reason='Current rule did not reconfirm the previous conclusion; inspect preserved evidence.')
  before={a.get('sha256') for a in old[c].get('artifacts',[])};after={a.get('sha256') for a in r[c].get('artifacts',[])}
  if old[c].get('status')!=r[c].get('status') or before!=after:r.setdefault('reassessment_history',[]).append({'component':c,'previous':old[c],'previous_review':reviews.get(c),'reason':'Explicit reassessment changed or reopened the conclusion.'})
 return r

def reopen_cpe_routes(r):
 if r['abstract'].get('status')=='found' and r['fulltext'].get('status')=='found':return
 from source_kind import assess
 evidence={e['path']:e for e in r['evidence']};opened=False
 for t in r.get('work_state',{}).get('tasks',[]):
  if t.get('scope_relation')=='unrelated':continue
  if t['kind'] not in ('source','pdf') or t.get('last_browser')=='firefox':continue
  for path in t.get('evidence_paths',[]):
   e=evidence.get(path);data=valid_bytes(e) if e else None
   if data:
    try:body=data.decode('utf-8-sig')
    except UnicodeError:continue
    if assess(body,None)=='provider_failure':
     t.update(status='retry',preferred_browser='firefox',reason='A normal authenticated Firefox ScienceDirect route is now verified; this source requires that alternative before any CPE-based conclusion.');opened=True;break
 if opened:
  for c in ('abstract','fulltext'):
   if r[c].get('status') in ('unavailable','not_found'):
    r.setdefault('reassessment_history',[]).append({'component':c,'previous':r[c],'reason':'New normal Firefox provider route requires renewed source investigation.'});r[c]={'status':'unresolved','reason':'Verified Firefox alternative has not yet been checked for this source.'};r['work_state']['reviews'].pop(c,None)

def adjudicate_saved(p,r):
 for candidate in r.get('abstract_candidates',[]):
  kind=classify(candidate.get('text',''))
  if kind in ('placeholder','rights_notice','bibliographic_note','table_of_contents','review_excerpt','source_excerpt','audience_only','bibliographic_citation'):
   candidate.update(status='additional_information',kind=kind,reason='Current tested content rule identifies a whole non-abstract value; retained for provenance, not an unread abstract candidate.')
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
  if r['abstract'].get('status')!='found':
   from selected_summary import approved
   decision_path=ROOT/'selected-summary-decisions.json'
   selected=approved(p['paper_id'],data,json.loads(decision_path.read_text(encoding='utf-8')))
   if selected:
    a=capture(p['paper_id'],'mathscinet-selected-summary.txt',selected['text'],e['url'],'database-selected-summary')
    r['abstract']=database_abstract(selected['text'],a)
    r['abstract'].update(source_kind='database_selected_summary',provided_by='MathSciNet',section_heading=selected['section_heading'],wording_source=selected['wording_source'],author_abstract_verified=False,quotation_boundary={'open':selected['quotation_open'],'close':selected['quotation_close'],'quote_sha256':selected['quote_sha256']},raw_format='MathSciNet_text_with_TeX_preserved',reason=selected['reason'])
    record_review(r,'abstract',selected['reason'],[e['path'],a['path']])
    r['work_state']['reviews']['abstract']['rule_code_sha256'].update({'selected_summary.py':sha((ROOT/'selected_summary.py').read_bytes()),'selected-summary-decisions.json':sha(decision_path.read_bytes())});r['work_state']['reviews']['abstract']['tests'].append('test_selected_summary.py')
    if selected['following']:
     extra=capture(p['paper_id'],'mathscinet-following-selected-summary.txt',selected['following'],e['url'],'database-apparatus-outside-quotation')
     if not any(v.get('artifact',{}).get('sha256')==extra['sha256'] for v in r.get('additional_content',[])):r.setdefault('additional_content',[]).append({'kind':'database-apparatus-outside-quotation','artifact':extra})
  if checked['abstract'] and r['abstract'].get('status')!='found':
   a=capture(p['paper_id'],'mathscinet-summary.txt',checked['abstract'],e['url'],'database-indexing-abstract');r['abstract']=database_abstract(checked['abstract'],a);r['abstract']['provided_by']='MathSciNet'
   if checked.get('wording_source'):r['abstract']['wording_source']=checked['wording_source']
   if re.search(r'\\[A-Za-z]|``',checked['abstract']):r['abstract']['raw_format']='MathSciNet_text_with_TeX_preserved'
   record_review(r,'abstract','Corresponding single-MR detail explicitly supplies a complete quoted Summary; source excerpts and shared reviews are excluded by the tested boundary rule.',[e['path'],a['path']]);r['work_state']['reviews']['abstract']['rule_code_sha256']['mr_review.py']=sha((ROOT/'mr_review.py').read_bytes());r['work_state']['reviews']['abstract']['tests'].append('test_mr_review.py')
  for key,kind in [('editorial_note','editorial-bibliographic-note'),('additional_description','publisher-audience-description')]:
   if checked.get(key):
    a=capture(p['paper_id'],'mathscinet-'+key+'.txt',checked[key],e['url'],kind)
    if not any(x.get('artifact',{}).get('sha256')==a['sha256'] for x in r.get('additional_content',[])):r.setdefault('additional_content',[]).append({'kind':kind,'artifact':a})
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
 reopen_cpe_routes(r)
 close_restricted_fulltext(r)
 from negative_review import unavailable_abstract
 negative=unavailable_abstract(p,r)
 if negative:
  r['abstract']={'status':negative['status'],'reason':negative['reason']};record_review(r,'abstract',negative['reason'],negative['evidence_paths'],scope_complete=True);r['work_state']['reviews']['abstract']['rule_code_sha256']['negative_review.py']=sha((ROOT/'negative_review.py').read_bytes());r['work_state']['reviews']['abstract']['tests'].append('test_negative_review.py')
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
 from mixed_source_scope import restricted_fulltext_evidence
 mixed=restricted_fulltext_evidence(r)
 if mixed:
  r['fulltext']={'status':'unavailable','reason':'All inventoried required source and download tasks are closed. Corresponding provider pages explicitly restrict access to the full body; other resolver paths supply no electronic resource or report their particular handle cannot be found. Those latter paths are not access-restriction evidence. Preserved PDF candidates were independently rejected as front/back matter or other work; no unread PDF is used as absence evidence.','access_scope':{k:v for k,v in mixed.items() if k!='evidence_paths'}}
  record_review(r,'fulltext',r['fulltext']['reason'],mixed['evidence_paths'],scope_complete=True);r['work_state']['reviews']['fulltext']['rule_code_sha256']['mixed_source_scope.py']=sha((ROOT/'mixed_source_scope.py').read_bytes());r['work_state']['reviews']['fulltext']['tests'].append('test_mixed_source_scope.py')
  return

def retry(fn,wait=time.sleep):
 for attempt in range(3):
  try:return fn()
  except Exception as exc:
   if attempt==2 or not re.search(r'429|50[0-9]|timeout|timed out|ERR_',str(exc),re.I):raise
   wait(2**attempt)

def page_progress(t,total,received,paths):
 t.update(discovered=total,attempted=received,remaining=max(0,total-received),evidence_paths=list(dict.fromkeys(paths)),status='done' if received>=total else 'pending',reason='Observed UI result documents processed; remaining count refers to documents, not pages.')

def fulltext_links(links,page_url=''):
 from scoped_links import select_links
 return select_links(links,page_url)

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
   response_attempt(r,payload,e,'Submitted identifier batch through actual Summon search UI')
   store_json(ROOT/'results'/f"{p['paper_id']}.json",r)
 for offset in range(0,len(group),6):fetch(group[offset:offset+6])

def search_pages(page,p,r,t,metrics):
 identifiers=p.get('identifiers',{});identifier_values=identifiers.get('doi',[])+identifiers.get('isbn',[])
 if t['target'] not in identifier_values and not t['target'].startswith('(TitleCombined:'):
  query=fielded_query(p,r)
  if query:
   payload=retry(lambda:search_ui(page,query));metrics['searches']+=1
   e=capture(p['paper_id'],'fielded-'+sha(query.encode())[:12]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e);rows=consume_response(p,r,payload,e)
   response_attempt(r,payload,e,'Submitted observed title/author field expression through normal search UI')
   ft=task(r,'search',query);page_progress(ft,int(payload['record_count']),len(payload['documents']),[e['path']])
   if ft['status']=='done' and (rows or r['identity'].get('status')=='confirmed'):
    t.update(status='not_needed',reason='Required title/author search performed in the actual indexed TitleCombined/AuthorCombined fields; publication year and edition are checked in returned bibliography. Fulltext-only citation search superseded.',evidence_paths=[e['path']]);return
 payload=retry(lambda:search_ui(page,t['target']))
 narrow=narrow_query(p,payload) if int(payload['record_count'])>100 else None
 if narrow and narrow!=t['target']:
  e=capture(p['paper_id'],'broad-'+sha(t['target'].encode())[:12]+'.json',json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e);consume_response(p,r,payload,e)
  response_attempt(r,payload,e,'Submitted broad UI query before narrowing')
  narrow_payload=retry(lambda:search_ui(page,narrow));metrics['searches']+=2
  if int(narrow_payload['record_count'])<=len(narrow_payload['documents']) and select_documents(p,narrow_payload,narrow):
   ne=capture(p['paper_id'],'narrow-'+sha(narrow.encode())[:12]+'.json',json.dumps(selected_payload(narrow_payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');ne['media_type']='application/json';add_evidence(r,ne);consume_response(p,r,narrow_payload,ne)
   response_attempt(r,narrow_payload,ne,'Submitted narrowed observed-title UI query')
   nt=task(r,'search',narrow);page_progress(nt,int(narrow_payload['record_count']),len(narrow_payload['documents']),[ne['path']])
   t.update(status='not_needed',reason='Exact observed title, author and year query confirms target bibliography in a complete narrower result set; broad fulltext term matches superseded.',evidence_paths=[e['path'],ne['path']],discovered=int(payload['record_count']),attempted=len(payload['documents']),remaining=int(payload['record_count'])-len(payload['documents']))
   return
  payload=retry(lambda:search_ui(page,t['target']))
 received=0;paths=[];page_number=0
 while True:
  page_number+=1;metrics['searches']+=1
  e=capture(p['paper_id'],f"search-{sha(t['target'].encode())[:12]}-{page_number}.json",json.dumps(selected_payload(payload),ensure_ascii=False,indent=2),page.url,'observed-ui-search-response');e['media_type']='application/json';add_evidence(r,e)
  response_attempt(r,payload,e,'Submitted search UI or followed observed next-page control')
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
 page=context.new_page();metrics['source_visits']+=1;t['last_browser']=context.browser.browser_type.name
 try:
  observed=[];navigations=[]
  def observe(response):
   if 'application/pdf' in response.headers.get('content-type','').lower():observed.append(response)
   if response.request.is_navigation_request() and response.frame==page.main_frame:navigations.append(response)
  page.on('response',observe)
  response=None
  try:response=page.goto(t['target'],wait_until='domcontentloaded',timeout=30000)
  except Exception:
   if not observed:raise
  if 'degruyter' in (urlsplit(page.url).hostname or ''):
   deadline=time.monotonic()+15
   while not observed and not page.locator('h1:visible').count():
    if time.monotonic()>=deadline:raise TimeoutError('De Gruyter did not display its content heading or observed PDF after initialization.')
    page.wait_for_timeout(100)
   if not observed:page.wait_for_timeout(400)
  if navigations:response=navigations[-1]
  t['http_navigation_statuses']=[item.status for item in navigations]
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
   if e:
    t.update(status='done',reason='Observed PDF saved for worker content review.',evidence_paths=[e['path']]);r['attempts'].append({'method':'playwright','query':t['target'],'url':e['url'],'outcome':t['reason']});return
  page.wait_for_timeout(1000)
  body=page.locator('main').first if page.locator('main').count() else page.locator('body')
  text=body.inner_text(timeout=10000)
  if re.fullmatch(r'(?:Loading|Please wait)[.\s…]*',text.strip(),re.I):
   page.wait_for_function("() => {const t=(document.querySelector('main')||document.body).innerText.trim(); return t && !/^(Loading|Please wait)[.\\s…]*$/i.test(t)}",timeout=30000)
   body=page.locator('main').first if page.locator('main').count() else page.locator('body');text=body.inner_text()
  status=response.status if response else None
  if text.strip():e=capture(p['paper_id'],'source-'+sha(t['target'].encode())[:16]+'.txt',text,page.url,'provider-page')
  else:e=capture(p['paper_id'],'source-'+sha(t['target'].encode())[:16]+'.observation.json',json.dumps({'body_text_length':0,'http_status':status,'outcome':'Empty rendered provider page; content not assessed.'}),page.url,'empty-page-observation')
  add_evidence(r,e)
  from scoped_links import LINK_SCRIPT,public_link,download_kind,excluded
  links=page.locator('a[href]').evaluate_all(LINK_SCRIPT)
  public=[public_link(v) for v in links if v['url'].startswith(('http://','https://'))]
  link_e=capture(p['paper_id'],'source-link-context-'+sha(t['target'].encode())[:16]+'.json',json.dumps({'url':page.url,'links':public},ensure_ascii=False),page.url,'observed-source-link-context');link_e['media_type']='application/json';add_evidence(r,link_e)
  selected=fulltext_links(links,page.url)
  for v in selected:
   nt=task(r,download_kind(v),v['url']);nt.setdefault('discovered_from',e['path']);nt.setdefault('link_context_evidence',link_e['path']);nt.setdefault('link_label',v['text'])
  for v in links:
   reason=excluded(v,page.url)
   if reason and reason.startswith(('Archive file','Session-bound')) and re.match(r'^(?:download|view|read)\b',v.get('text',''),re.I):
    safe=public_link(v);nt=task(r,'source',safe['url'],'needs_review',reason,[e['path'],link_e['path']]);nt.update(status='needs_review',reason=reason);nt.setdefault('discovered_from',e['path'])
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
  elif outcome=='provider_failure':
   if t['last_browser']=='firefox':t.update(status='needs_review',preferred_browser='firefox',reason='Firefox institution context was tried for this target but CPE persists; inspect the normal public detail/source route before a negative conclusion.')
   else:t.update(status='retry',preferred_browser='firefox',reason='Observed CPE00001 content-provision failure; verified Firefox institution route remains to be checked. This is not a subscription rejection.')
  r['attempts'].append({'method':'playwright','query':t['target'],'url':page.url,'outcome':t['reason']})
 finally:page.close()

def download_link(context,p,r,t,metrics):
 def request():
  metrics['download_attempts']=metrics.get('download_attempts',0)+1
  return context.request.get(t['target'],timeout=30000)
 response=retry(request)
 e=save_pdf(p,r,response.body(),response.url,metrics)
 if e:
  t.update(status='done',reason='Observed UI download link returned a readable PDF; content review remains.',evidence_paths=[e['path']]);r['attempts'].append({'method':'playwright','query':t['target'],'url':e['url'],'outcome':t['reason']})
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

def process_tasks(context,sp,mp,p,r,metrics,firefox_provider=None):
 attempted=set()
 while True:
  active=next_task(r,attempted)
  if active is None:break
  attempted.add(active['key']);start=time.monotonic();before=tuple(len(r.get(k,[])) for k in ('identity_candidates','abstract_candidates','fulltext_candidates'));request_before={k:metrics.get(k,0) for k in ('source_visits','download_attempts','pdf_responses','new_pdf_files')}
  try:
   source_context=context
   if active.get('preferred_browser')=='firefox' and firefox_provider:
    source_context,proof=firefox_provider.get()
    if proof:
     e=capture('_browser','firefox-provider-ready.json',json.dumps(proof,ensure_ascii=False,indent=2),proof['url'],'authenticated-provider-ui');add_evidence(r,e)
   if active['kind']=='search':
    if re.fullmatch(r'MR\d+',active['target']):mr_search(mp,p,r,active,metrics)
    else:search_pages(sp,p,r,active,metrics)
   elif active['kind']=='pdf':download_link(source_context,p,r,active,metrics)
   else:visit_source(source_context,p,r,active,metrics)
   if active.get('source_outcome')=='provider_failure' and active.get('last_browser')!='firefox' and firefox_provider:
    source_context,proof=firefox_provider.get()
    if proof:
     e=capture('_browser','firefox-provider-ready.json',json.dumps(proof,ensure_ascii=False,indent=2),proof['url'],'authenticated-provider-ui');add_evidence(r,e)
    visit_source(source_context,p,r,active,metrics)
  except Exception as exc:
   message=re.sub(r'https?://\S+','[URL omitted]',str(exc))[:1800]
   message=re.sub(r'(?im)^\s*[- ]*(?:cookie|set-cookie|authorization|x-api-key)\s*:.*$','[private header omitted]',message)
   active.update(status='retry',reason=type(exc).__name__+': '+message)
   r.setdefault('execution_errors',[]).append({'task':active['key'],'type':type(exc).__name__,'detail':message,'time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())})
   error_url=active['target'] if active['target'].startswith(('https://','http://')) else getattr(mp if re.fullmatch(r'MR\d+',active['target']) else sp,'url','https://knu.summon.serialssolutions.com/')
   parts=urlsplit(error_url);error_url=parts._replace(query='',fragment='').geturl()
   e=capture(p['paper_id'],'collection-error-'+sha(active['key'].encode())[:12]+'.json',json.dumps({'task':active['key'],'query':active['target'],'exception_type':type(exc).__name__,'detail':message,'outcome':'Collection step failed; no absence conclusion follows.'},ensure_ascii=False,indent=2),error_url,'collector-error-observation');e['media_type']='application/json';add_evidence(r,e)
   active['evidence_paths']=[e['path']];r['attempts'].append({'method':'playwright','query':active['target'],'url':error_url,'outcome':active['reason']})
  active['elapsed_seconds']=round(time.monotonic()-start,3)
  active['request_metrics']={key:metrics.get(key,0)-value for key,value in request_before.items()}
  after=tuple(len(r.get(k,[])) for k in ('identity_candidates','abstract_candidates','fulltext_candidates'))
  if after!=before:adjudicate_saved(p,r)
  store_json(ROOT/'results'/f"{p['paper_id']}.json",r)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);parser.add_argument('--saved-only',action='store_true');parser.add_argument('--reassess',action='store_true');parser.add_argument('--paper-id',action='append');parser.add_argument('--shard-index',type=int,default=0);parser.add_argument('--shard-count',type=int,default=1);parser.add_argument('--max-papers',type=int);args=parser.parse_args()
 manifest_path,execution=manifest(sys.argv);start=time.monotonic();metrics=execution['metrics']
 papers=[json.loads(line) for line in (BASE/ASSIGN['members_path']).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
 from shard import partition
 papers=partition(papers,args.shard_index,args.shard_count)
 run.configure_scope(papers,args.shard_index,args.shard_count)
 execution['shard']={'index':args.shard_index,'count':args.shard_count,'assigned':len(papers),'owned_ids_sha256':sha('\n'.join(p['paper_id'] for p in papers).encode())};store_json(manifest_path,execution)
 if args.paper_id:papers=[p for p in papers if p['paper_id'] in args.paper_id]
 if args.limit is not None:papers=papers[:args.limit]
 work=[];missing_ids=set()
 for p in papers:
  path=ROOT/'results'/f"{p['paper_id']}.json"
  prior=json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else None
  if prior is None:missing_ids.add(p['paper_id'])
  if args.saved_only and prior is None:continue
  if prior and not should_process(prior,args.reassess):continue
  r=inventory(p,prior or new_result(p))
  if args.reassess:reassess_saved(p,r)
  else:adjudicate_saved(p,r)
  metrics['saved_evidence_reused']+=sum(t['status']=='done' for t in r['work_state']['tasks'])
  if prior:store_json(path,r)
  work.append((p,r))
 work.sort(key=lambda pair:pair[0]['paper_id'] not in missing_ids)
 if args.max_papers is not None:work=work[:args.max_papers]
 if not args.saved_only:
  from playwright.sync_api import sync_playwright
  with sync_playwright() as pw:
   from firefox_provider import FirefoxProvider
   firefox_provider=FirefoxProvider(pw,ASSIGN['browser_state'])
   browser=pw.chromium.launch(channel='chrome',headless=True);context=browser.new_context(storage_state=ASSIGN['browser_state']);context.set_default_timeout(15000)
   context.on('response',lambda response:observe_response(response,metrics))
   sp=context.new_page();sp.goto('https://kudos.knu.ac.kr/pages/index.htm',wait_until='domcontentloaded');sp.get_by_role('link',name='로그아웃',exact=True).wait_for(state='visible')
   execution['authentication']=capture('_browser','chrome-authentication.json',json.dumps({'authenticated':True,'visible_logout':True,'observed_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pid':os.getpid()}),sp.url,'authentication-observation');store_json(manifest_path,execution)
   sp.goto('https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=');sp.locator('#ho0').wait_for()
   if not sp.locator('#ho0').is_checked():sp.locator('#ho0').press('Space')
   sp.wait_for_function("document.querySelector('#ho0').checked");sp.wait_for_timeout(1500)
   mp=context.new_page()
   for index,(p,r) in enumerate(work):
    if index%6==0:prefetch_identifiers(sp,work[index:index+6],metrics)
    process_tasks(context,sp,mp,p,r,metrics,firefox_provider=firefox_provider)
    adjudicate_saved(p,r);store_json(ROOT/'results'/f"{p['paper_id']}.json",r)
    metrics['review_waiting']=sum(t['status']=='needs_review' for t in r['work_state']['tasks'])
    metrics['elapsed_seconds']=round(time.monotonic()-start,3);store_json(manifest_path,execution)
    run.progress('resume-content-review-and-browser',p['paper_id']);print(json.dumps({'paper_id':p['paper_id'],'open_tasks':len(pending_work(r)),'abstract_candidates':len(r.get('abstract_candidates',[])),'fulltext_candidates':len(r.get('fulltext_candidates',[]))}),flush=True)
   firefox_provider.close();browser.close()
 if args.saved_only:run.progress('saved-evidence-reassessed' if args.reassess else 'saved-evidence-assessed')
 metrics['elapsed_seconds']=round(time.monotonic()-start,3);execution['ended_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());store_json(manifest_path,execution)
 import subprocess
 execution['checker_at_launch']={'time':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'code_sha256':{name:sha((ROOT.parent/name).read_bytes()) for name in ('check_recovery.py','work_queue.py')}};store_json(manifest_path,execution)
 check=subprocess.run([sys.executable,str(ROOT.parent/'check_recovery.py'),'--assignment',str(ROOT/'assignment.json'),'--partial'],capture_output=True,text=True,encoding='utf-8')
 (ROOT/'runs'/(manifest_path.stem+'-check.json')).write_text(check.stdout,encoding='utf-8');print(json.dumps({'saved_results':len(work),'check_exit_code':check.returncode,'run':str(manifest_path)}),flush=True)

def manifest(argv):
 now=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
 path=ROOT/'runs'/f'{now}-{os.getpid()}.json'
 code=list(ROOT.glob('*.py'))+[ROOT/'selected-summary-decisions.json',ROOT/'abstract-content-decisions.json',ROOT.parent/'work_queue.py',ROOT.parent/'check_recovery.py']
 value={'started_at':now,'pid':os.getpid(),'arguments':[sys.executable,*argv], 'code_sha256':{str(f.relative_to(ROOT.parent)):sha(f.read_bytes()) for f in code},'metrics':{'searches':0,'source_visits':0,'download_attempts':0,'pdf_responses':0,'new_pdf_files':0,'saved_evidence_reused':0,'review_waiting':0,'elapsed_seconds':0}}
 store_json(path,value);return path,value

if __name__=='__main__':
 main()
