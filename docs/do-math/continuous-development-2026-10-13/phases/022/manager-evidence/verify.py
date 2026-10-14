"""Recheck original evidence and current bytes; do not rerun or edit product tests."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/022/tasks/review-delivery'
E = T / 'evidence'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n, v): (O/n).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def git(*args, data=None): return subprocess.check_output(['git', *args], cwd=R, input=data)

cmd = [sys.executable, '-B', 'services/continuous-development/check.py', 'report', str(R), str(RUN), '022', T.name]
p = subprocess.run(cmd, cwd=R, capture_output=True)
save('report-check.json', dict(argv=cmd, exit_code=p.returncode, stdout=p.stdout.decode(), stderr=p.stderr.decode()))
assert p.returncode == 0
task_hashes = {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
start, end = read(E/'start.json'), read(E/'final.json')
current = {p.relative_to(R).as_posix():{'sha256':sha(p), 'bytes':p.stat().st_size}
           for root in ('.claude/skills','.agents/skills','.agents/diff')
           for p in (R/root).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
assert current == end
assert {p:v['sha256'] for p,v in start.items()} == read(RUN/'phases/021/manager-evidence/source-inspected.json')
save('source-inspected.json', {p:v['sha256'] for p,v in current.items()})
report = read(T/'report.json')
changes = sorted(p for p in start.keys() | end.keys() if start.get(p) != end.get(p))
assert changes == sorted(x['path'] for x in report['changes'])
assert set(changes) <= set(read(RUN/'phases/022/phase.json')['tasks'][0]['writes'])
assert all(start[p] == end[p] for p in start if '/do-math/' in p and p.endswith('.md'))
receipts = []
for check in report['checks']:
    ref = next(x for x in check['evidence'] if x.endswith('-process.json'))
    row = read(RUN/ref[4:])
    assert row['exit_code'] == check['exit_code'] and row['pid'] > 0 and row['start'] < row['end']
    receipts.append(dict(reference=ref, exit_code=row['exit_code'], result=check['result']))

suites, rows_by_label = {}, {}
for label, tree, exit_code in [('red','.claude',1),('red-doc','.claude',1),('focus','.claude',0),
                               ('corrected','.claude',0),('c','.claude',0),('m','.agents',0)]:
    result = read(E/label/'report.json')
    rows = [r for group in result['reports'] for r in group['rows'] if not r.get('fixture')]
    ids = [r['id'] for r in rows]
    counts = dict(Counter(r['outcome'] for r in rows))
    assert len(ids) == len(set(ids)) == len(result['selected']) and set(ids) == set(result['selected'])
    assert counts == result['counts'] and result['complete'] and not result['changed_during_run']
    assert result['successful'] == (exit_code == 0) and read(E/(label+'-process.json'))['exit_code'] == exit_code
    assert counts == ({'failed':1} if exit_code else {'passed':363,'skipped':1} if label in ('c','m') else {'passed':len(ids)})
    rows_by_label[label] = {r['id']:r for r in rows}
    suites[label] = dict(selected=len(ids), counts=counts, exit_code=exit_code,
                        nonpassed=[r for r in rows if r['outcome'] != 'passed'])
    if label in ('c','m'):
        scripts = R/tree/'skills/do-math/scripts'
        sources = {p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
        assert sources == result['source_sha256']
        b,a = read(E/(label+'-before.json')), read(E/(label+'-after.json'))
        delta = [p for p in b.keys() | a.keys() if b.get(p) != a.get(p)]
        assert all(Path(p).name in ('.timings.json','.timings-t3.json') for p in delta)
        assert all(current[p] == v for p,v in a.items() if p.startswith(tree+'/') and Path(p).name not in ('.timings.json','.timings-t3.json'))
        skipped = suites[label]['nonpassed']
        assert skipped[0]['id'] == 'unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        assert '1314' in str(skipped[0]['details'])
        suites[label].update(python_files=len(sources), source_changes=delta)
assert rows_by_label['c'].keys() == rows_by_label['m'].keys()
old_selected = read(RUN/'phases/021/tasks/document-review/evidence/c/report.json')['selected']
assert set(old_selected) <= rows_by_label['c'].keys()
failure_mapping = {}
for label in ('red','red-doc'):
    for tid in rows_by_label[label]:
        assert rows_by_label['c'][tid]['outcome'] == rows_by_label['m'][tid]['outcome'] == 'passed'
        failure_mapping[tid] = tid
assert '2 != 1' in (E/'red.stderr').read_text(encoding='utf-8')
assert 'ValueError not raised' in (E/'red-doc.stderr').read_text(encoding='utf-8')
save('failure-mapping.json', failure_mapping)

proposal_rows = {}
for label in ('c','m'):
    obs = read(E/(label+'-proposal-observation.json'))
    assert obs['official_exit_code'] == 0 and obs['satisfied']
    checked = []
    for row in obs['returns']:
        value = read(E/row['actual_return_file'])
        proposal = value['context']['role_review']['proposal']
        paths = []
        def visit(node, path='context'):
            if isinstance(node,dict):
                if node == proposal: paths.append(path)
                for k,v in node.items(): visit(v,path+'.'+k)
            elif isinstance(node,list):
                for i,v in enumerate(node): visit(v,f'{path}[{i}]')
        visit(value['context'])
        assert paths == row['paths'] == ['context.role_review.proposal']
        assert row['count'] == row['expected_count'] == 1
        checked.append(dict(stage=row['stage'],slot=row['slot'],paths=paths,file=row['actual_return_file'],sha256=sha(E/row['actual_return_file'])))
    assert len(checked) == 80
    proposal_rows[label] = checked
save('proposal-check.json', dict(expected_count=1, requirement_satisfied=True, returns=proposal_rows))

history_rows = []
for group in read(E/'history-verification.json'):
    for row in group['reports']:
        assert row['exists'] and sha(R/row['path']) == row['sha256'] == row['expected_sha256']
        history_rows.append(dict(id=group['id'],path=row['path'],sha256=row['sha256']))
save('history-check.json', history_rows)
pres = read(E/'preservation.json')
runtime_changes = [p for p in pres['runtime_and_live_inputs'] if current[p] != start[p]]
boundary_changes = [p for p in pres['fixed_runtime_and_t4_paths'] if current[p] != start[p]]
assert runtime_changes == pres['runtime_changes'] == ['.claude/skills/do-math/scripts/do_math/review_cycle.py']
assert sorted(boundary_changes) == sorted(pres['fixed_runtime_and_t4_changes']) == sorted(p for p in changes if p.endswith('/do_math/review_cycle.py'))
for path,digest in pres['tools'].items(): assert sha(path) == digest
for row in pres['host_recordings']: assert sha(RUN/row['path']) == row['sha256']
for row in pres['corpus']:
    path = row['path']; raw = (R/path).read_bytes()
    assert current[path] == start[path] and sha(R/path) == row['sha256']
    blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
    assert git('hash-object','--path='+path,'--stdin',data=raw).decode().strip() == blob == row['raw_git_blob'] == row['clean_git_blob']
for row in pres['explicit_sha']:
    assert sha(R/row['tree']/'skills/do-math/scripts/tests/corpus'/row['path']) == row['sha256']
baseline = read(RUN/'phases/018/tasks/job-cleanup/evidence/final-baseline.json')
for row in baseline['files']:
    raw = (Path(baseline['baseline'])/row['path']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row['sha256']
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob']
for label in ('mirror-build','cache-sync','mirror-check','skill-only'):
    assert read(E/(label+'-process.json'))['exit_code'] == 0
assert 'verified' in (E/'skill-only.stdout').read_text(encoding='utf-8')
prior = read(RUN/'phases/021/manager-evidence/task-files.json')
assert all(sha(RUN/'phases/021/tasks/document-review'/p) == h for p,h in prior.items())
assert task_hashes == {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
save('task-files.json', task_hashes)
products = sorted({x['path'] for phase,task in [('021','document-review'),('022','review-delivery')]
                   for x in read(RUN/f'phases/{phase}/tasks/{task}/report.json')['changes']
                   if Path(x['path']).name not in ('.timings.json','.timings-t3.json')})
save('product-paths.json', products)
save('verification.json', dict(head=git('rev-parse','HEAD').decode().strip(), sources=len(current),
    start_equal_previous=True,current_equal_final=True,changes=changes,outside_writes=[],receipts=receipts,
    suites=suites,original_failures_resolved=failure_mapping,proposal_requirement_satisfied=True,
    old_selected_preserved=len(old_selected),product_documents_unchanged=True,products_to_commit=len(products),
    preservation=dict(runtime_inputs=len(pres['runtime_and_live_inputs']),runtime_changes=runtime_changes,
        fixed_boundary_paths=len(pres['fixed_runtime_and_t4_paths']),boundary_changes=boundary_changes,
        host_recordings=len(pres['host_recordings']),tools=len(pres['tools']),corpus_paths=len(pres['corpus']),
        explicit_sha=len(pres['explicit_sha']),baseline_files=len(baseline['files'])),
    task_files_unchanged=len(task_hashes),previous_task_files_unchanged=len(prior)))
print(json.dumps(dict(sources=len(current),changes=len(changes),products=len(products),
    suites={k:{f:v[f] for f in ('selected','counts','exit_code')} for k,v in suites.items()},
    proposal_returns={k:len(v) for k,v in proposal_rows.items()},task_files=len(task_hashes)),ensure_ascii=False))
