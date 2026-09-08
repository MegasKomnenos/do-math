"""Close proven unrelated discovered branches while preserving every task and file."""
import re
from collections import defaultdict,deque
from urllib.parse import urlsplit,parse_qsl
from abstract_reclassify import valid_bytes
from scoped_links import doi

def roots(r):
 evidence={e['path']:e for e in r['evidence']};found={};body_cache={}
 for t in r.get('work_state',{}).get('tasks',[]):
  origin=t.get('discovered_from')
  if not origin or origin not in evidence:continue
  target=urlsplit(t['target']);parent=urlsplit(evidence[origin]['url'])
  if any(key.lower()=='linklocation' and value.lower()=='reference' for key,value in parse_qsl(target.query,keep_blank_values=True)):found[t['key']]='Publisher linkout explicitly declares linkLocation=Reference; FULL_TEXT is a linkout parameter, not evidence that the linked work is the target.';continue
  if re.search(r'^/(?:ftp|bulk)(?:/|$)',target.path,re.I):found[t['key']]='Observed global bulk/FTP directory or archive branch, outside the assigned document.';continue
  if 'perlego.com' in (target.hostname or '') and '/book/' in target.path:
   child=re.search(r'/book/(\d+)',target.path);source=re.search(r'/book/(\d+)',parent.path)
   if child and source and child[1]!=source[1]:found[t['key']]='Different Perlego book identifier reached from the target product page; related-book title slug -pdf is not a target download.';continue
   if child and source and child[1]==source[1] and t['kind']=='pdf':found[t['key']]='Duplicate HTML product/anchor navigation was mislabeled PDF by its -pdf slug; the original target source is preserved.';continue
  current=doi(evidence[origin]['url']);candidate=doi(t['target'])
  if 'springer' in (parent.hostname or '') and t['kind']=='source' and current and candidate and current!=candidate:
   # Actual Springer reference controls use generic Article labels. Book-child
   # DOI paths and explicit PDF/container controls are retained.
   if re.search(r'/book/',parent.path) and candidate.startswith((current+'_',current+'.')):continue
   if origin not in body_cache:
    data=valid_bytes(evidence[origin]);body_cache[origin]=data.decode('utf-8-sig') if data else ''
   if re.search(r'(?m)^References\s*$',body_cache[origin]):found[t['key']]='Different DOI discovered through the observed Springer generic Article/reference route; original page contains the References section. Target DOI and explicit download/container controls are retained.'
 return found

def prune(r):
 tasks=r.get('work_state',{}).get('tasks',[]);by_key={t['key']:t for t in tasks};children=defaultdict(list);by_url=defaultdict(set);evidence={e['path']:e for e in r['evidence']}
 for e in r['evidence']:by_url[e['url']].add(e['path'])
 for t in tasks:
  if t.get('discovered_from'):children[t['discovered_from']].append(t['key'])
 reasons=roots(r);queue=deque(reasons);blocked_paths=set()
 while queue:
  key=queue.popleft();t=by_key[key]
  if reasons[key].startswith('Duplicate HTML'):continue
  origin=t.get('discovered_from');origin_url=evidence.get(origin,{}).get('url');paths=set(t.get('scope_original_evidence_paths',t.get('evidence_paths',[])))
  paths={p for p in paths if p!=origin and evidence.get(p,{}).get('url')!=origin_url};urls=({t['target']}|{evidence[p]['url'] for p in paths if p in evidence})-{origin_url}
  for url in urls:paths.update(by_url[url])
  paths={p for p in paths if p!=origin and evidence.get(p,{}).get('url')!=origin_url}
  for path in paths:
   blocked_paths.add(path)
   for child in children[path]:
    if child not in reasons:reasons[child]='Descendant of a proven unrelated reference, related-book or global-download branch; target source inventory is retained.';queue.append(child)
 count=0;visited=0;pdf_attempt_lower_bound=0
 for key,reason in reasons.items():
  t=by_key[key]
  if t.get('scope_relation')=='unrelated':continue
  previous=t['status'];visited+=int('elapsed_seconds' in t);pdf_attempt_lower_bound+=int(t['kind']=='pdf' and 'elapsed_seconds' in t)
  t.setdefault('scope_original_evidence_paths',[p for p in t.get('evidence_paths',[]) if p!=t.get('discovered_from')])
  t.update(status='not_needed',scope_relation='unrelated',scope_previous_status=previous,reason=reason,evidence_paths=list(dict.fromkeys(t.get('evidence_paths',[])+[t['discovered_from']])));count+=1
 for candidate in r.get('fulltext_candidates',[]):
  if candidate['artifact']['path'] in blocked_paths and candidate.get('status')!='accepted':candidate.update(status='not_fulltext',reason='Preserved download belongs to a proven unrelated discovery branch; excluded from target acquisition candidates.')
 for candidate in r.get('abstract_candidates',[]):
  if candidate.get('evidence_path') in blocked_paths:candidate.update(status='additional_information',kind='out_of_scope',reason='Observed on an unrelated discovery branch; not the target abstract.')
 for t in tasks:
  if t['kind']=='review' and t['target'] in blocked_paths and t['status']=='needs_review':t.update(status='not_needed',scope_relation='unrelated',reason='Review concerns a preserved file from an excluded discovery branch.',evidence_paths=[t['target']])
 return {'newly_closed_tasks':count,'observed_steps_in_closed_branches':visited,'download_attempt_lower_bound':pdf_attempt_lower_bound,'limitation':'Prior SDK request counts were not checkpointed per step; PDF-kind steps establish a lower bound, not an exact retry count. New collector records per-step request metrics.'}
