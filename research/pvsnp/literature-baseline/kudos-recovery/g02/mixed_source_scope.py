"""Distinguish explicit restrictions from exhausted resolver paths."""
from abstract_reclassify import valid_bytes
from source_kind import assess

def restricted_fulltext_evidence(r):
 if r['identity'].get('status')!='confirmed' or r['fulltext'].get('status')=='found':return None
 scope=[t for t in r.get('work_state',{}).get('tasks',[]) if t['kind'] in ('search','source','pdf') and t.get('scope_relation')!='unrelated']
 sources=[t for t in scope if t['kind']=='source']
 if not sources or any(t['status'] not in ('done','not_needed') for t in scope):return None
 if any(c.get('status') not in ('not_fulltext','rejected_other_work') for c in r.get('fulltext_candidates',[])):return None
 evidence={e['path']:e for e in r['evidence']};restricted=[];no_resource=[];missing=[]
 for t in sources:
  classified=[]
  for path in t.get('evidence_paths',[]):
   e=evidence.get(path);data=valid_bytes(e) if e else None
   if not data:continue
   try:body=data.decode('utf-8-sig')
   except UnicodeError:continue
   classified.append((assess(body,None),path))
  allowed=[(kind,path) for kind,path in classified if kind in ('restricted','no_resource','link_not_found')]
  if not allowed:return None
  # Every captured content observation must support a terminal path outcome.
  if any(kind not in ('restricted','no_resource','link_not_found') for kind,path in classified):return None
  for kind,path in allowed:
   {'restricted':restricted,'no_resource':no_resource,'link_not_found':missing}[kind].append(path)
 if not restricted:return None
 return {'restriction_evidence_paths':list(dict.fromkeys(restricted)),'no_resource_evidence_paths':list(dict.fromkeys(no_resource)),'missing_link_evidence_paths':list(dict.fromkeys(missing)),'evidence_paths':list(dict.fromkeys(restricted+no_resource+missing))}
