from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from task_tools import REPO, RUN, HERE, snapshot, write

def read(p):
    return json.loads(p.read_bytes())

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

start = read(HERE / 'source-start.json')
current = snapshot()
write('source-final.json', current)
phase = read(RUN / 'phases/016/phase.json')
task = next(t for t in phase['tasks'] if t['id'] == 't4-fixture-repair')
changes = sorted(p for p in set(start) | set(current) if start.get(p) != current.get(p))
outside = [p for p in changes if p not in task['writes']]
assert not outside, outside
suites=[]
for label, tree in [('canonical-boundary','.claude'),('canonical-unit','.claude'),
                    ('mirror-boundary','.agents'),('mirror-unit','.agents')]:
    report=read(HERE / label / 'report.json')
    rows=[r for part in report['reports'] for r in part['rows'] if not r.get('fixture')]
    ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids)) and set(ids)==set(report['selected'])
    assert Counter(r['outcome'] for r in rows)==report['counts']
    assert report['successful'] and report['complete'] and all(r['outcome']=='passed' for r in rows)
    assert not report['changed_during_run']
    scripts=REPO / tree / 'skills/do-math/scripts'
    python={p.relative_to(scripts).as_posix():digest(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
    assert report['source_sha256']==python
    before,after=read(HERE/(label+'.source-before.json')),read(HERE/(label+'.source-after.json'))
    changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
    assert all(p.endswith(('/.timings.json','/.timings-t3.json')) for p in changed),changed
    receipt=read(HERE/(label+'.command.json'))
    assert receipt['exit_code']==0
    entry={'label':label,'selected':len(report['selected']),'unique_rows':len(ids),'counts':report['counts'],
           'fixture_counts':report['fixture_counts'],'exit_code':receipt['exit_code'],
           'successful':report['successful'],'complete':report['complete'],'python_count':len(python),
           'changed_during_run':report['changed_during_run'],'source_changes':changed,'seconds':report['total_seconds']}
    if label.endswith('boundary'):
        t4=report['t4_adapter']
        assert t4['complete'] and t4['tests_complete'] and not t4['problems']
        assert read(HERE/label/'adapter-coverage.json')==t4
        for worker in t4['workers']:
            assert worker['status']=='merged'
            directory=Path(worker['directory'])
            manifest=read(directory/'adapter-measurement.json')
            assert manifest['request']['source_sha256']==python==manifest['source_after']
            assert manifest['request']['requested']==worker['requested']
            assert manifest['request']['run_id']==t4['run_id']
            assert all(digest(directory/name)==h for name,h in manifest['artifacts'].items())
        entry['adapter']={'complete':t4['complete'],'workers':len(t4['workers']),
                          'modules':sorted(t4['modules']),'totals':t4['totals']}
        prior=read(RUN / 'phases/015/manager-evidence/verification.json')
        red=next(s['nonpassed'] for s in prior['suites'] if s['label']=='canonical-t4-final')
        exact={r['id'] for r in red if r['outcome'] in ('error','failed')}
        assert len(exact)==10 and exact<=set(ids)
        entry['exact_prior_failures_now_passed']=sorted(exact)
    suites.append(entry)
assert read(HERE/'canonical-boundary/report.json')['selected']==read(HERE/'mirror-boundary/report.json')['selected']
assert read(HERE/'canonical-unit/report.json')['selected']==read(HERE/'mirror-unit/report.json')['selected']

prior=read(RUN / 'phases/015/manager-evidence/verification.json')
previous=read(RUN / 'phases/015/manager-evidence/source-inspected.json')
reused=prior['reused_inputs']
assert all(current[p]==previous[p] for p in reused)
corpus={p:h for p,h in start.items() if '/do-math/scripts/tests/corpus/' in p}
assert len(corpus)==144 and all(current[p]==h for p,h in corpus.items())
raw_clean=[]
for relative in sorted(corpus):
    raw=(REPO/relative).read_bytes()
    a=subprocess.run(['git','hash-object','--stdin','--no-filters'],input=raw,capture_output=True,cwd=REPO,check=True)
    b=subprocess.run(['git','hash-object','--stdin','--path='+relative],input=raw,capture_output=True,cwd=REPO,check=True)
    assert a.stdout==b.stdout,relative
    raw_clean.append({'path':relative,'sha256':corpus[relative], 'raw_oid':a.stdout.decode().strip(),
                      'clean_oid':b.stdout.decode().strip()})
write('corpus-raw-clean.json',raw_clean)
tools=prior['tool_sha256_preserved']
assert all(digest(Path(p))==h for p,h in tools.items())
host=read(RUN / 'phases/015/tasks/t4-adapter-report/evidence/verification.json')['host_recordings_preserved']
assert len(host)==prior['host_recordings_preserved']
for row in host:
    assert digest(RUN/row['path'])==row['sha256']
special={p:h for p,h in start.items() if '/.t3-store/' in p or p.endswith(('/.selection-index.json','/pseudo_tested.json'))}
assert all(current[p]==h for p,h in special.items())
old_task=read(RUN/'phases/015/tasks/t4-adapter-report/report.json')
old_product=[r['path'] for r in old_task['changes'] if not r['path'].endswith(('/.timings.json','/.timings-t3.json'))]
assert len(old_product)==12 and all(current[p]==start[p] for p in old_product)
for rel in task['writes']:
    if rel.startswith('.claude') and rel.endswith(('/.timings.json','/.timings-t3.json')):
        assert (REPO/rel).read_bytes()==(REPO/rel.replace('.claude','.agents',1)).read_bytes()
out={'start_count':len(start),'final_count':len(current),'changes':changes,'outside_writes':outside,'suites':suites,
     'runtime_and_inputs_preserved':len(reused),'reused_inputs':reused,'corpus_raw_clean_count':len(raw_clean),
     'host_recordings_preserved':host,'tool_sha256_preserved':tools,'old_015_product_paths_unchanged':old_product,
     'selection_index_pseudo_and_t3_store_preserved':special,
     'limits':['Designated module regressions only, not whole T4/general/fresh T3/mutation/final review.',
               'No P10/P11 baseline comparisons or other task output consumed.',
               'Bootstrap original WinError5 cause remains unknown despite current exact-ID passes.',
               'Existing live evidence reused only for unchanged inputs, tools and previously approved properties.']}
write('verification.json',out)
print(json.dumps({'changes':changes,'suites':[{k:v for k,v in s.items() if k in ('label','selected','counts','exit_code','seconds')} for s in suites],
                  'preserved_inputs':len(reused),'corpus':len(raw_clean)},ensure_ascii=False))
