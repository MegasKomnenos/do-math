from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from difflib import unified_diff
import hashlib
import json
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = RUN / 'phases/011/tasks/regression-reading'
E = TASK / 'evidence'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def diff(a,b): return [{'path':p,'before':a.get(p),'after':b.get(p)} for p in sorted(a.keys()|b.keys()) if a.get(p)!=b.get(p)]
def run(name, argv):
    p = subprocess.run(argv,cwd=REPO,capture_output=True)
    (OUT/(name+'.stdout.log')).write_bytes(p.stdout)
    (OUT/(name+'.stderr.log')).write_bytes(p.stderr)
    save(OUT/(name+'.json'), {'argv':argv,'cwd':str(REPO),'exit_code':p.returncode})
    assert p.returncode == 0, (name,p.stderr.decode(errors='replace'))

run('report-check',[sys.executable,'-B','services/continuous-development/check.py','report',str(REPO),str(RUN),'011','regression-reading'])
report = read(TASK/'report.json')
start, end = read(E/'source-start.json'), read(E/'source-final.json')
current = {p:sha(REPO/p) if (REPO/p).is_file() else None for p in end}
assert current == end
assert start == read(RUN/'phases/010/manager-evidence/source-inspected.json')
for root in ('.claude/skills','.agents/skills','.agents/diff','services/continuous-development'):
    found = {p.relative_to(REPO).as_posix() for p in (REPO/root).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    assert found == {p for p in end if p.startswith(root+'/')}, root
changes = diff(start,end)
writes = read(RUN/'phases/011/phase.json')['tasks'][0]['writes']
assert {x['path'] for x in changes} == set(writes) == {x['path'] for x in report['changes']}
save(OUT/'source-inspected.json',current)

suites = {}
for label,tree in [('focused','.claude'),('canonical-final','.claude'),('mirror-final','.agents')]:
    r = read(E/(label+'-results/report.json'))
    execution = read(E/(label+'-execution.json'))
    rows = [x for group in r['reports'] for x in group['rows']]
    ids = [x['id'] for x in rows]
    assert len(ids) == len(set(ids)) == len(r['selected'])
    assert set(ids) == set(r['selected'])
    assert Counter(x['outcome'] for x in rows) == {'passed':len(ids)}
    assert r['counts'] == {'passed':len(ids)} and r['successful'] and r['complete']
    assert execution['exit_code'] == 0 and not r['changed_during_run']
    assert all(sha(REPO/tree/'skills/do-math/scripts'/p)==v for p,v in r['source_sha256'].items())
    actual = diff(read(E/(label+'-source-before.json')),read(E/(label+'-source-after.json')))
    assert actual == execution['changes']
    assert all(x['path']==tree+'/skills/do-math/scripts/tests/.timings.json' for x in actual)
    if label != 'focused': assert set(ids)==set(read(E/'selection.json')['selected'])
    suites[label] = {'selected':len(ids),'unique_rows':len(set(ids)),'counts':r['counts'],'exit_code':execution['exit_code'],'python_hashes':len(r['source_sha256']),'seconds':r['total_seconds']}

new = read(E/'canonical-final-results/report.json')
new_ids = set(new['selected'])
old = read(RUN/'phases/010/tasks/host-smoke/evidence/related-results/report.json')
doc = read(RUN/'phases/009/tasks/document-callable/evidence/canonical-final/results/report.json')
prefixes = ('structure.test_doc_code.','sim.test_knowledge_currentness.RecoveryMaterialTests.','sim.test_role_input_context.OperationalInputTests.','flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests.','unit.test_role_input_packaging.','unit.test_role_input_scoped_packaging.')
extra = {x for x in doc['selected'] if x.startswith(prefixes)}
assert len(old['selected'])==61 and len(extra)==75 and new_ids==set(old['selected'])|extra
failures = {}
for label in ('related-results','baseline-repro-02-results'):
    r=read(RUN/'phases/010/tasks/host-smoke/evidence'/label/'report.json')
    failed=[x for g in r['reports'] for x in g['rows'] if x['outcome']!='passed']
    assert len(failed)==2 and all(x['id'] in new_ids for x in failed)
    failures[label]=[{'id':x['id'],'before':x['outcome'],'after':'passed'} for x in failed]

task_verification=read(E/'verification-final.json')
preserved=task_verification['all_preserved_paths']
assert all(start[p]==end[p] for p in preserved)
for record in task_verification['host_recordings_reused']:
    p=RUN/record['path']; r=read(p)
    assert sha(p)==record['sha256'] and r['passed'] and all(r['checks'].values())
tools=task_verification['tool_conditions']
for name in ('python','pythonw','powershell'):
    key='powershell_sha256_now' if name=='powershell' else name+'_sha256'
    assert sha(Path(tools[name]))==tools[key]
assert tools['python_version']==sys.version
corpus=[]
for p in task_verification['corpus_unchanged']:
    raw=subprocess.check_output(['git','hash-object','--no-filters',p],cwd=REPO).strip()
    clean=subprocess.check_output(['git','hash-object','--path='+p,p],cwd=REPO).strip()
    assert raw==clean,p
    corpus.append({'path':p,'sha256':sha(REPO/p),'git_oid':raw.decode()})
save(OUT/'git-clean-observation.json',corpus)

reading=RUN/'phases/010/tasks/reading-limits/evidence'
pages=read(reading/'fixture-page-results.json')
clipped=read(reading/'fixture-capped-results.json')
reading_results=[]
for fixture,cap in zip(read(reading/'fixture-manifest.json')['fixtures'],clipped):
    p=reading/fixture['name']; assert sha(p)==fixture['sha256']
    lines=p.read_text(encoding='utf-8').splitlines(); assert lines==fixture['expected_lines']
    prefix=fixture['name'].removeprefix('fixture-').removesuffix('.txt')
    group=[page for page in pages if page['case'].startswith(prefix+'-page-')]
    received=[]
    for page in group:
        rows=page['result']['output'].splitlines()
        assert page['result']['exit_code']==0 and page['start']==len(received)+1
        assert rows==lines[page['start']-1:page['end']]
        received.extend(rows)
    assert received==lines and len(lines)==80
    missing=[i for i,line in enumerate(lines,1) if line not in cap['result']['output'].splitlines()]
    reading_results.append({'fixture':fixture['name'],'pages':len(group),'missing_first':min(missing),'missing_last':max(missing)})
assert [(r['missing_first'],r['missing_last']) for r in reading_results]==[(18,63),(16,65)]
aggregate=read(reading/'fixture-aggregate-results.json')
assert all(len(x['result']['output'].splitlines())==10 for x in aggregate['before_outer_delivery'])
assert aggregate['model_observed']['complete_ascii_line_ids']==[1,2,3]
assert aggregate['model_observed']['complete_unicode_line_ids']==[6,7,8,9,10]

actual_diff=[]
for p in ['.claude/skills/do-math/SKILL.md', '.claude/skills/do-math/scripts/tests/boundary/test_scheduling_call_jobs.py', '.claude/skills/do-math/scripts/tests/structure/test_doc_code.py', '.claude/skills/do-math/scripts/tests/sim/test_knowledge_currentness.py']:
    raw=subprocess.check_output(['git','show','HEAD:'+p],cwd=REPO)
    candidates=(raw,raw.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
    before=next(x for x in candidates if hashlib.sha256(x).hexdigest()==start[p])
    a,b=before.decode().splitlines(keepends=True),(REPO/p).read_bytes().decode().splitlines(keepends=True)
    if p.endswith('/SKILL.md'):
        assert len(a)==len(b) and [i for i,(x,y) in enumerate(zip(a,b)) if x!=y]==[13]
        assert a[13].split('긴 문서는')[0]==b[13].split('긴 문서는')[0]
    actual_diff.extend(unified_diff(a,b,fromfile='start/'+p,tofile='final/'+p))
assert ''.join(actual_diff).replace('\r\n','\n')==(E/'changes.diff').read_text(encoding='utf-8')
for operation,plan in [('mirror-build','mirror-plan'),('cache-sync','cache-plan')]:
    e=read(E/(operation+'-execution.json'))
    assert e['exit_code']==0 and e['changes']==read(E/(plan+'.json'))['changes']
run('mirror-check',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
assert all(sha(REPO/p)==v for p,v in current.items())
save(OUT/'verification.json',{'result':'pass','at_utc':datetime.now(timezone.utc).isoformat(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),'source_count':len(current),'source_mismatches':[],'changes':changes,'suites':suites,'old_failure_correspondence':failures,'runtime_preserved':124,'provider_inputs_preserved':3,'corpus_raw_clean_paths':len(corpus),'host_recordings_reused':len(task_verification['host_recordings_reused']),'reading_fixtures':reading_results,'skill_changed_lines':[14],'limitations':['No new OS T5 or paid calls; unchanged input/runtime reuse only.','PowerShell historical executable hash absent.','No G4/G5/G6 or Lean/scheduler/academic execution; no L01 certification.']})
print(json.dumps({'result':'pass','sources':len(current),'changes':len(changes),'suites':suites,'corpus_paths':len(corpus)},ensure_ascii=False))
