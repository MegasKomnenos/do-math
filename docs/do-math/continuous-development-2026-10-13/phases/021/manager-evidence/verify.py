"""Read original phase 021 evidence and verify current files without running suites."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/021/tasks/document-review'
E = T / 'evidence'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, value): (O / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def git(*args, data=None): return subprocess.check_output(['git', *args], cwd=R, input=data)
def command(name, argv):
    p = subprocess.run(argv, cwd=R, capture_output=True)
    save(name, dict(argv=argv, cwd=str(R), exit_code=p.returncode,
                   stdout=p.stdout.decode('utf-8', errors='replace'), stderr=p.stderr.decode('utf-8', errors='replace')))
    assert p.returncode == 0

command('report-check.json', [sys.executable, '-B', 'services/continuous-development/check.py',
                             'report', str(R), str(RUN), '021', T.name])
before_task = {p.relative_to(T).as_posix(): sha(p) for p in T.rglob('*') if p.is_file()}
start, end = read(E / 'start.json'), read(E / 'final.json')
current = {p.relative_to(R).as_posix(): {'sha256':sha(p), 'bytes':p.stat().st_size}
           for base in ('.claude/skills', '.agents/skills', '.agents/diff')
           for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
assert current == end
assert {p:v['sha256'] for p,v in start.items()} == read(RUN / 'phases/020/manager-evidence/source-inspected.json')
save('source-inspected.json', {p:v['sha256'] for p,v in current.items()})
report = read(T/'report.json')
changes = sorted(p for p in start.keys() | end.keys() if start.get(p) != end.get(p))
assert changes == sorted(x['path'] for x in report['changes'])
assert set(changes) <= set(read(RUN/'phases/021/phase.json')['tasks'][0]['writes'])
receipts = []
for check in report['checks']:
    ref = next(x for x in check['evidence'] if x.endswith('-process.json'))
    row = read(RUN / ref[4:])
    assert row['exit_code'] == check['exit_code'] and row['pid'] > 0 and row['start'] < row['end']
    receipts.append({'reference':ref, 'exit_code':row['exit_code'], 'result':check['result']})

suites = {}
all_rows = {}
for label, tree, counts, exit_code in [
    ('red','.claude',{'failed':1},1), ('focus','.claude',{'passed':39,'error':3},1),
    ('corrected','.claude',{'passed':1,'error':2},1), ('corrected2','.claude',{'error':2},1),
    ('corrected3','.claude',{'error':2},1), ('corrected4','.claude',{'passed':3},0),
    ('focused-final','.claude',{'passed':67},0),
    ('c','.claude',{'passed':269,'skipped':1},0), ('m','.agents',{'passed':269,'skipped':1},0)]:
    result = read(E/label/'report.json')
    rows = [r for group in result['reports'] for r in group['rows'] if not r.get('fixture')]
    ids = [r['id'] for r in rows]
    receipt = read(E/(label+'-process.json'))
    assert len(ids) == len(set(ids)) == len(result['selected'])
    assert set(ids) == set(result['selected'])
    assert dict(Counter(r['outcome'] for r in rows)) == counts == result['counts']
    assert result['complete'] and not result['changed_during_run']
    assert result['successful'] == (exit_code == 0) and receipt['exit_code'] == exit_code
    all_rows[label] = {r['id']:r for r in rows}
    suites[label] = {'selected':len(ids),'counts':counts,'exit_code':exit_code,
                     'nonpassed':[r for r in rows if r['outcome'] != 'passed']}
    if label in ('c','m'):
        root = R/tree/'skills/do-math/scripts'
        sources = {p.relative_to(root).as_posix():sha(p) for p in root.rglob('*.py') if '__pycache__' not in p.parts}
        assert result['source_sha256'] == sources
        b,a = read(E/(label+'-before.json')), read(E/(label+'-after.json'))
        delta = [p for p in b.keys() | a.keys() if b.get(p) != a.get(p)]
        assert all(Path(p).name in ('.timings.json','.timings-t3.json') for p in delta)
        assert all(current[p] == value for p,value in a.items()
                   if p.startswith(tree+'/') and Path(p).name not in ('.timings.json','.timings-t3.json'))
        skipped = suites[label]['nonpassed']
        assert len(skipped)==1 and skipped[0]['id']=='unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported'
        assert '1314' in str(skipped[0]['details'])
        suites[label].update(python_files=len(sources), source_changes=delta)
assert set(all_rows['c']) == set(all_rows['m'])
failure_mapping = {}
for label in ('red','focus','corrected','corrected2','corrected3'):
    for tid,row in all_rows[label].items():
        if row['outcome'] != 'passed':
            final_id = tid.replace('unit.test_review_research_owner_contract.ResearchOwnerContractTests.test_review_stage_documents_reach_the_final_seat_input', 'sim.test_submission_review_inputs.ReviewInputTests.test_review_stage_documents_reach_the_final_seat_input')
            assert all_rows['c'][final_id]['outcome'] == all_rows['m'][final_id]['outcome'] == 'passed'
            failure_mapping[tid] = final_id
assert len(suites['red']['nonpassed'][0]['details']) == 4
save('failure-mapping.json', failure_mapping)

observation = read(E/'proposal-observation.json')
assert observation['official_exit_code'] == 0 and not observation['satisfied']
assert read(E/'proposal-probe-process.json')['exit_code'] == 1
proposal_rows = []
for row in observation['returns']:
    returned = read(E/row['actual_return_file'])
    proposal = returned['context']['role_review']['proposal']
    paths = []
    def visit(value, path):
        if isinstance(value, dict):
            if value == proposal: paths.append(path)
            for k,v in value.items(): visit(v,path+'.'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value): visit(v,f'{path}[{i}]')
    visit(returned['context'],'context')
    assert paths == row['complete_proposal_paths'] and len(paths) == row['count']
    proposal_rows.append({'stage':row['stage'],'slot':row['slot'],'count':len(paths),'paths':paths})
assert len(proposal_rows) == 15 and [x['count'] for x in proposal_rows] == [1]*14+[2]
save('proposal-check.json', {'expected_count':1,'rows':proposal_rows,'requirement_satisfied':False})
history = read(E/'history-verification.json')
history_rows = []
for group in history:
    for row in group['reports']:
        assert row['exists'] and sha(R/row['path']) == row['sha256'] == row['expected_sha256']
        history_rows.append({'id':group['id'],'path':row['path'],'sha256':row['sha256']})
save('history-check.json', history_rows)

pres = read(E/'preservation.json')
for path in pres['runtime_and_live_inputs'] + pres['fixed_runtime_and_t4_paths']:
    assert current[path] == start[path]
for path, digest in pres['tools'].items(): assert sha(path) == digest
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
assert before_task == {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file()}
save('task-files.json', before_task)
save('verification.json', {'head':git('rev-parse','HEAD').decode().strip(), 'sources':len(current),
    'start_equal_previous':True,'current_equal_final':True,'changes':changes,'outside_writes':[],
    'receipts':receipts,'suites':suites,'original_failures_resolved_or_relocated':failure_mapping,'proposal_requirement_satisfied':False,
    'preservation':{'runtime_and_live_inputs':len(pres['runtime_and_live_inputs']),
        'fixed_runtime_and_t4_paths':len(pres['fixed_runtime_and_t4_paths']), 'host_recordings':len(pres['host_recordings']),
        'tools':len(pres['tools']),'corpus_paths':len(pres['corpus']),'explicit_sha':len(pres['explicit_sha']),
        'baseline_files':len(baseline['files'])},'task_files_unchanged':len(before_task)})
print(json.dumps({'sources':len(current),'changes':len(changes),'suites':{k:{f:v[f] for f in ('selected','counts','exit_code')} for k,v in suites.items()},'task_files_unchanged':len(before_task)},ensure_ascii=False))
