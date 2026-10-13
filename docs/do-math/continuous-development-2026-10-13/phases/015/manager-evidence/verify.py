"""Manager rechecks preserved files without rewriting task evidence or running suites."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent
T = RUN / 'phases/015/tasks/t4-adapter-report'
E = T / 'evidence'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value): (O/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def command(name, args):
    p = subprocess.run(args, cwd=R, capture_output=True)
    row = {'argv':args, 'cwd':str(R), 'exit_code':p.returncode,
           'stdout':p.stdout.decode('utf-8', errors='replace'), 'stderr':p.stderr.decode('utf-8', errors='replace')}
    save(name, row)
    assert p.returncode == 0, row
    return row

command('report-check.json', [sys.executable, '-B', 'services/continuous-development/check.py', 'report', str(R), str(RUN), '015', 't4-adapter-report'])
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R).decode().strip()
before, end = read(E/'source-start.json'), read(E/'source-final.json')
current = {p.relative_to(R).as_posix():sha(p) for base in ('.claude/skills','.agents/skills','.agents/diff')
           for p in (R/base).rglob('*') if p.is_file() and '__pycache__' not in p.parts and '.t3-store' not in p.parts}
assert current == end
previous = read(RUN/'phases/014/manager-evidence/source-inspected.json')
assert all(before[p] == previous[p] for p in before)
changes = sorted(p for p in before.keys()|end.keys() if before.get(p) != end.get(p))
report = read(T/'report.json')
assert changes == sorted(c['path'] for c in report['changes'])
allowed = read(RUN/'phases/015/phase.json')['tasks'][0]['writes']
assert all(p in allowed for p in changes)
save('source-inspected.json', current)

sys.path.insert(0, str(R/'.claude/skills/do-math/scripts/tests'))
from support.branch_gate import REASONED_EXCLUSION
import coverage

suites = []
for label, tree, listing in [('canonical-related-04','.claude',None),('mirror-related-final','.agents',None),
                             ('canonical-t4-final','.claude','canonical-t4-list-final'),('mirror-t4-full','.agents','mirror-t4-list')]:
    d = E/label
    r = read(d/'report.json')
    rows = [v for part in r['reports'] for v in part['rows'] if not v.get('fixture')]
    ids = [v['id'] for v in rows]
    assert len(ids) == len(set(ids)) and set(ids) == set(r['selected'])
    assert dict(Counter(v['outcome'] for v in rows)) == r['counts']
    scripts = R/tree/'skills/do-math/scripts'
    source = {p.relative_to(scripts).as_posix():sha(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
    assert source == r['source_sha256'] and r['changed_during_run'] == []
    sb, sa = read(E/(label+'.source-before.json')), read(E/(label+'.source-after.json'))
    changed = [p for p in sb.keys()|sa.keys() if sb.get(p)!=sa.get(p)]
    assert all(p.endswith(('/.timings.json','/.timings-t3.json')) for p in changed)
    receipt = read(E/(label+'.command.json'))
    assert receipt['exit_code'] == (1 if listing else 0)
    item = {'label':label,'selected':len(ids),'counts':r['counts'],'complete':r['complete'],
            'successful':r['successful'],'exit_code':receipt['exit_code'],'python_files':len(source),
            'nonpassed':[v for v in rows if v['outcome']!='passed'],'source_changes':changed}
    if listing:
        population = [line.split('\t')[1] for line in (E/(listing+'.stdout')).read_text(encoding='utf-8').splitlines() if line.startswith('boundary\t')]
        assert population == r['selected']
        t4 = read(d/'adapter-coverage.json')
        assert t4 == r['t4_adapter']
        layers = next(ast.literal_eval(n.value) for n in ast.parse((scripts/'do_math/layers.py').read_text(encoding='utf-8')).body
                      if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LAYERS' for t in n.targets))
        modules = {p for p, layer in layers.items() if layer=='adapter'}
        assert set(t4['modules']) == modules
        workers = {part['directory']:part for part in r['reports'] if 'directory' in part}
        assert {w['directory'] for w in t4['workers']} == set(workers)
        for w in t4['workers']:
            wd = Path(w['directory']); publication = read(wd/'adapter-measurement.json')
            assert w['status']=='merged' and w['requested']==workers[str(wd)]['requested']
            assert publication['request']=={'kind':'t4','run_id':t4['run_id'],'source_sha256':source,'requested':w['requested']}
            assert publication['source_after']==source
            assert set(publication['artifacts'])=={'coverage.data','opened.json','entered.json'}
            assert all(sha(wd/name)==h for name,h in publication['artifacts'].items())
            cd=coverage.CoverageData(basename=str(wd/'coverage.data')); cd.read(); assert cd.has_arcs()
        tracer=coverage.Coverage(data_file=str(d/'adapter.data'),branch=True,config_file=False)
        tracer.set_option('report:exclude_lines',[REASONED_EXCLUSION]); tracer.set_option('report:partial_branches',[]); tracer.load()
        output=O/(label+'-raw-analysis.json')
        tracer.json_report(morfs=[str(scripts/p) for p in sorted(modules)],outfile=str(output))
        analysis=read(output); files={(Path.cwd()/p).resolve():v for p,v in analysis['files'].items()}
        for module in modules:
            entry=t4['modules'][module]
            assert entry['source_sha256']==source[module]
            for key in ('executed_lines','missing_lines','excluded_lines','executed_branches','missing_branches','summary'):
                assert entry[key]==files[(scripts/module).resolve()][key],(label,module,key)
        assert t4['totals']==analysis['totals']
        assert not any(k in r for k in ('branch_gate','selection_index','t3_store','mutation'))
        item['adapter']={'complete':t4['complete'],'workers':len(workers),'modules':sorted(modules),'totals':t4['totals'],'problems':t4['problems']}
    suites.append(item)

task_verify=read(E/'verification.json')
assert all(current[p]==previous[p] for p in task_verify['reused_inputs'])
corpus={p:h for p,h in before.items() if '/do-math/scripts/tests/corpus/' in p}
assert all(current[p]==h for p,h in corpus.items())
assert all(current[p]==h for p,h in before.items() if p.endswith(('/.selection-index.json','/pseudo_tested.json')))
for row in task_verify['host_recordings_preserved']: assert sha(RUN/row['path'])==row['sha256']
for p,h in task_verify['tool_sha256_preserved'].items(): assert sha(Path(p))==h
for p in corpus:
    raw=(R/p).read_bytes()
    a=subprocess.check_output(['git','hash-object','--no-filters','--stdin'],cwd=R,input=raw)
    b=subprocess.check_output(['git','hash-object','--path='+p,'--stdin'],cwd=R,input=raw)
    assert a==b,p
receipts=[]
for check in report['checks']:
    refs=[r for r in check['evidence'] if r.endswith('.command.json')]
    if refs:
        receipt=read(RUN/refs[0][4:]); assert receipt['exit_code']==check['exit_code']
        receipts.append({'path':refs[0],'exit_code':receipt['exit_code'],'reported_result':check['result']})
command('mirror-check.json',[sys.executable,'-B','.claude/skills/writing-skills/scripts/build_skill_mirrors.py','--check'])
command('skill-only.json',[sys.executable,'-B','.claude/skills/do-math/scripts/probe_cli.py','--skill-only'])
save('verification.json',{'head':head,'source_start_count':len(before),'source_final_count':len(current),'current_matches_task':True,
     'changes':changes,'suites':suites,'runtime_and_inputs_preserved':len(task_verify['reused_inputs']),
     'reused_inputs':task_verify['reused_inputs'],'corpus_raw_clean_paths':len(corpus),'host_recordings_preserved':8,
     'tool_sha256_preserved':task_verify['tool_sha256_preserved'],'check_receipts':receipts,
     'limits':['No product test suites rerun by manager. Existing raw results are rechecked.',
               'OS causes remain unresolved; complete measurement does not certify failed or skipped tests.',
               'Final G4/G5/G6/G8 and remaining G1/G2/G3/G7 requirements remain open.']})
print(json.dumps({'source':len(current),'changes':len(changes),'suites':[{k:v for k,v in s.items() if k in ('label','selected','counts','exit_code')} for s in suites]},ensure_ascii=False))
