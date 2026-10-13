"""Manager reconciliation of immutable submissions; no live product execution."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
E = RUN / 'phases/013/tasks/scheduler-smoke/evidence'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, v): (O/name).write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def command(name, argv):
    p = subprocess.run(argv, cwd=R, capture_output=True)
    (O/(name+'.stdout.log')).write_bytes(p.stdout)
    (O/(name+'.stderr.log')).write_bytes(p.stderr)
    save(name+'.json', {'argv':argv, 'cwd':str(R), 'exit_code':p.returncode})
    assert p.returncode == 0, (name, p.returncode)
command('report-check', [sys.executable, '-B', 'services/continuous-development/check.py', 'report', str(R), str(RUN), '013', 'scheduler-smoke'])
start, end = read(E/'source-start.json'), read(E/'source-final.json')
assert start == read(RUN/'phases/012/manager-evidence/source-inspected.json')
current = {p:sha(R/p) if (R/p).is_file() else None for p in end}
assert current == end
for prefix in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
    actual = {p.relative_to(R).as_posix() for p in (R/prefix).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert actual == {p for p in end if p.startswith(prefix+'/')}, prefix
save('source-inspected.json', current)
changes = {p:{'before':start.get(p), 'after':end.get(p)} for p in sorted(start.keys()|end.keys()) if start.get(p)!=end.get(p)}
report = read(E.parent/'report.json')
writes = read(RUN/'phases/013/phase.json')['tasks'][0]['writes']
assert set(changes) == {r['path'] for r in report['changes']}
assert all(any(p==w or w.endswith('/') and p.startswith(w) for w in writes) for p in changes)
suites = {}
for name in ('live-01','live-02','live-03','live-final','canonical-related','mirror-related'):
    s=read(E/name/'report.json'); c=read(E/(name+'.command.json'))
    rows=[r for g in s['reports'] for r in g['rows']]; ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids))==len(s['selected']) and set(ids)==set(s['selected'])
    expected={'error':1} if name in ('live-01','live-02','live-03') else {'passed':len(ids)}
    assert Counter(r['outcome'] for r in rows)==expected==s['counts']
    assert s['complete'] and not s['changed_during_run']
    assert s['successful']==('passed' in expected) and c['exit_code']==(0 if s['successful'] else 1)
    tree='.agents' if name.startswith('mirror') else '.claude'
    different=[p for p,h in s['source_sha256'].items() if sha(R/tree/'skills/do-math/scripts'/p)!=h]
    if s['successful']: assert not different, different
    suites[name]={'selected':len(ids),'unique_rows':len(set(ids)),'counts':s['counts'],'exit_code':c['exit_code'],'python_hashes':len(s['source_sha256']),'source_differences':different,'seconds':s['total_seconds']}
assert read(E/'canonical-related/report.json')['selected']==read(E/'mirror-related/report.json')['selected']

ns={'t':'http://schemas.microsoft.com/windows/2004/02/mit/task'}
live={}
for name in ('live-final','canonical-related','mirror-related'):
    p=next((E/name).rglob('smoke.json')); s=read(p); root=p.parent
    assert s['passed'] and len(s['checks'])==19 and all(s['checks'].values()) and s['paid_calls']==0
    assert read(root/'requests.json')==s['requests']
    owner=read(root/'ownership.json'); workspace=Path(s['workspace']); repository=Path(s['repository'])
    assert owner['initial_status']=={'operator':None,'engine':None,'wake':None}
    assert owner['names']==s['names'] and sha(workspace/'operator/HOLD.json')==owner['hold_sha256']
    assert not list(repository.iterdir()) and not (workspace/'operator/engine').exists() and not (workspace/'operator/recovery').exists()
    decoded={}
    for c in s['commands']:
        label=c['label']; raw=root/(label+'.stdout.bin'); err=root/(label+'.stderr.bin')
        assert c['exit_code']==0 and sha(raw)==c['stdout_sha256'] and sha(err)==c['stderr_sha256']
        assert read(root/(label+'.command.json'))=={k:v for k,v in c.items() if k!='label'}
        decoded[label]=json.loads(raw.read_bytes())
    assert decoded['environment']==s['environment']
    assert s['environment']['scheduler_service']=='Running' and s['environment']['interactive']
    assert decoded['freeze-confirmation']==s['freeze_confirmation']
    for mode in ('check','run-engine','wake'): assert decoded['held-'+mode]==s['held_outputs'][mode]=={'outcome':'held'}
    for obs in s['observations']:
        assert any(v=={k:x for k,x in obs.items() if k!='label'} for key,v in decoded.items() if key.startswith(obs['label']+'-'))
    for label,recording in s['recordings'].items(): assert decoded[label]==recording['value']
    freeze=s['freeze_confirmation']; manifest_path=Path(freeze['manifest']); manifest=read(manifest_path)
    assert manifest==s['manifest'] and manifest['snapshot_sha256']==freeze['snapshot_sha256']
    tree='.agents' if name.startswith('mirror') else '.claude'; scripts=R/tree/'skills/do-math/scripts'
    for f,h in manifest['files'].items():
        assert sha(manifest_path.parent/f)==h
        if name!='live-final': assert sha(scripts.parent/f)==h, f
    for v in s['executables'].values(): assert sha(Path(v['path']))==v['sha256']
    modes={'operator':'check','engine':'run-engine','wake':'wake'}
    for role,mode in modes.items():
        task=s['runs'][role]; before=s['run_bindings'][role]['before']
        assert before['last_result']==267011 and int(task['last_run_ticks'])>int(before['last_run_ticks'])
        assert task['last_result']==0 and task['state']=='Ready' and task['name']==s['names'][role]
        bootstrap=scripts/'operator_bootstrap.py' if role=='wake' else Path(freeze['entrypoint'])
        expected=f'"{bootstrap}" {mode} --repository "{repository}" --instance "{s["instance"]}" --workspace "{workspace}"'
        assert task['arguments']==expected and Path(task['cwd'])==workspace
        assert task['execute']==s['executables']['pythonw']['path']
    installed=next(v for v in s['observations'] if v['label']=='installed')['tasks']
    for role,limit in [('operator','PT1H35M'),('engine','PT0S')]:
        t=installed[role]; xml=ET.fromstring(t['xml'])
        assert xml.findtext('t:Settings/t:ExecutionTimeLimit',namespaces=ns)==limit
        assert xml.findtext('t:Settings/t:MultipleInstancesPolicy',namespaces=ns)=='IgnoreNew'
        assert xml.findtext('t:Settings/t:Hidden',namespaces=ns)=='true'
        assert t['principal_run_level']=='Limited' and t['principal_logon_type']=='Interactive'
        assert xml.findtext('t:Principals/t:Principal/t:UserId',namespaces=ns)==s['environment']['sid']
    assert ET.fromstring(installed['operator']['xml']).findtext('t:Triggers/t:TimeTrigger/t:Repetition/t:Interval',namespaces=ns)=='PT2H'
    assert len(ET.fromstring(installed['engine']['xml']).find('t:Triggers',ns))==0
    wake=ET.fromstring(s['runs']['wake']['xml'])
    trigger=datetime.fromisoformat(wake.findtext('t:Triggers/t:TimeTrigger/t:StartBoundary',namespaces=ns)).astimezone(timezone.utc)
    assert trigger==datetime.fromisoformat(s['wake_request']['WakeAt']).replace(microsecond=0)
    assert wake.findtext('t:RegistrationInfo/t:Description',namespaces=ns)==s['wake_request']['WakeKey']
    assert [r['action'] for r in s['requests']].count('start-operator')==1 and [r['action'] for r in s['requests']].count('start-engine')==1
    assert not any('start-wake' in a['argv'] for a in s['audit'])
    cleanup=s['cleanup']
    assert not cleanup['errors'] and cleanup['final_status']==decoded['absent-status']=={'operator':None,'engine':None,'wake':None}
    assert cleanup['final_observation']['tasks']==cleanup['final_status'] and cleanup['final_observation']['processes']==[]
    assert s['cancelled']['wake'] is None
    processes=[{'label':o['label'],'at':o['observed_at'],'process':v} for o in s['observations'] for v in o['processes']]
    live[name]={'checks':len(s['checks']),'commands_raw_verified':len(s['commands']),'snapshot_files':len(manifest['files']),'smoke_sha256':sha(p),'fresh_exit0_roles':list(modes),'names':s['names'],'clock_deltas':{k:v['service_timestamp_minus_request_seconds'] for k,v in s['run_bindings'].items()},'event_log_enabled':s['environment']['task_event_log_enabled'],'process_observations':processes,'cleanup_three_null':True}
for name in ('live-02','live-03'):
    s=read(next((E/name).rglob('smoke.json')))
    assert not s['passed'] and not s['cleanup']['errors'] and s['cleanup']['final_status']=={'operator':None,'engine':None,'wake':None}

tv=read(E/'verification-final.json'); old=read(RUN/'phases/012/tasks/lean-smoke/evidence/verification-final.json')
reuse=old['runtime_paths']+old['provider_inputs']+old['host_inputs']+tv['lean_inputs_preserved']
assert all(start[p]==end[p] for p in reuse)
for h in tv['host_recordings_reused']: assert sha(RUN/h['path'])==h['sha256']
for p,h in tv['lean_tool_executables_preserved'].items(): assert sha(Path(p))==h
for f in tv['old_nonmanifest_corpus_preserved']: assert start[f]==end[f]
sys.path.insert(0,str(R/'.claude/skills/do-math/scripts'))
from do_math.powershell_scheduler import PowerShellScheduler
corpus=[]
for tree in ('.claude','.agents'):
    root=R/tree/'skills/do-math/scripts/tests/corpus'; manifest=read(root/'manifest.json')
    raw_old=subprocess.check_output(['git','show','HEAD:'+tree+'/skills/do-math/scripts/tests/corpus/manifest.json'],cwd=R)
    assert hashlib.sha256(raw_old).hexdigest()==start[(root/'manifest.json').relative_to(R).as_posix()]
    assert manifest['entries'][:-2]==json.loads(raw_old)['entries'] and len(manifest['entries'])==21
    files=[p for p in root.rglob('*') if p.is_file()]; assert len(files)==62 and sum(p.stat().st_size for p in files)<5*1024*1024
    for p in files:
        rel=p.relative_to(R).as_posix()
        raw=subprocess.check_output(['git','hash-object','--no-filters',rel],cwd=R).strip()
        clean=subprocess.check_output(['git','hash-object','--path='+rel,rel],cwd=R).strip()
        assert raw==clean,rel
        assert p.read_bytes()==(R/('.agents' if tree=='.claude' else '.claude')/'skills/do-math/scripts/tests/corpus'/p.relative_to(root)).read_bytes()
        corpus.append({'path':rel,'sha256':sha(p),'git_oid':raw.decode()})
    for entry in manifest['entries']:
        for record in entry.get('recordings',[]): assert sha(root/record['path'])==record['sha256']
        for h,k in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
            if h in entry: assert sha(root/entry[k])==entry[h]
    for entry in manifest['entries'][-2:]:
        assert entry['kind']=='scheduler_json'
        original=read(R/entry['source']); label='absent-status' if entry['id'].endswith('-absent') else 'installed-status'
        rec=original['recordings'][label]; scratch=Path(original['evidence_directory'])
        assert (root/entry['path']).read_bytes()==(scratch/(label+'.stdout.bin')).read_bytes()
        assert entry['command']==rec['command']['argv'] and entry['cwd']==rec['command']['cwd']
        assert entry['returncode']==rec['command']['exit_code'] and entry['verdict']==rec['value']
        def recorded_process(argv, **kwargs):
            return subprocess.CompletedProcess(argv,entry['returncode'],(root/entry['path']).read_text(encoding='utf-8'),'')
        assert PowerShellScheduler(runner=recorded_process).run('status',entry['arguments'])==entry['verdict']
save('git-clean-observation.json',corpus)
for name in ('mirror-build','mirror-cache-build','mirror-check','skill-only','t5-list'):
    assert read(E/(name+'.command.json'))['exit_code']==0
command('mirror-check',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
assert all(sha(R/p)==h for p,h in current.items())
save('verification.json',{'result':'pass','at_utc':datetime.now(timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_count':len(current),'source_mismatches':[],'changes':changes,'suites':suites,'live':live,'corpus_raw_clean_paths':len(corpus),'runtime_preserved':len(old['runtime_paths']),'old_corpus_nonmanifest_preserved':len(tv['old_nonmanifest_corpus_preserved']),'reused_input_paths':reuse,'correction':'Live-final await-wake captured pythonw PID 9492 with the exact live bootstrap/workspace command. Canonical-related and mirror-related captured no PID. Task report broad PID absence wording is narrowed; immutable report retained.','limitations':['Only held scheduler installation/OS boundary; no research engine operation.','No OS stdout; Operational log disabled; service clock offset cause unknown.','Manager inspected original evidence and current parser without new OS task creation.','G4/G5/G6, other G7, L01 and final review remain.']})
print(json.dumps({'result':'pass','source_count':len(current),'changes':len(changes),'suites':suites,'live':live,'corpus_paths':len(corpus)},ensure_ascii=False))
