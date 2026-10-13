"""Recheck phase 016 original evidence; never rewrite task artifacts or run suites."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/016/tasks'
E = T / 't4-fixture-repair/evidence'
B = T / 'provenance-baseline/evidence'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(data): return hashlib.sha256(data).hexdigest()
def sha(p): return digest(p.read_bytes())
def save(name, value): (O/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def git(*args, data=None): return subprocess.check_output(['git', *args], cwd=R, input=data)
def command(name, args):
    p = subprocess.run(args, cwd=R, capture_output=True)
    record = {'argv':args, 'cwd':str(R), 'exit_code':p.returncode,
              'stdout':p.stdout.decode('utf-8', errors='replace'), 'stderr':p.stderr.decode('utf-8', errors='replace')}
    save(name, record)
    assert p.returncode == 0, record

for task in ('t4-fixture-repair','provenance-baseline'):
    command(task+'-report-check.json', [sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'016',task])
head = git('rev-parse','HEAD').decode().strip()
start, end = read(E/'source-start.json'), read(E/'source-final.json')
current = {p.relative_to(R).as_posix():sha(p) for base in ('.claude/skills','.agents/skills','.agents/diff')
           for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert current == end
previous = read(RUN/'phases/015/manager-evidence/source-inspected.json')
assert all(start[p] == h for p,h in previous.items())
extra = sorted(start.keys()-previous.keys())
assert len(extra)==4 and all('/.t3-store/' in p for p in extra)
changes = sorted(p for p in start.keys()|end.keys() if start.get(p)!=end.get(p))
report = read(T/'t4-fixture-repair/report.json')
assert changes == sorted(row['path'] for row in report['changes'])
assert set(changes) <= set(read(RUN/'phases/016/phase.json')['tasks'][0]['writes'])
save('source-inspected.json', current)
checks=[]
for task in ('t4-fixture-repair','provenance-baseline'):
    for check in read(T/task/'report.json')['checks']:
        refs=[v for v in check['evidence'] if v.endswith('.command.json')]
        if refs:
            receipt=read(RUN/refs[0][4:])
            assert receipt['exit_code']==check['exit_code']
            checks.append({'reference':refs[0],'exit_code':receipt['exit_code'],'reported_result':check['result']})

suites=[]
for label,tree in [('canonical-boundary','.claude'),('canonical-unit','.claude'),('mirror-boundary','.agents'),('mirror-unit','.agents')]:
    d=E/label; r=read(d/'report.json'); receipt=read(E/(label+'.command.json'))
    rows=[v for part in r['reports'] for v in part['rows'] if not v.get('fixture')]
    ids=[v['id'] for v in rows]
    assert len(ids)==len(set(ids))==len(r['selected']) and set(ids)==set(r['selected'])
    assert r['counts']==dict(Counter(v['outcome'] for v in rows))=={'passed':len(ids)}
    assert r['complete'] and r['successful'] and receipt['exit_code']==0 and r['changed_during_run']==[]
    scripts=R/tree/'skills/do-math/scripts'
    source={p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
    assert r['source_sha256']==source
    before,after=read(E/(label+'.source-before.json')),read(E/(label+'.source-after.json'))
    changed=[p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)]
    assert all(p.endswith(('/.timings.json','/.timings-t3.json')) for p in changed)
    item={'label':label,'selected':len(ids),'counts':r['counts'],'exit_code':receipt['exit_code'],
          'python_files':len(source),'source_changes':changed,'seconds':r['total_seconds']}
    if label.endswith('boundary'):
        old_label='canonical-t4-final' if tree=='.claude' else 'mirror-t4-full'
        old=read(RUN/('phases/015/tasks/t4-adapter-report/evidence/'+old_label+'/report.json'))
        assert all(start[tree+'/skills/do-math/scripts/'+p]==h for p,h in old['source_sha256'].items())
        failed=[v['id'] for part in old['reports'] for v in part['rows'] if v['outcome'] in ('error','failed') and not v.get('fixture')]
        assert len(failed)==10 and set(failed)<=set(ids)
        item['prior_ten_failures_now_passed']=failed
        item['bootstrap_passed']=[v for v in ids if '.test_operator_bootstrap_info.' in v]
        assert len(item['bootstrap_passed'])==2
        t4=read(d/'adapter-coverage.json'); assert t4==r['t4_adapter'] and t4['complete'] and not t4['problems']
        workers={v['directory']:v for v in r['reports'] if 'directory' in v}
        assert set(workers)=={v['directory'] for v in t4['workers']}
        for w in t4['workers']:
            wd=Path(w['directory']); publication=read(wd/'adapter-measurement.json')
            assert w['status']=='merged' and w['requested']==workers[str(wd)]['requested']
            assert publication['request']=={'kind':'t4','run_id':t4['run_id'],'source_sha256':source,'requested':w['requested']}
            assert publication['source_after']==source and set(publication['artifacts'])=={'coverage.data','opened.json','entered.json'}
            assert all(sha(wd/name)==h for name,h in publication['artifacts'].items())
        item['adapter']={'workers':len(workers),'complete':True,'totals':t4['totals']}
    suites.append(item)

red=read(E/'os-official-before/report.json')
assert red['counts']=={'failed':1} and read(E/'os-official-before.command.json')['exit_code']==1
controls={}
for name,code in [('os-job-control',0),('os-job-original',1)]:
    handles=read(E/name/'handles.json'); receipt=read(E/name/'receipt.json')
    assert receipt['exit_code']==code and handles[0]['handles'][0]['handle'] is None
    assert all(v['handles'][1]['valid'] and v['handles'][2]['valid'] for v in handles)
    if code==0: assert all(v['handles'][0]['handle'] is None for v in handles)
    else:
        assert all(v['handles'][0]['handle'] and not v['handles'][0]['valid'] for v in handles[1:])
        raw=(E/name/'stderr').read_text(encoding='utf-8'); assert 'DuplicateHandle' in raw and '[WinError 6]' in raw
    controls[name]={'receipt':receipt,'handles':handles}
fixed=read(E/'repaired-os-observation.json')
assert fixed['exit_code']==0 and fixed['job_root_signaled'] and fixed['active_processes']==0 and not fixed['process_ids']
assert fixed['binary_readback'] and any(fixed['positive']['consoles'])
assert not any(fixed['negative']['consoles']) and not fixed['negative']['visible']
assert all(fixed[k]['stdin_unchanged'] for k in ('positive','negative'))
assert read(E/'repaired-os-final/actual.json')==[fixed['positive'],fixed['negative']]

audit=read(E/'fixture-audit.json'); record_path=Path(audit['record_path'])
assert sha(record_path)==audit['record_sha256']
record=read(record_path); baseline=record['baselines'][0]
assert set(baseline['fingerprint']['files'])==set(baseline['content']['files'])
assert len(baseline['content']['files'])==audit['judgment_files']==11094
assert all(baseline['content']['files'][p]==h for p,h in audit['raw_content_samples'].items())
assert audit['validation_is_synthetic'] and not audit['installation_record_adoption']

tv=read(E/'verification.json')
assert all(current[p]==start[p] for p in tv['reused_inputs'])
assert all(current[p]==start[p] for p in tv['old_015_product_paths_unchanged'])
assert all(current[p]==h for p,h in tv['selection_index_pseudo_and_t3_store_preserved'].items())
for row in tv['host_recordings_preserved']: assert sha(RUN/row['path'])==row['sha256']
for p,h in tv['tool_sha256_preserved'].items(): assert sha(Path(p))==h
corpus={p:h for p,h in start.items() if '/do-math/scripts/tests/corpus/' in p}
assert all(current[p]==h for p,h in corpus.items())
for p in corpus:
    raw=(R/p).read_bytes()
    assert git('hash-object','--no-filters','--stdin',data=raw)==git('hash-object','--path='+p,'--stdin',data=raw)
for name,needle in [('mirror-final-check','1336'),('skill-final','verified')]:
    assert read(E/(name+'.command.json'))['exit_code']==0
    assert needle in (E/(name+'.stdout')).read_text(encoding='utf-8')

manifest=read(B/'baseline-manifest.json'); root=Path(manifest['extracted_scripts'])
assert root.is_relative_to(B) and root.resolve()!=Path(manifest['current_scripts']).resolve()
parent=git('rev-parse',manifest['introduction_commit']+'^').decode().strip()
assert parent==manifest['baseline_commit']
assert git('rev-parse',parent+':'+manifest['repository_prefix']).decode().strip()==manifest['scripts_git_tree']
tree=git('ls-tree','-r','-z',parent,'--',manifest['repository_prefix']+'/')
population={}
for entry in tree.split(b'\0'):
    if not entry: continue
    header,path=entry.split(b'\t',1);mode,kind,oid=header.decode().split()
    assert kind=='blob' and mode in ('100644','100755')
    population[path.decode('utf-8')]=(mode,oid)
assert set(population)=={v['repository_path'] for v in manifest['files']}
oids=sorted({v['git_blob'] for v in manifest['files']})
batch=io.BytesIO(git('cat-file','--batch',data=('\n'.join(oids)+'\n').encode()))
objects={}
for oid in oids:
    actual,kind,size=batch.readline().decode().split(); assert actual==oid and kind=='blob'
    raw=batch.read(int(size)); assert batch.read(1)==b'\n'
    assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==oid
    objects[oid]=raw
assert not batch.read()
assert {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}=={v['path'] for v in manifest['files']}
for v in manifest['files']:
    p=root/v['path']; assert p.resolve().is_relative_to(root.resolve()) and not p.is_symlink()
    raw=p.read_bytes(); assert raw==objects[v['git_blob']] and digest(raw)==v['sha256'] and len(raw)==v['bytes']
    assert population[v['repository_path']]==(v['mode'],v['git_blob'])
assert len(manifest['files'])==manifest['file_count']==910
assert sum(v['bytes'] for v in manifest['files'])==manifest['total_bytes']==9901995
memory=git('show',manifest['introduction_commit']+':기억/layer1/M-0472.md')
assert memory==(B/'fix-memory.stdout').read_bytes() and b'010b0597' in memory
save('verification.json', {'head':head,'source_start_count':len(start),'source_final_count':len(current),'current_matches_task':True,
    'extra_preexisting_t3_store':extra,'changes':changes,'suites':suites,'os_controls':controls,'repaired_os':fixed,
    'fixture_record_sha256':sha(record_path),'fixture_judgment_files':11094,'validation_is_synthetic':True,
    'runtime_and_inputs_preserved':len(tv['reused_inputs']),'reused_inputs':tv['reused_inputs'],
    'old_015_product_paths_unchanged':tv['old_015_product_paths_unchanged'],'corpus_raw_clean_paths':len(corpus),
    'host_recordings_preserved':tv['host_recordings_preserved'],'tool_sha256_preserved':tv['tool_sha256_preserved'],
    'baseline':{'commit':parent,'introduction':manifest['introduction_commit'],'tree':manifest['scripts_git_tree'],
    'files':len(manifest['files']),'bytes':manifest['total_bytes'],'unique_blobs':len(oids),'fresh_git_bytes_equal':True,
    'manifest_sha256':sha(B/'baseline-manifest.json'),'root':str(root),'comparison_executed':False},'check_receipts':checks,
    'limits':['No product suites rerun by manager; raw task results and source bytes rechecked.',
    'Bootstrap historical WinError5 cause remains unknown; current designated cases passed.',
    'Two exact baseline comparisons and both complete T4 suites remain for phase 017.',
    'G4/G5/G6/G8 and remaining semantic/document/L01 obligations remain open.']})
print(json.dumps({'source':len(current),'changes':len(changes),'suites':[{k:v for k,v in s.items() if k in ('label','selected','counts','exit_code')} for s in suites],'baseline_files':910},ensure_ascii=False))
