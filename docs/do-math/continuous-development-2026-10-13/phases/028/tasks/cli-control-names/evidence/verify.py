from bounded_io import *
from collections import Counter

start=json.loads(read(OUT/'source-start.json'))
previous=json.loads(read(RUN/'phases/027/manager-evidence/source-inspected.json'))
end={p:digest(REPO/p) for p in start}
save('source-end.json',end)
assert start==previous,'027 manager source set/version differs'
assert end==start,'source changed during analysis'
assignment=next(t for t in json.loads(read(RUN/'phases/028/assignments.json'))['tasks'] if t['task']=='cli-control-names')
rows=json.loads(read(OUT/'section-decisions.json'))
packet=next(p for p in json.loads(read(RUN/'phases/001/tasks/document-closeout/evidence/followup-packets.json'))['packets'] if p['id']=='N01')
historical=[r for r in packet['required_slices'] if r['id'] in {s['id'] for s in assignment['slices']}]
assert len(rows)==27 and {r['id'] for r in rows}=={r['id'] for r in assignment['slices']}=={r['id'] for r in historical}
for r in rows:
    assert {k:r[k] for k in ('id','document','start_line','end_line','heading')}==next(s for s in assignment['slices'] if s['id']==r['id'])
    assert r['current_start']==r['start_line'] and r['current_end']==r['end_line']
    assert r['document_sha256']==digest(resolve(r['document']))
    assert len({(o['line'],o['column'],o['form']) for o in r['occurrences']})==len(r['occurrences'])
    assert r['conclusion'] in ('유지','기존 근거 재사용','문구 수정','검사 보강','정확 미결')
    assert all(o['owner_groups'] for o in r['occurrences'])
inventory=json.loads(read(RUN/'phases/001/tasks/document-closeout/evidence/source-census.json'))
old_inline=[o for o in inventory['all_inline_spans'] if o['document']==assignment['documents'][0] and o['line']<=679]
current_inline=[(o['line'],o['name']) for r in rows for o in r['occurrences'] if o['form']=='inline/table']
historical_inline_counter=Counter((o['line'],o['token']) for o in old_inline)
inline_added=list((Counter(current_inline)-historical_inline_counter).elements())
inline_removed=list((historical_inline_counter-Counter(current_inline)).elements())
assert inline_removed==[] and inline_added==[(234,'dispatch_wait.since'),(234,'dispatch_wait.limit_seconds')]
historical_candidates=[]
for item in historical:
    candidate_rows=[o for o in old_inline if item['start_line']<=o['line']<=item['end_line'] and o['token'] in item['distinct_tokens']]
    assert len(candidate_rows)==item['candidate_occurrences']
    historical_candidates.extend(candidate_rows)
assert len(historical_candidates)==assignment['historical_inline_occurrences']==692

owners=json.loads(read(OUT/'owner-profiles.json'))
used_files=set()
for group in owners.values():
    for ref in group['reuse']: assert resolve(ref).is_file(),ref
    for field in ('definitions','consumer_tests'):
        for coordinate in group[field]:
            p=resolve(coordinate['ref']); used_files.add(coordinate['ref'])
            assert coordinate['file_sha256']==digest(p)
            a,b=coordinate['lines']; source='\n'.join(read(p).splitlines()[a-1:b])
            assert coordinate['fragment_sha256']==hashlib.sha256(source.encode()).hexdigest()

c3_path=RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json'
c3=json.loads(read(c3_path))
sha_mismatch=[p for p,h in c3['source_sha256'].items() if digest(REPO/'.claude/skills/do-math/scripts'/p)!=h]
assert len(c3['source_sha256'])==875 and not sha_mismatch
doc_rows=[r for group in c3['reports'] for r in group['rows'] if r['id'].startswith('structure.test_doc_code.')]
assert len(doc_rows)==38 and all(r['outcome']=='passed' for r in doc_rows)
assert len(set(r['id'] for r in doc_rows))==38 and set(r['id'] for r in doc_rows)<=set(c3['selected'])
assert c3['changed_during_run']==[] and c3['complete'] and c3['successful']
binding_inventory=json.loads(read(RUN/'phases/001/tasks/document-closeout/evidence/binding-inventory.json'))
relevant_bindings=[r for r in binding_inventory['bindings'] if any(d.get('document')==assignment['documents'][0] and d.get('line',10000)<=679 for d in r['documents'])]
save('check-bindings.json',{'existing_c3':{'ref':'run:phases/027/tasks/doc-policy/evidence/c3/report.json','sha256':digest(c3_path),
  'python_files':875,'python_sha_mismatches':sha_mismatch,'document_rows':doc_rows,'new_run':False},
  'actual_current_assertions':{name:value['consumer_tests'] for name,value in owners.items() if value['consumer_tests']},
  'historical_binding_owners':[{'owner':r['owner'],'definition':r['definition'],'assessment':r['assessment']} for r in relevant_bindings],
  'limits':'doc_code는명령/flag·inline dotted owner·지정producer를검사한다. 모든단독값/JSON키/자연어검사가아니다. actual_current_assertions는현재소스단언이며새실행이아니다. 원38row는각범위에서만재사용한다.'})

# Source and verdict provenance for exact reusable P/B properties; no claim all old Python versions equal current.
reuse=[]
for phase,task in [('008','document-recovery'),('019','document-results'),('020','document-tools'),('022','review-delivery'),('023','document-governance'),('024','document-waits'),('025','document-trust'),('026','policy-semantics'),('027','doc-policy')]:
    report_ref=f'run:phases/{phase}/tasks/{task}/report.json'
    report=json.loads(read(resolve(report_ref)))
    item={'phase':phase,'report_ref':report_ref,'report_sha256':digest(resolve(report_ref)),'status':report['status'],
        'manager_ref':f'run:phases/{phase}/manager-evidence/review.md','manager_sha256':digest(RUN/f'phases/{phase}/manager-evidence/review.md')}
    inspected=RUN/f'phases/{phase}/manager-evidence/source-inspected.json'
    if inspected.is_file():
        prior=json.loads(read(inspected))
        matches=[]; differences=[]
        for ref in used_files:
            rel=ref.split(':',1)[1]
            if rel in prior:
                (matches if digest(REPO/rel)==prior[rel] else differences).append(ref)
        item.update(source_profile_ref=f'run:phases/{phase}/manager-evidence/source-inspected.json',source_profile_sha256=digest(inspected),
                    matched_used_files=sorted(matches),changed_used_files=sorted(differences),
                    limitation='Changed helper/source paths are not whole-file execution evidence; only unchanged exact definition/assertion and manager-approved sentence properties are reused.')
    reuse.append(item)
# Historical B132/B133/B134 original reports are read at their actual path and SHA.
history_ref='run:phases/001/tasks/document-closeout/evidence/history-selected.json'
hist=json.loads(read(resolve(history_ref)))
old_reports=[]
for name,value in hist['increments'].items():
    if value.get('id') not in ('B132','B133','B134'): continue
    for mode,entry in value['reports'].items():
        if not isinstance(entry,dict) or 'path' not in entry: continue
        p=REPO/entry['path']
        old_reports.append({'increment':value['id'],'mode':mode,'ref':'repo:'+entry['path'],
            'expected_sha256':entry['sha256'],'actual_sha256':digest(p) if p.is_file() else None,'exists':p.is_file(),
            'reuse_scope':'Only the designated manifest/restore/profile_selection owner assertion; not entire CLI-control sections.'})
        if p.is_file():
            assert digest(p)==entry['sha256']
            raw=json.loads(read(p)); old_reports[-1]['actual_rows']=[{'id':r['id'],'outcome':r['outcome']} for g in raw.get('reports',[]) for r in g.get('rows',[])]
save('reuse-profile.json',{'properties':reuse,'historical_B_reports':old_reports,'history_index_sha256':digest(resolve(history_ref)),
 'policy_decisions_ref':'run:phases/026/tasks/policy-semantics/evidence/policy-decisions.json',
 'policy_decisions_sha256':digest(RUN/'phases/026/tasks/policy-semantics/evidence/policy-decisions.json'),
 'limits':'P04/P05/P07 are role input/output outside this 27-section slice; no extra section-wide reuse claim. P03/P06/P08/P10 and policy/connection only exact current sentence/owner property. No new product execution.'})
inputs=json.loads(read(OUT/'input-profile.json'))
assert all(digest(resolve(item['ref']))==item['sha256'] for item in inputs),'input mutated'
negative=[o for row in rows for o in row['occurrences'] if o['classification']=='explicit-negative-task-state']
assert set(o['name'] for o in negative)=={'ready','performing','assessing','needs_revision'}
verification={'source_files':len(start),'start_matches_027':True,'source_changed':[],'input_files':len(inputs),'inputs_unchanged':True,
 'assigned_slices':len(rows),'exact_slice_union':True,'missing_slices':[],'duplicate_slices':[],
 'inline_occurrences':len(current_inline),'historical_all_inline_occurrences':len(old_inline),'historical_candidate_occurrences':len(historical_candidates),
 'historical_candidates_covered':True,'inline_added_since_001':inline_added,'inline_removed_since_001':inline_removed,
 'historical_inline_difference_explanation':'027 assignments sum original candidate_occurrences filtered by each slice distinct_tokens, not all inline spans. Current broader inventory retains all 849 inline, including two dispatch_wait fields introduced by prior approved024; every original692 candidate is retained.',
 'fence_occurrences':sum(len(r['occurrences']) for r in rows)-len(current_inline),
 'total_name_coordinates':sum(len(r['occurrences']) for r in rows),'owner_groups':len(owners),'negative_task_examples':negative,
 'c3_reused_doc_rows':38,'c3_python_files':875,'c3_python_sha_mismatches':[],
 'conclusions':dict(Counter(r['conclusion'] for r in rows)),'new_product_tests':0,
 'findings':len(json.loads(read(OUT/'findings.json'))),'analysis_scope':'Fixed document and code; no OS/network/model/domain effects or test runner.'}
save('verification.json',verification)
print(json.dumps(verification,ensure_ascii=False,indent=2))
