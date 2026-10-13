"""Read task evidence without rewriting it; record manager cross-checks."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path('C:/math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
HOST = RUN / 'phases/010/tasks/host-smoke/evidence'
READ = RUN / 'phases/010/tasks/reading-limits/evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, x): (OUT/n).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def git(*a): return subprocess.check_output(['git', *a], cwd=ROOT)
def resolve(ref):
    namespace, rel = ref.split(':', 1)
    return {'repo': ROOT, 'run': RUN}[namespace] / rel.split('#')[0]

checks = {}
for task in ('host-smoke', 'reading-limits'):
    argv = [sys.executable, '-B', str(ROOT/'services/continuous-development/check.py'), 'report', str(ROOT), str(RUN), '010', task]
    p = subprocess.run(argv, cwd=ROOT, capture_output=True)
    checks[task] = {'argv':argv, 'exit_code':p.returncode, 'stdout':p.stdout.decode(), 'stderr':p.stderr.decode()}
    assert p.returncode == 0, checks[task]
save('report-checks.json', checks)
start, end = read(HOST/'source-start.json'), read(HOST/'source-end.json')
assert start == read(RUN/'phases/009/tasks/document-callable/evidence/source-final.json')
current = {p:sha(ROOT/p) for p in end}
assert current == end
save('source-inspected.json', current)
changed = sorted(p for p in set(start)|set(end) if start.get(p) != end.get(p))
report = read(HOST.parent/'report.json')
allowed = read(RUN/'phases/010/phase.json')['tasks'][0]['writes']
assert set(changed) == set(allowed) == {r['path'] for r in report['changes']}
assert not read(READ.parent/'report.json')['changes']

suites = {}
for label, tree in [('host-01','.claude'), ('host-02','.claude'), ('host-final','.claude'), ('related','.claude'), ('mirror-host','.agents'), ('baseline-repro-02',None)]:
    path = HOST/(label+'-results/report.json')
    data, command = read(path), read(HOST/(label+'.command.json'))
    rows = [r for g in data['reports'] for r in g['rows']]
    ids = [r['id'] for r in rows]
    assert len(set(ids)) == len(ids) == len(data['selected'])
    assert set(ids) == set(data['selected'])
    assert dict(Counter(r['outcome'] for r in rows)) == data['counts']
    assert data['complete'] and not data['changed_during_run']
    assert command['exit_code'] == (0 if data['successful'] else 1)
    mismatches = []
    if tree:
        before, after = read(HOST/(label+'.before.json')), read(HOST/(label+'.after.json'))
        prefix = tree+'/skills/do-math/scripts/'
        for p,h in data['source_sha256'].items():
            assert before[prefix+p] == h == after[prefix+p]
            if current.get(prefix+p) != h: mismatches.append(p)
        if label in ('host-final','related','mirror-host'): assert not mismatches
    suites[label] = {'selected_count':len(ids),'counts':data['counts'],'exit_code':command['exit_code'],
        'successful':data['successful'],'sha256':sha(path),'python_sources':len(data['source_sha256']),
        'current_mismatches':mismatches,'nonpassed':[r for r in rows if r['outcome']!='passed']}
assert suites['host-final']['counts'] == suites['mirror-host']['counts'] == {'passed':3}
assert suites['related']['counts'] == {'passed':59,'failed':1,'error':1}
assert {r['id']:r['outcome'] for r in suites['related']['nonpassed']} == {r['id']:r['outcome'] for r in suites['baseline-repro-02']['nonpassed']}
baseline = read(HOST/'baseline-manifest.json')
for p,h in baseline['hashes'].items():
    assert sha(Path(baseline['source_root'])/p) == h
    if p != 'tests/.timings.json': assert h == start['.claude/skills/do-math/scripts/'+p]
methods = {}
for rel in ('test_scheduling_windows_job.py','test_scheduling_owned_job_children.py','test_role_input_snapshot_reach.py'):
    p = '.claude/skills/do-math/scripts/tests/boundary/'+rel
    def test_asts(s):
        return {c.name+'.'+n.name:ast.dump(n, include_attributes=False) for c in ast.parse(s).body if isinstance(c,ast.ClassDef)
                for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
    old, new = test_asts(git('show','HEAD:'+p).decode('utf-8')), test_asts((ROOT/p).read_text(encoding='utf-8'))
    assert old == new
    methods[rel] = len(new)

recordings = []
for label in ('host-final','mirror-host'):
    paths = list((HOST/(label+'-results')).rglob('smoke.json'))
    assert len(paths) == 4
    for path in paths:
        r = read(path)
        assert r['passed'] and all(r['checks'].values()) and 'error' not in r
        if 'mode' in r:
            assert r['wait_after'] == dict.fromkeys(('worker','cli','child','grandchild'),0)
            assert r['worker_kernel']['creation_filetime'] == r['started']['creation_filetime']
            assert r['worker_kernel']['in_named_job']
            assert all(v['in_named_job'] and v['pid'] in r['job_pids_before'] for v in r['children_kernel'].values())
            barrier = r['result']['execution']['collect']['termination_barrier']
            assert barrier['confirmed']
            stderr = (path.parent/'call/stderr.txt').read_bytes()
            if r['mode']=='normal': assert r['result']['output']=={'host':'ok','value':'한글'} and not stderr
            if r['mode']=='nonzero': assert stderr==b'local host CLI exit 7\n' and r['result']['error_kind']=='execution_failure'
            if r['mode']=='cancel': assert r['result']['status']=='stopped' and not (path.parent/'release').exists()
        else:
            for ledger, code, status in [('readable',0,'ok'),('supplied_only',1,'refused')]:
                o = r['observations'][ledger]
                assert o['returncode']==code and o['parent_console']==0 and o['stderr']==''
                assert json.loads(o['stdout'])['records'][0]['status']==status
                assert (path.parent/ledger/'powershell-observed.json').is_file()
        recordings.append({'ref':'run:'+path.relative_to(RUN).as_posix(),'sha256':sha(path),'mode':r.get('mode','pythonw'),'checks':r['checks']})
previous = read(HOST/'verification.json')
for key in ('runtime_unchanged','provider_smoke_inputs_unchanged'):
    assert all(current[p]==start[p] for p in previous[key])
corpus = read(RUN/'phases/008/tasks/document-recovery/evidence/corpus-final.json')
corpus_paths = []
for tree, info in corpus['trees'].items():
    for row in info['files'].values():
        p = row['path']
        assert current[p]==start[p]==row['sha256']
        raw = (ROOT/p).read_bytes()
        clean = subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=ROOT,input=raw).strip()
        raw_id = subprocess.check_output(['git','hash-object','--stdin'],cwd=ROOT,input=raw).strip()
        assert clean == raw_id
        corpus_paths.append(p)
for label in ('mirror-build','cache-sync','mirror-check','skill-only'):
    assert read(HOST/(label+'.command.json'))['exit_code']==0
for label in ('mirror-check','skill-only'):
    assert not read(HOST/(label+'.command.json'))['changed_sources']

fixed = read(READ/'sources-start.json')['files']+read(READ/'additional-source-start.json')['files']
for row in fixed: assert sha(resolve(row['ref']))==row['sha256']
host_snapshot = read(READ/'host-snapshot.json')
for row in host_snapshot['binaries']: assert sha(Path(row['path']))==row['sha256']
pages, capped = read(READ/'fixture-page-results.json'), read(READ/'fixture-capped-results.json')
fixtures = []
for f in read(READ/'fixture-manifest.json')['fixtures']:
    label = f['name'].split('-')[1].split('.')[0]
    selected = sorted((p for p in pages if p['case'].startswith(label+'-')), key=lambda p:p['start'])
    delivered = []
    for p in selected:
        lines = p['result']['output'].splitlines()
        assert p['result']['exit_code']==0 and lines==f['expected_lines'][p['start']-1:p['end']]
        delivered.extend(lines)
    assert delivered == f['expected_lines']
    sample = next(p for p in capped if p['case'].startswith(label))
    text = sample['result']['output']
    ids = [int(m.group(1)) for m in re.finditer(r'(?m)^'+label+r':(\d{3})\|',text)]
    assert ids[-1]==80 and len(ids)<80 and 'truncated' in text
    fixtures.append({'label':label,'pages':len(selected),'received_lines':len(delivered),'tail':ids[-1],'missing':sorted(set(range(1,81))-set(ids))})
aggregate = read(READ/'fixture-aggregate-results.json')
assert all(len(p['result']['output'].splitlines())==10 for p in aggregate['before_outer_delivery'])
assert aggregate['model_observed']['omission_marker']=='…178 tokens truncated…'
claude = next(Path(r['path']) for r in host_snapshot['binaries'] if Path(r['path']).name=='claude.exe')
raw = claude.read_bytes()
binding = read(READ/'claude-read-binding.json')
# Excerpts include context before the matched byte offset; verify the excerpt occurs near it.
for row in binding:
    snippet = row['text'].encode('utf-8')
    assert snippet in raw[max(0,row['offset']-1000):row['offset']+3000]
save('verification.json', {'head':git('rev-parse','HEAD').decode().strip(),'source_count':len(current),
    'current_source_mismatches':[],'changes':changed,'suites':suites,'baseline_files':len(baseline['hashes']),
    'baseline_start_equivalent_noncache_files':len(baseline['hashes'])-1,
    'baseline_cache_note':'tests/.timings.json was copied from the current cost cache; excluded from source-start equivalence as declared by baseline-manifest.',
    'preserved_test_methods':methods,'host_recordings':recordings,'runtime_preserved':len(previous['runtime_unchanged']),
    'provider_inputs_preserved':len(previous['provider_smoke_inputs_unchanged']),'corpus_raw_clean_paths':len(corpus_paths),
    'reading_fixed_inputs':len(fixed),'reading_binaries':len(host_snapshot['binaries']),'reading_fixtures':fixtures,
    'claude_static_binding_excerpts':len(binding),'aggregate_observation':'Preserved task observation; not a new model delivery replay.',
    'limits':'Host partial: related failed1/error1. Reading investigation complete; output-byte/actual operator contract not certified. No product execution or edits by manager.'})
print(json.dumps({'result':'pass','sources':len(current),'changes':len(changed),'host':'3/3 each','related':suites['related']['counts'],'reading_lines':sum(r['received_lines'] for r in fixtures)},ensure_ascii=False))
