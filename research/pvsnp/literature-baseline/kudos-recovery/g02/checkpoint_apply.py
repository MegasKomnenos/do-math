"""Apply hash-bound direct decisions only while both collectors are stopped."""
import json,sys,time
import resume
from resume import ROOT,BASE,sha,task,add_evidence,record_review,store_json

def main():
 manifest,execution=resume.manifest(sys.argv);changed={};notes=[]
 papers={p['paper_id']:p for p in [json.loads(line) for line in (BASE/resume.ASSIGN['members_path']).read_text(encoding='utf-8-sig').splitlines()]}
 def record(pid):
  if pid not in changed:changed[pid]=json.loads((ROOT/'results'/f'{pid}.json').read_text(encoding='utf-8'))
  return changed[pid]
 for d in json.loads((ROOT/'partial-pdf-decisions.json').read_text(encoding='utf-8')):
  if sha((BASE/d['artifact_path']).read_bytes())!=d['artifact_sha256']:raise ValueError('Partial PDF decision source changed.')
  r=record(d['paper_id']);c=next(c for c in r['fulltext_candidates'] if c['artifact']['sha256']==d['artifact_sha256']);c.update(status='not_fulltext',reason=d['reason'])
  for t in r['work_state']['tasks']:
   if t['kind']=='review' and t['target']==d['artifact_path']:t.update(status='done',reason=d['reason'],evidence_paths=[d['artifact_path']])
 for d in json.loads((ROOT/'public-supplement-followups.json').read_text(encoding='utf-8')):
  r=record(d['paper_id']);e={'path':d['evidence_path'],'sha256':sha((BASE/d['evidence_path']).read_bytes()),'url':d['url'],'kind':'public-search-result-observation','media_type':'application/json'};add_evidence(r,e)
  links=r.setdefault('observed_source_links',[])
  if not any(v['url']==d['url'] for v in links):links.append({'url':d['url'],'evidence_path':e['path'],'reason':d['reason']})
  task(r,'source',d['url'],reason=d['reason'],evidence_paths=[e['path']])
 d=json.loads((ROOT/'ross-negative-decision.json').read_text(encoding='utf-8'));r=record(d['paper_id'])
 scope=[t for t in r['work_state']['tasks'] if t['kind'] in ('search','source','pdf')]
 if set(t['key'] for t in scope)!=set(d['scope_task_keys']) or any(t['status'] not in ('done','not_needed') for t in scope):raise ValueError('Ross inspected source scope changed.')
 if any(sha((BASE/path).read_bytes())!=h for path,h in d['source_sha256'].items()):raise ValueError('Ross reviewed source bytes changed.')
 public_path=next(path for path in d['evidence_paths'] if path.endswith('public-complement-search.json'))
 add_evidence(r,{'path':public_path,'sha256':d['source_sha256'][public_path],'url':'https://www.mathsoc.jp/section/complex/PDF/1996_1.pdf','kind':'public-search-results-containing-book-citations','media_type':'application/json'})
 for component in ('abstract','fulltext'):
  if r[component]['status']=='found':raise ValueError('New positive evidence must not be overwritten by prior negative review.')
  r.setdefault('reassessment_history',[]).append({'component':component,'previous':r[component],'reason':'Direct completion of inspected scope distinguishes no-resource from actual restriction.'})
  r[component]=d[component];record_review(r,component,d[component]['reason'],d['evidence_paths'],scope_complete=True)
 for pid,r in changed.items():
  resume.adjudicate_saved(papers[pid],r);store_json(ROOT/'results'/f'{pid}.json',r);notes.append({'paper_id':pid,'abstract':r['abstract']['status'],'fulltext':r['fulltext']['status'],'remaining':len(resume.pending_work(r))})
 execution['ended_at']=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime());execution['applied_decisions']={name:sha((ROOT/name).read_bytes()) for name in ('partial-pdf-decisions.json','public-supplement-followups.json','ross-negative-decision.json')};execution['results']=notes;store_json(manifest,execution);print(json.dumps({'run':str(manifest),'updated':notes},ensure_ascii=False))

if __name__=='__main__':main()
