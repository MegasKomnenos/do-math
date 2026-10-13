from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
E = RUN / 'phases/012/tasks/lean-smoke/evidence'
def read(p): return json.loads(p.read_bytes())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def differences(a,b): return {p:{'before':a.get(p),'after':b.get(p)} for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)}
def command(name,argv):
    result=subprocess.run(argv,cwd=REPO,capture_output=True)
    (OUT/(name+'.stdout.log')).write_bytes(result.stdout)
    (OUT/(name+'.stderr.log')).write_bytes(result.stderr)
    save(OUT/(name+'.json'),{'argv':argv,'cwd':str(REPO),'exit_code':result.returncode})
    assert result.returncode==0,(name,result.stderr.decode(errors='replace'))

command('report-check',[sys.executable,'-B','services/continuous-development/check.py','report',str(REPO),str(RUN),'012','lean-smoke'])
start,end=read(E/'source-start.json'),read(E/'source-final.json')
assert start==read(RUN/'phases/011/manager-evidence/source-inspected.json')
current={p:sha(REPO/p) if (REPO/p).is_file() else None for p in end}
assert current==end,differences(end,current)
for prefix in ('.claude/skills','.agents/skills','.agents/diff','services/continuous-development'):
    actual={p.relative_to(REPO).as_posix() for p in (REPO/prefix).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
    assert actual=={p for p in end if p.startswith(prefix+'/')},prefix
save(OUT/'source-inspected.json',current)
changes=differences(start,end)
report=read(E.parent/'report.json')
writes=read(RUN/'phases/012/phase.json')['tasks'][0]['writes']
assert set(changes)=={c['path'] for c in report['changes']}
assert all(any(p==w or w.endswith('/') and p.startswith(w) for w in writes) for p in changes)
suites={}
for name in ('live-01','live-02','live-final','canonical-related','mirror-live','mirror-related'):
    r=read(E/name/'report.json'); execution=read(E/(name+'.command.json'))
    rows=[row for group in r['reports'] for row in group['rows']]
    ids=[row['id'] for row in rows]
    assert len(ids)==len(set(ids))==len(r['selected']) and set(ids)==set(r['selected'])
    expected={'error':1} if name in ('live-01','live-02') else {'passed':len(ids)}
    assert Counter(row['outcome'] for row in rows)==expected==r['counts']
    assert r['complete'] and not r['changed_during_run']
    assert r['successful']==('passed' in expected) and execution['exit_code']==(0 if r['successful'] else 1)
    tree='.agents' if name.startswith('mirror') else '.claude'
    mismatch={p:{'recorded':v,'current':sha(REPO/tree/'skills/do-math/scripts'/p)} for p,v in r['source_sha256'].items() if sha(REPO/tree/'skills/do-math/scripts'/p)!=v}
    if r['successful']: assert not mismatch,mismatch
    else: assert set(mismatch)=={'tests/support/lean_live.py','tests/unit/test_corpus_replay.py'}
    suites[name]={'selected':len(ids),'unique_rows':len(set(ids)),'counts':r['counts'],'exit_code':execution['exit_code'],'python_hashes':len(r['source_sha256']),'source_mismatches':mismatch,'seconds':r['total_seconds']}
assert read(E/'canonical-related/report.json')['selected']==read(E/'mirror-related/report.json')['selected']
for stem in ('source-canonical','source-mirror'):
    d=differences(read(E/(stem+'.json')),read(E/(stem+'-after.json')))
    assert all(p.endswith('/tests/.timings.json') for p in d)

sys.path[:0]=[str(REPO/'.claude/skills/do-math/scripts'),str(REPO/'.claude/skills/do-math/scripts/tests')]
from do_math.lean_evidence import check_file, parse_evidence
from do_math.canonical import exact_content_hash
from do_math.trust_inventory import validation_program
from support.lean_live import SOURCE, DECLARATIONS, SIGNATURES, INVALID_SOURCE
live={}
for name in ('live-final','mirror-live'):
    sp=next((E/name).rglob('smoke.json')); s=read(sp); scratch=sp.parent
    assert s['passed'] and len(s['checks'])==20 and all(s['checks'].values()) and not s['observation_errors']
    assert s['source']==SOURCE and s['declarations']==DECLARATIONS and s['extract_evidence'] is True
    assert s['installation_before']==s['installation_after']
    before,after=read(scratch/'judgment-before.json'),read(scratch/'judgment-after.json')
    assert before==after and len(before['files'])==11094
    for p,v in s['installation_before']['files'].items(): assert sha(Path(p))==v,p
    for p,v in s['identity']['executables'].items(): assert sha(Path(p))==v,p
    assert len(s['installation_before']['dependencies'])==9
    for d in s['installation_before']['dependencies']:
        assert d['exit_code']==0 and d['observed_rev']==d['manifest_rev']
        assert subprocess.check_output(['git','-C',d['directory'],'rev-parse','HEAD'],cwd=REPO,text=True).strip()==d['manifest_rev']
    v=s['validation']; source,scope=validation_program(s['identity'])
    assert v['source_text']==source and v['scope']==scope=='mathlib_import_and_representative_proofs'
    assert v['status']=='verified' and v['exit_code']==0 and sha(Path(v['source']))==v['source_sha256']
    assert read(Path(v['source']).parent/'validation.json')==v
    assert 'import Mathlib' in source and 'norm_num' in source
    assert len(s['jobs'])==5 and len(s['commands'])==5
    assert [j['request']['command'] for j in s['jobs']]==[c['command'] for c in s['commands']]
    for j in s['jobs']:
        p=Path(j['directory']); assert read(p/'request.json')==j['request'] and read(p/'observed.json')==j
        assert j['root_ended'] and j['active_processes']==0 and j['process_ids']==[]
        assert j['identity']['pid']>0 and j['identity']['creation_filetime']
        status=read(p/'status'); assert status['state']=='exited'
        assert status['exit']==(1 if j==s['invalid_job'] else 0)
    normal,invalid=s['normal'],s['invalid']
    assert normal==read(scratch/'normal.json') and invalid==read(scratch/'invalid.json')
    assert normal['status']=='verified' and normal['exit_code']==0 and normal['declaration_signatures']==SIGNATURES
    assert normal['axioms']=={d:[] for d in DECLARATIONS} and normal['signature_hash']==exact_content_hash(SIGNATURES)
    assert len(normal['dependency_evidence'])==32
    assert invalid['status']=='failed' and invalid['exit_code']==1 and invalid['reason']=='lean rejected'
    assert (scratch/'normal.lean').read_bytes()==SOURCE.encode() and (scratch/'invalid.lean').read_bytes()==INVALID_SOURCE.encode()
    p=Path(s['normal_job']['directory']); raw=(p/'out').read_bytes()
    assert (p/'compiled.lean').read_bytes()==check_file(SOURCE.encode(),DECLARATIONS,extract_evidence=True)
    base={'stdout':raw.decode(),'declaration_signatures':{},'axioms':{},'dependency_closure':{},'declaration_evidence':{}}
    parsed=parse_evidence(base,DECLARATIONS,[],extract_evidence=True)
    for k in ('status','declaration_signatures','axioms','signature_hash','dependency_closure','declaration_evidence','dependency_evidence'):
        assert parsed[k]==normal[k],k
    ip=Path(s['invalid_job']['directory'])
    assert 'type mismatch' in ((ip/'out').read_text(encoding='utf-8')+(ip/'err').read_text(encoding='utf-8')).lower()
    assert not (scratch/'workspace').exists() and s['call_executors_created']==0
    live[name]={'checks':len(s['checks']),'jobs':len(s['jobs']),'dependencies':9,'judgment_files':len(before['files']),'dependency_evidence':32,'raw_stdout_bytes':len(raw),'normal_exit':0,'invalid_exit':1,'smoke_sha256':sha(sp)}

corpus=[]
for tree in ('.claude','.agents'):
    root=REPO/tree/'skills/do-math/scripts/tests/corpus'; manifest=read(root/'manifest.json')
    old=json.loads(subprocess.check_output(['git','show','HEAD:'+tree+'/skills/do-math/scripts/tests/corpus/manifest.json'],cwd=REPO))
    assert manifest['entries'][:-1]==old['entries'] and len(manifest['entries'])==19 and len(old['entries'])==18
    files=[p for p in root.rglob('*') if p.is_file()]; assert len(files)==56 and sum(p.stat().st_size for p in files)<5*1024*1024
    for p in files:
        rel=p.relative_to(REPO).as_posix()
        raw=subprocess.check_output(['git','hash-object','--no-filters',rel],cwd=REPO).strip()
        clean=subprocess.check_output(['git','hash-object','--path='+rel,rel],cwd=REPO).strip()
        assert raw==clean,rel
        corpus.append({'path':rel,'sha256':sha(p),'git_oid':raw.decode()})
    for entry in manifest['entries']:
        for r in entry.get('recordings',[]): assert sha(root/r['path'])==r['sha256']
        for h,p in [('source_sha256','path'),('schema_sha256','schema_path'),('transport_schema_sha256','transport_schema_path')]:
            if h in entry: assert sha(root/entry[p])==entry[h]
    new=manifest['entries'][-1]; s=read(next((E/'live-final').rglob('smoke.json'))); job=Path(s['normal_job']['directory']); scratch=Path(s['evidence_directory'])
    for key,p in [('path',job/'out'),('source_path',scratch/'normal.lean'),('compiled_path',job/'compiled.lean')]: assert (root/new[key]).read_bytes()==p.read_bytes()
    for p in files: assert p.read_bytes()==(REPO/('.agents' if tree=='.claude' else '.claude')/'skills/do-math/scripts/tests/corpus'/p.relative_to(root)).read_bytes()
save(OUT/'git-clean-observation.json',corpus)
tv=read(E/'verification-final.json')
for p in tv['runtime_paths']+tv['provider_inputs']+tv['host_inputs']+tv['existing_corpus_files_unchanged']: assert start[p]==end[p]
for r in tv['host_recordings_reused']:
    p=RUN/r['path']; s=read(p); assert sha(p)==r['sha256'] and s['passed'] and all(s['checks'].values())
for r in read(E/'history-original-reports.json'): assert not Path(r['path']).is_file() and r['exists'] is False
for name in ('mirror-build','mirror-cache-build','mirror-check','skill-only','t5-list','lake-version'): assert read(E/(name+'.command.json'))['exit_code']==0
assert len(read(E/'mirror-plan-initial.json')['changed'])==11 and len(read(E/'mirror-plan-cache.json')['changed'])==1
command('mirror-check',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
assert all(sha(REPO/p)==v for p,v in current.items())
save(OUT/'verification.json',{'result':'pass','at_utc':datetime.now(timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'source_count':len(current),'source_mismatches':[],'changes':changes,'suites':suites,'live':live,'corpus_raw_clean_paths':len(corpus),'runtime_preserved':len(tv['runtime_paths']),'provider_inputs_preserved':len(tv['provider_inputs']),'host_recordings_reused':len(tv['host_recordings_reused']),'history_original_reports_absent':10,'limitations':['Lean slice only, no trust adoption or other G7 boundaries.','No new live calls by manager; original raw results and pure parser replay inspected.','No G4/G5/G6/final review or L01 certification.']})
print(json.dumps({'result':'pass','sources':len(current),'changes':len(changes),'suites':suites,'live':live,'corpus_paths':len(corpus)},ensure_ascii=False))
