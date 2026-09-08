"""Independent abstract-access verdict for fully inspected, explicitly restricted scope."""
import json,re
from abstract_reclassify import valid_bytes
from abstract_kind import classify
from response_recovery import document_matches,validate_response
from work_queue import component_basis
def unavailable_abstract(p,r):
 if r['abstract'].get('status')=='found' or r['identity'].get('status')!='confirmed':return None
 if r.get('work_state',{}).get('reviews',{}).get('identity',{}).get('basis_sha256')!=component_basis(r,'identity'):return None
 scoped=[t for t in r.get('work_state',{}).get('tasks',[]) if t['kind'] in ('search','source','pdf') and t.get('scope_relation')!='unrelated']
 sources=[t for t in scoped if t['kind']=='source']
 if not sources or not any(t['kind']=='search' for t in scoped) or any(t['status'] not in ('done','not_needed') for t in scoped):return None
 if any(r.get(flag) for flag in ('unvisited_link','unvisited_search_pages','collection_error','needs_mathscinet_revisit')):return None
 if r.get('fulltext_candidates') or any(c.get('status')=='needs_review' for c in r.get('abstract_candidates',[])):return None
 paths=[];mr_seen=False;summon_seen=False
 evidence={e['path']:e for e in r['evidence']}
 for e in r['evidence']:
  data=valid_bytes(e)
  if not data:continue
  if 'mathscinet' in e['path'] and e['path'].endswith('.txt'):
   text=data.decode('utf-8-sig');mr_seen=True
   if re.search(r"Authors?.? abstract|From the abstract|Summary:",text,re.I):return None
   if re.search(r'(?m)^Summary\s*:?\s*$',text) and not re.search(r'From the (?:text|preface|introduction)',text,re.I):return None
   paths.append(e['path'])
  elif e['path'].endswith('.json'):
   try:payload=json.loads(data)
   except ValueError:continue
   if 'documents' not in payload or 'query' not in payload:continue
   try:validate_response(payload,payload['query']['original_query'])
   except ValueError:continue
   summon_seen=True
   for d in payload['documents']:
    if document_matches(p,d):
     for a in d.get('abstracts') or []:
      kind=classify(a.get('abstract',''))
      if kind in ('database_indexing_abstract','damaged_text','truncated_snippet','unverified_formula','unverified_excerpt'):return None
   paths.append(e['path'])
 if not mr_seen or not summon_seen:return None
 for t in sources:
  bodies=[]
  for path in t.get('evidence_paths',[]):
   e=evidence.get(path);data=valid_bytes(e) if e else None
   if data:
    try:bodies.append(data.decode('utf-8-sig'))
    except UnicodeError:pass
  if not bodies:return None
  for body in bodies:
   if re.search(r'(?im)^\s*(?:abstract|summary|résumé|resumen|zusammenfassung|аннотация|摘要|概要)\s*[:.]?\s*$',body):return None
  from source_kind import assess
  if any(assess(body,None)=='provider_failure' for body in bodies):return None
  elif not any(re.search(r'Unusual Traffic Detected \(Error 418\)|preview of subscription content|보안 확인 수행 중',body,re.I) for body in bodies):return None
  paths.extend(t['evidence_paths'])
 reason='Abstract existence itself is unverified. Corresponding inspected Summon fields contain no eligible complete abstract, MR supplies no eligible abstract, and every remaining required provider/book-inspection path explicitly restricts access. No unread candidate or unvisited/error task is used as absence evidence.'
 return {'status':'unavailable','reason':reason,'evidence_paths':list(dict.fromkeys(paths)),'scope_complete':True}
