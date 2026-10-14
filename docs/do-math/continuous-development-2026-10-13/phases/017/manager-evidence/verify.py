"""Inspect original phase 017 evidence without running suites or editing task files."""
from collections import Counter
import hashlib
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/017/tasks/t4-baseline-integration'
E = T / 'evidence'

def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, value): (O/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def git(*args, data=None): return subprocess.check_output(['git', *args], cwd=R, input=data)
def command(name, args):
    p = subprocess.run(args, cwd=R, capture_output=True)
    row = {'argv':args, 'cwd':str(R), 'exit_code':p.returncode,
           'stdout':p.stdout.decode('utf-8', errors='replace'), 'stderr':p.stderr.decode('utf-8', errors='replace')}
    save(name, row)
    assert p.returncode == 0, row

command('report-check.json', [sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'017',T.name])
head = git('rev-parse','HEAD').decode().strip()
start, end = read(E/'source-start.json'), read(E/'source-final.json')
current = {p.relative_to(R).as_posix():sha(p) for base in ('.claude/skills','.agents/skills','.agents/diff')
           for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert current == end and start == read(RUN/'phases/016/manager-evidence/source-inspected.json')
changes = sorted(p for p in start.keys() | end.keys() if start.get(p) != end.get(p))
report = read(T/'report.json')
assert changes == sorted(v['path'] for v in report['changes'])
assert set(changes) <= set(read(RUN/'phases/017/phase.json')['tasks'][0]['writes'])
save('source-inspected.json', current)
task_hashes = {p.relative_to(T).as_posix():sha(p) for p in T.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
receipts=[]
for check in report['checks']:
    refs = [p for p in check['evidence'] if p.endswith('.command.json')]
    if refs:
        receipt = read(RUN/refs[0][4:])
        assert receipt['exit_code'] == check['exit_code'] and receipt['pid'] > 0 and receipt['started'] < receipt['ended']
        receipts.append({'reference':refs[0], 'exit_code':receipt['exit_code'], 'result':check['result']})

scripts = R/'.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts/'tests')]
import coverage
from support.adapter_coverage import validate_publication
from support.branch_gate import REASONED_EXCLUSION
from do_math.layers import LAYERS
suite_specs = [('canonical-exact','canonical-exact','.claude',{'passed':2},0),
    ('mirror-exact','mirror-exact','.agents',{'passed':2},0),
    ('canonical-t4-full','canonical-t4-full','.claude',{'passed':289,'failed':4,'error':2},1),
    ('canonical-t4-full-final','canonical-t4-full-final','.claude',{'passed':294,'error':1},1),
    ('canonical-t4-short','c4','.claude',{'passed':294,'error':1},1),
    ('mirror-t4-short','m4','.agents',{'passed':295},0)]
suites=[]
all_rows={}
for label, directory, tree, counts, exit_code in suite_specs:
    d=E/directory; result=read(d/'report.json'); receipt=read(E/(label+'.command.json'))
    rows=[v for group in result['reports'] for v in group['rows'] if not v.get('fixture')]
    ids=[v['id'] for v in rows]
    assert len(ids)==len(set(ids))==len(result['selected']) and set(ids)==set(result['selected'])
    assert result['counts']==dict(Counter(v['outcome'] for v in rows))==counts
    assert result['complete'] and result['successful']==(exit_code==0) and receipt['exit_code']==exit_code
    assert not result['changed_during_run']
    root=R/tree/'skills/do-math/scripts'
    sources={p.relative_to(root).as_posix():sha(p) for p in root.rglob('*.py') if '__pycache__' not in p.parts}
    assert result['source_sha256']==sources
    before,after=read(E/(label+'-source-before.json')),read(E/(label+'-source-after.json'))
    altered=sorted(p for p in before.keys()|after.keys() if before.get(p)!=after.get(p))
    assert all(p.endswith(('/.timings.json','/.timings-t3.json')) for p in altered)
    assert all(current[p]==h for p,h in after.items() if not p.endswith(('/.timings.json','/.timings-t3.json')))
    all_rows[label]={v['id']:v for v in rows}
    item={'label':label,'selected':len(ids),'counts':counts,'exit_code':exit_code,'python_files':len(sources),
          'seconds':receipt['seconds'],'source_changes':altered,'nonpassed':[v for v in rows if v['outcome']!='passed']}
    if '-t4-' in label:
        tree_label='canonical' if tree=='.claude' else 'mirror'
        listed=[line.split('\t')[1] for line in (E/(tree_label+'-t4-list.stdout')).read_text(encoding='utf-8').splitlines() if '\t' in line]
        assert len(listed)==len(set(listed))==len(ids) and set(listed)==set(ids)
        adapter=read(d/'adapter-coverage.json')
        assert adapter==result['t4_adapter'] and adapter['complete'] and not adapter['problems']
        assert sorted(adapter['modules'])==sorted(p for p,l in LAYERS.items() if l=='adapter')
        parent=coverage.CoverageData(basename=str(d/'adapter.data')); parent.read()
        workers=[]
        for w in adapter['workers']:
            wd=Path(w['directory']); request=read(wd/'measure.json')
            assert request['requested']==read(wd/'requested.json')==w['requested']
            assert request['source_sha256']==sources and request['run_id']==adapter['run_id']
            data=validate_publication(wd,request)
            assert w['status']=='merged' and data.has_arcs()
            wr=read(wd/'worker-report.json')
            assert wr['requested']==request['requested'] and wr['returncode']==w['returncode']
            for f in data.measured_files(): assert set(data.arcs(f) or [])<=set(parent.arcs(f) or [])
            assert data.measured_contexts()<=parent.measured_contexts()
            workers.append({'directory':str(wd),'requested':w['requested'],'returncode':w['returncode'],
                            'publication_sha256':sha(wd/'adapter-measurement.json')})
        c=coverage.Coverage(data_file=str(d/'adapter.data'),branch=True,config_file=False)
        c.set_option('report:exclude_lines',[REASONED_EXCLUSION]); c.set_option('report:partial_branches',[]); c.load()
        out=O/(label+'-raw-analysis.json')
        c.json_report(morfs=[str(root/p) for p in adapter['modules']], outfile=str(out))
        raw=read(out); mapped={(R/p).resolve():v for p,v in raw['files'].items()}
        assert raw['totals']==adapter['totals']
        for p,entry in adapter['modules'].items():
            assert entry['source_sha256']==sources[p]
            assert all(entry[k]==v for k,v in mapped[(root/p).resolve()].items())
        item['adapter']={'workers':len(workers),'complete':True,'totals':adapter['totals'],'raw_analysis_equal':True,'worker_records':workers}
        if label.endswith('-short'):
            old=read(RUN/'phases/015/tasks/t4-adapter-report/evidence'/('canonical-t4-final' if tree=='.claude' else 'mirror-t4-full')/'report.json')
            prior=[v for g in old['reports'] for v in g['rows'] if not v.get('fixture') and v['outcome']!='passed']
            assert len(prior)==12 and all(all_rows[label][v['id']]['outcome']=='passed' for v in prior)
            item['prior_twelve_now_passed']=[v['id'] for v in prior]
    suites.append(item)

# Reuse the inspected raw-only helper; redirect every write to manager-owned paths.
# It reads saved snapshots/DBs and does not launch suites or children.
sys.path.insert(0,str(E))
import verify_task
verify_task.write=lambda path,value: save('rechecked-'+Path(path).name,value)
verify_task.raw_verify()
raw=read(O/'rechecked-raw-verification.json')
assert raw==read(E/'raw-verification.json')
m=importlib.import_module('boundary.test_shared_input_provenance')
companion=read(E/'companion-result.json')
assert companion['successful'] and companion['tests_run']==2 and companion['fixtures']==6
assert companion['module_sha256']==sha(Path(m.__file__))
assert companion['worker_sha256']==hashlib.sha256(m.WORKER.encode()).hexdigest()
assert companion['snapshot_sha256']==hashlib.sha256(m.SNAPSHOT.encode()).hexdigest()
marker_checks=[]
for fixture in raw['fixtures']:
    for pair in fixture['pairs']:
        prefix=pair['prefix']; old=pair['old_markers']; new=pair['new_markers']
        if prefix=='serial':
            first=pair['ordinary']['ids'][0].split('.')[1][-1]
            consumers={'unit.test_input_'+letter+'.Case.test_consume':['outer'] for letter in 'ab'}
            expected_old={**consumers,'fixture:unit.test_input_'+first:['leaf','unused-leaf'] if fixture['nested'] else ['unused-leaf'],
                          'unit.test_input_b.Case.test_passive':['outer']}
            expected_new={**consumers,**({'shared:outer':['leaf']} if fixture['nested'] else {}),'shared:unused-outer':['unused-leaf']}
        elif prefix=='imports':
            expected_old={'fixture:unit.test_input_a':['import-leaf'],'fixture:unit.test_input_b':['fixture-parent'],
                          'unit.test_input_a.Case.test_actual':['import-leaf'],'unit.test_input_a.Case.test_paused':['fixture-parent']}
            expected_new={k:v for k,v in expected_old.items() if not k.endswith('.test_paused')}
            expected_new['shared:fixture-parent']=['import-leaf']
        else:
            assert prefix in ('a','b')
            consumer='unit.test_input_'+prefix+'.Case.test_consume'
            expected_old={consumer:['outer'],'fixture:unit.test_input_'+prefix:['leaf','unused-leaf'],
                          **({'unit.test_input_b.Case.test_passive':['outer']} if prefix=='b' else {})}
            expected_new={consumer:['outer'],'shared:outer':['leaf'],'shared:unused-outer':['unused-leaf']}
        assert old==expected_old and new==expected_new
        marker_checks.append({'fixture':fixture['preserved_root'],'prefix':prefix,'explicit_markers_match_current_assertions':True})

B=RUN/'phases/016/tasks/provenance-baseline/evidence'
manifest=read(B/'baseline-manifest.json'); base=Path(manifest['extracted_scripts'])
assert git('rev-parse',manifest['introduction_commit']+'^').decode().strip()==manifest['baseline_commit']
assert read(E/'start-baseline.json')==read(E/'final-baseline.json')
assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}=={r['path'] for r in manifest['files']}
for row in manifest['files']:
    data=(base/row['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
assert len(manifest['files'])==910
invocations=read(E/'companion-invocations.json')
children=[v for v in invocations if Path(v['argv'][0]).resolve()==Path(sys.executable).resolve() and '-c' in v['argv']]
assert len(children)==30 and all(v['exit_code']==0 and Path(v['baseline_environment'])==base for v in children)
assert any(str(base)==v['argv'][4] for v in children)

preserved=read(E/'preservation.json')
assert len(preserved['runtime_and_live_inputs'])==139 and len(preserved['product22_paths'])==22
for p in preserved['runtime_and_live_inputs']+preserved['product22_paths']: assert current[p]==start[p]
for row in preserved['host_recordings']: assert sha(RUN/row['path'])==row['sha256']
for p,h in preserved['tools'].items(): assert sha(p)==h
corpus=read(E/'corpus-raw-clean.json')
assert len(corpus['files'])==144 and len(corpus['explicit_sha_records'])==150
for row in corpus['files']:
    p=row['path']; data=(R/p).read_bytes(); assert sha(R/p)==row['sha256']==start[p]
    blob=git('hash-object','--path='+p,'--stdin',data=data).decode().strip()
    assert blob==row['raw_git_blob']==row['clean_git_blob']
for row in corpus['explicit_sha_records']:
    root=R/('.claude' if row['tree']=='canonical' else '.agents')/'skills/do-math/scripts/tests/corpus'
    assert sha(root/row['path'])==row['sha256']
for p,h in start.items():
    if '/.t3-store/' in p or 'pseudo_tested' in p or p.endswith('/test_index.json'): assert current[p]==h
for label,needle in [('mirror-check','1336'),('skill','verified')]:
    assert read(E/(label+'.command.json'))['exit_code']==0
    assert needle in (E/(label+'.stdout')).read_text(encoding='utf-8')
long=read(E/'probe-long-observation.json'); short=read(E/'probe-short-observation.json')
assert not long['successful'] and long['calls'][0]['cwd_characters']==262 and long['calls'][0]['winerror']==267
assert short['successful'] and [v['exit_code'] for v in short['calls']]==[0,1]
assert all(v['cwd_characters']==241 and v['cwd_is_directory'] for v in short['calls'])
failure_id='boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once'
assert all_rows['canonical-t4-short'][failure_id]['outcome']=='error'
assert all(all_rows[label][failure_id]['outcome']=='passed' for label in ('canonical-t4-full','canonical-t4-full-final','mirror-t4-short'))
trace=(E/'c4/boundary-isolated-027/stderr.txt').read_text(encoding='utf-8')
assert all(v in trace for v in ('[WinError 32]','[WinError 5]','TemporaryDirectory' if 'TemporaryDirectory' in trace else 'tempfile.py'))
assert all(sha(T/p)==h for p,h in task_hashes.items())
save('verification.json',{'head':head,'source_count':len(current),'source_matches_task':True,'start_matches_016':True,
    'changes':changes,'suites':suites,'check_receipts':receipts,
    'raw':{'fixtures':len(raw['fixtures']),'snapshots':sum(x['snapshots'] for x in raw['fixtures']),
           'databases':sum(len(x['databases']) for x in raw['fixtures']),'children':len(children),'marker_checks':marker_checks,
           'mirror_limit':raw['raw_reuse_limit']},
    'baseline_files':910,'baseline_manifest_sha256':sha(B/'baseline-manifest.json'),
    'preserved_inputs':139,'products_deferred':preserved['product22_paths'],'corpus_paths':144,'explicit_sha':150,
    'host_recordings':preserved['host_recordings'],'tools':preserved['tools'],
    'job_failure':{'id':failure_id,'outcome':'error','cause':'Unconfirmed; close does not wait for termination and the fixture deletes cwd afterward.',
                   'failure_time_process_handles_observed':False},
    'path_control':{'long_cwd':262,'long_winerror':267,'short_cwd':241,'short_exit_codes':[0,1]},
    'task_artifacts_unchanged':len(task_hashes),
    'limits':['No product test rerun by manager.','Full canonical T4 remains failed; complete measurement is distinct.',
              'Prior bootstrap WinError5 cause remains unknown.','G4/G5/G6/G8, L01 and remaining semantic/document obligations remain open.']})
print(json.dumps({'source':len(current),'suites':[{k:v for k,v in s.items() if k in ('label','counts','exit_code')} for s in suites],
                  'raw_fixtures':6,'baseline_files':910,'task_bytes_unchanged':len(task_hashes)},ensure_ascii=False))
