"""Read-only consistency checks for closure-map, independent of its generator."""
import collections
import ast
import hashlib
import json
from pathlib import Path

REPO=Path('C:/math')
RUN=REPO/'docs/do-math/continuous-development-2026-10-13'
OUT=RUN/'phases/001/tasks/closure-map/evidence'
OLD=REPO/'docs/do-math/시험-재편-2026-09-29'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def walk(value):
    yield value
    if isinstance(value,dict):
        for child in value.values(): yield from walk(child)
    elif isinstance(value,list):
        for child in value: yield from walk(child)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def resolve_ref(value):
    root,name=(RUN,value[4:]) if value.startswith('run:') else (REPO,value[5:])
    assert '#' not in name, ('unexpected fragment',value)
    relative=Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts, ('unsafe reference',value)
    path=(root/relative).resolve()
    assert path.is_relative_to(root), ('escaped reference',value)
    assert path.is_file(), ('missing file reference',value)
    return path

index=read(RUN/'sources/requirements-index.json')
board=read(OLD/'단계-전환표-2026-10-03.json')
p2=read(OLD/board['stage2']['p2_bindings'])
state=read(OUT/'requirement-state.json')
tracking=read(OUT/'tracking-state.json')
prior=read(OUT/'prior-review-state.json')
expected={'stage1':board['obligations'],'stage2':board['stage2']['eleven_obligations'],
          'preservation':board['preservation'],'p2':p2['rows']}
counts={'stage1':19,'stage2':11,'preservation':61,'p2':12}
fields={'stage1':'original_requirement','stage2':'population_input_property_verbatim',
        'preservation':'original_rule','p2':'normal_expected_from_historical_prep'}
for group,source_rows in expected.items():
    result=[r for r in state['rows'] if r['group']==group]
    indexed=[r for r in index['rows'] if r['group']==group]
    ids=[r['id'] for r in result]
    assert len(ids)==counts[group] and len(ids)==len(set(ids)), (group,'count/duplicate')
    assert set(ids)=={r['id'] for r in source_rows}=={r['id'] for r in indexed}, (group,'population mismatch')
    old={r['id']:r for r in source_rows}
    ix={r['id']:r for r in indexed}
    for row in result:
        original=old[row['id']][fields[group]]
        assert row['original']==original, (group,row['id'],'changed original')
        index_field='historical_expectation' if group=='p2' else 'original'
        assert ix[row['id']][index_field]==original, (group,row['id'],'index disagrees')
        for key in ['classification','classification_reason','sources','reviewed_properties','remaining','question','next_action','tracking_task_ids','edition_limit','meaning_resolution']:
            assert row[key], (group,row['id'],'empty',key)
        assert row['classification'] in state['classifications']
        assert row['product_completion_claim'] is False
    print(f'PASS {group}: {len(ids)} original IDs, exact set, no duplicates, original text unchanged')
assert {r['id'] for r in expected['p2']}==set(board['current_work']['p2']['original_ids'])
print('PASS P2: original_ids agrees; later KD cases were not added to the denominator')

# Source text is checked for the 30 obligation quotations, not just the index.
category=(OLD/'조사/결함-범주.md').read_text(encoding='utf-8-sig')
for group in ['stage1','stage2']:
    for r in expected[group]:
        assert r[fields[group]] in category, ('obligation original absent from current source',r['id'])
print('PASS 30 obligation quotations occur verbatim in current defect-category source')

old_tasks=board['current_work']['independent_execution']['plan']['tasks']
old_by_id={t['id']:t for t in old_tasks}
task_ids=[t['id'] for t in tracking['tasks']]
assert len(task_ids)==109 and len(set(task_ids))==109 and set(task_ids)==set(old_by_id)
assert not tracking['orphan_tasks'] and not tracking['duplicate_task_ids']
original_ids={r['id'] for r in state['rows']}
for t in tracking['tasks']:
    assert [x['id'] for x in t['requirement_links']]==old_by_id[t['id']]['requirement_ids']
    assert t['classification'] in state['classifications']
    for link in t['requirement_links']:
        assert link['id'] in original_ids or link['id'] in tracking['auxiliary_requirement_goals']
        assert link['goals']
        for gid in link['goals']:
            assert '\n### '+gid+' ' in (RUN/'context.md').read_text(encoding='utf-8-sig')
    assert set(t['dependencies'])<=set(task_ids), ('unknown dependency',t['id'])
for row in state['rows']:
    assert set(row['tracking_task_ids'])=={t['id'] for t in old_tasks if row['id'] in t['requirement_ids']}
active=set(); done=set(); task_by_id={t['id']:t for t in tracking['tasks']}
def visit(tid):
    assert tid not in active, ('dependency cycle',tid)
    if tid in done: return
    active.add(tid)
    for dep in task_by_id[tid]['dependencies']: visit(dep)
    active.remove(tid); done.add(tid)
for tid in task_ids: visit(tid)
print('PASS 109 tracking tasks: unique, original/auxiliary G links preserved, no orphans, dependencies valid and acyclic')

assert len(prior['review_units'])==25
assert {r['id'] for r in prior['review_units']}=={f'PR{i:02d}' for i in range(25)}
history_ids=[b for r in prior['review_units'] for b in r['history_ids']]
assert len(history_ids)==109 and len(set(history_ids))==109
assert set(history_ids)=={f'B{i:02d}' for i in range(1,110)}
for unit in prior['review_units']:
    assert set(unit['coassign_with_tracking_tasks'])<=set(task_ids)
    assert {s['history_id'] for s in unit['review_slices']}==set(unit['history_ids'])
    assert set(unit['actual_reviewed_history_ids'])<=set(unit['history_ids'])
assert [r['id'] for r in prior['review_units'] if r['historical_status']=='review_complete']==['PR23']
print('PASS 25 prior-review areas: B01-B109 each exactly once; PR23 completion kept separate from mapping and PR06 partial review')

files=['requirement-state.json','tracking-state.json','prior-review-state.json','source-comparison.json','evidence-catalog.json','code-readback.json']
references=set(); fingerprints=0
for filename in files:
    data=read(OUT/filename)
    for item in walk(data):
        if isinstance(item,str) and item.startswith(('repo:','run:')):
            resolve_ref(item); references.add(item)
        if isinstance(item,dict) and 'reference' in item and 'sha256' in item:
            assert sha(resolve_ref(item['reference']))==item['sha256'], ('edition changed',filename,item['reference'])
            fingerprints+=1
print(f'PASS {len(references)} distinct current file references; {fingerprints} recorded file fingerprints still match')
snapshot=read(OUT/'source-comparison.json')
assert not snapshot['changed_or_missing']
assert snapshot['index_authority']['matches_recorded_sha256'] and snapshot['index_p2']['matches_recorded_sha256']
print(f'PASS baseline comparison: {len(snapshot["files"])} source/engine/product files unchanged; index authority and P2 hashes match')

missing_inputs=[(t['id'],x) for t in tracking['tasks'] for x in t['unresolved_historical_input_locators']]
missing_test_modules=[(r['id'],x['unresolved_module_locator']) for r in state['rows'] for x in r['current_test_bindings'] if 'unresolved_module_locator' in x]
print('INFO explicitly unresolved historical task input locators:',len(missing_inputs))
print('INFO explicitly unresolved historical test module locators:',len(missing_test_modules))
for item in (missing_inputs+missing_test_modules)[:12]: print('UNRESOLVED',item)
corrected_file=REPO/'.claude/skills/do-math/scripts/tests/flows/test_provider_native_storage.py'
tree=ast.parse(corrected_file.read_text(encoding='utf-8-sig'))
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='NativeStorageTests')
assert any(isinstance(n,ast.FunctionDef) and n.name=='test_native_numbers_and_public_blocks_survive_actual_runner_and_repository' for n in cls.body)
native=next(r for r in state['rows'] if r['id']=='1-C')
assert any('historical_test_id' in b and b['test_id']=='flows.test_provider_native_storage.NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository' for b in native['current_test_bindings'])
assert any(x['id']=='flows.test_provider_native_storage.NativeStorageTests.test_native_numbers_and_public_blocks_survive_actual_runner_and_repository' and x['outcome']=='passed' for x in native['observed_b129_outcomes'])
assert not missing_inputs and not missing_test_modules
print('PASS R05/R06 stale module corrected to current NativeStorageTests definition and actual B129 passed test ID')
print('PASS mapping consistency only; no product tests, T3, mutation, provider calls, G1/G2 completion claim')
