"""Inspect original phase 018 evidence without running suites or editing task files."""
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
T = RUN / 'phases/018/tasks/job-cleanup'
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

command('report-check.json', [sys.executable,'-B','services/continuous-development/check.py','report',str(R),str(RUN),'018',T.name])
head = git('rev-parse','HEAD').decode().strip()
start, end = read(E/'source-start.json'), read(E/'source-final.json')
current = {p.relative_to(R).as_posix():sha(p) for base in ('.claude/skills','.agents/skills','.agents/diff')
           for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
assert current == end and start == read(RUN/'phases/017/manager-evidence/source-inspected.json')
changes = sorted(p for p in start.keys() | end.keys() if start.get(p) != end.get(p))
report = read(T/'report.json')
assert changes == sorted(v['path'] for v in report['changes'])
assert set(changes) <= set(read(RUN/'phases/018/phase.json')['tasks'][0]['writes'])
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
suite_specs = [('canonical-exact-job','cj','.claude',{'passed':1},0),
 ('canonical-related','cr','.claude',{'passed':27},0),('mirror-related','mr','.agents',{'passed':27},0),
 ('canonical-t4-short','c4','.claude',{'passed':295},0),('mirror-t4-short','m4','.agents',{'passed':295},0)]
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
    assert all(current[p]==h for p,h in after.items() if p.startswith(tree+'/') and not p.endswith(('/.timings.json','/.timings-t3.json')))
    if '-t4-' in label: assert all(current[p]==h for p,h in after.items() if not p.endswith(('/.timings.json','/.timings-t3.json')))
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

preserved=read(E/'preservation.json')
for p in preserved['runtime_and_live_inputs']: assert current[p]==start[p]
for p in preserved['product22_paths']:
    if not p.endswith('/시험-지침.md'): assert current[p]==start[p]
for row in preserved['product22_authorized_guidance_updates']:
    assert sha(row['original_bytes_preserved_at'])==start[row['path']]==row['before_sha256']
    assert current[row['path']]==row['after_sha256']
for row in preserved['host_recordings']: assert sha(RUN/row['path'])==row['sha256']
for p,h in preserved['tools'].items(): assert sha(p)==h
corpus=read(E/'corpus-raw-clean.json')
assert len(corpus['files'])==144 and len(corpus['explicit_sha_records'])==150
for row in corpus['files']:
    p=row['path']; data=(R/p).read_bytes(); assert sha(R/p)==row['sha256']==start[p]
    assert git('hash-object','--path='+p,'--stdin',data=data).decode().strip()==row['raw_git_blob']==row['clean_git_blob']
for row in corpus['explicit_sha_records']:
    root=R/('.claude' if row['tree']=='canonical' else '.agents')/'skills/do-math/scripts/tests/corpus'
    assert sha(root/row['path'])==row['sha256']
B=RUN/'phases/016/tasks/provenance-baseline/evidence'
manifest=read(B/'baseline-manifest.json'); base=Path(manifest['extracted_scripts'])
assert read(E/'start-baseline.json')==read(E/'final-baseline.json')
assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}=={r['path'] for r in manifest['files']}
for row in manifest['files']:
    data=(base/row['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==row['sha256']
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob']
for p,h in start.items():
    if '/.t3-store/' in p or 'pseudo_tested' in p or p.endswith('/test_index.json'): assert current[p]==h
reuse=read(E/'raw-reuse-basis.json')
for p,h in reuse['unchanged_current_definitions'].items(): assert sha(R/p)==h
previous=RUN/'phases/017/tasks/t4-baseline-integration/evidence'
prior_hashes=read(E/'previous-evidence-start.json')
assert all(sha(previous/p)==h for p,h in prior_hashes.items())
assert sha(previous/'companion-manifest.json')==reuse['companion_manifest_sha256']
assert sha(B/'baseline-manifest.json')==reuse['baseline_manifest_sha256']
before=read(E/'job-observation-before2.json'); after=read(E/'job-observation-after.json')
assert before[0]['root_owned'] and before[0]['live_rmdir']['winerror']==32 and before[0]['ended_rmdir']['success']
assert [r['events'][1]['duplicate_root_wait'] for r in before[1:3]]==[258,258]
for row in after:
    assert row['root_owned'] and row['successful'] and row['directory_removed']
    assert row['events'][0]['inspection']=={'active_processes':0,'process_ids':[],'root_signaled':True}
    assert row['events'][1]['duplicate_root_wait']==0
for row in read(E/'cleanup-faults.json'):
    assert row['close_attempted'] and row['handles_closed'] and row['directory_removed']
    assert len(row['expected_errors'])==2
    assert 'ValueError' in row['expected_errors'][0] and 'ObservationFault' in row['expected_errors'][1]
for label,needle in [('mirror-check','1336'),('skill','verified')]:
    assert read(E/(label+'.command.json'))['exit_code']==0
    assert needle in (E/(label+'.stdout')).read_text(encoding='utf-8')
failure_id='boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once'
resolved=[]
for label in ('canonical-t4-short','mirror-t4-short'):
    old=read(previous/('c4' if label.startswith('canonical') else 'm4')/'report.json')
    for v in [v for g in old['reports'] for v in g['rows'] if not v.get('fixture') and v['outcome']!='passed']:
        assert all_rows[label][v['id']]['outcome']=='passed'
        resolved.append({'label':label,'id':v['id'],'prior':v['outcome'],'current':'passed'})
    assert all_rows[label][failure_id]['outcome']=='passed'
assert all(sha(T/p)==h for p,h in task_hashes.items())
save('task-hashes.json',task_hashes)
save('verification.json',{'head':head,'source_count':len(current),'source_matches_task':True,'start_matches_017':True,
 'changes':changes,'suites':suites,'check_receipts':receipts,'resolved_017':resolved,
 'baseline_files':len(manifest['files']),'preserved_inputs':len(preserved['runtime_and_live_inputs']),
 'corpus_paths':144,'explicit_sha':150,'preserved_product_paths':preserved['product22_paths'],
 'product22_unchanged':20,'guidance_updated':preserved['product22_authorized_guidance_updates'],
 'host_recordings':preserved['host_recordings'],'tools':preserved['tools'],
 'job_observations':{'before_close_not_barrier':True,'live_cwd_locked':True,'after_termination_removed':True,
  'final_states':len(after),'real_fake_fault_cases':2,'historical_race_reproduced':False},
 'raw_reuse':reuse,'previous_task_evidence_unchanged':len(prior_hashes),'task_artifacts_unchanged':len(task_hashes),
 'limits':['Manager did not rerun product suites.','Historical Job error-time state and bootstrap WinError5 cause remain unknown.',
 'G4/G5/G6/G8, L01 and remaining semantic/document obligations remain open.']})
print(json.dumps({'sources':len(current),'suites':[{k:v for k,v in s.items() if k in ('label','counts','exit_code')} for s in suites],
 'task_files_unchanged':len(task_hashes),'previous_evidence_unchanged':len(prior_hashes)},ensure_ascii=False))

