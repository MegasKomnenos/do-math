import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from task_tools import ROOT, HERE, dump, snapshot

RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
sys.path[:0] = [str(ROOT/'.claude/skills/do-math/scripts'), str(ROOT/'.claude/skills/do-math/scripts/tests')]
from support.branch_gate import REASONED_EXCLUSION
import coverage

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

start = read(HERE/'source-start.json')
now = snapshot()
dump(HERE/'source-final.json',now)
changes = sorted(p for p in start.keys()|now.keys() if start.get(p) != now.get(p))
phase = read(HERE.parents[2]/'phase.json')
outside = [p for p in changes if p not in phase['tasks'][0]['writes']]
assert not outside, outside
previous = read(RUN/'phases/014/manager-evidence/source-inspected.json')
previous_verification = read(RUN/'phases/014/manager-evidence/verification.json')
reused = previous_verification['reused_inputs']
reused_mismatch = [p for p in reused if now.get(p) != previous[p]]
assert not reused_mismatch,reused_mismatch
corpus = {p:h for p,h in start.items() if '/do-math/scripts/tests/corpus/' in p}
assert all(now.get(p)==h for p,h in corpus.items())
assert all(now.get(p)==h for p,h in start.items() if p.endswith('/.selection-index.json') or p.endswith('/pseudo_tested.json'))

suites = []
for label,tree,listing in [('canonical-related-04','.claude',None),
    ('canonical-t4-final','.claude','canonical-t4-list-final'),
    ('mirror-related-final','.agents',None),('mirror-t4-full','.agents','mirror-t4-list')]:
    directory = HERE/label
    report = read(directory/'report.json')
    rows = [row for part in report['reports'] for row in part['rows'] if not row.get('fixture')]
    row_ids = [row['id'] for row in rows]
    assert len(row_ids)==len(set(row_ids)) and set(row_ids)==set(report['selected']),label
    assert Counter(row['outcome'] for row in rows)==report['counts'],label
    scripts = ROOT/tree/'skills/do-math/scripts'
    current_source = {p.relative_to(scripts).as_posix():digest(p) for p in scripts.rglob('*.py') if '__pycache__' not in p.parts}
    assert report['source_sha256']==current_source and not report['changed_during_run'],label
    before,after=read(HERE/(label+'.source-before.json')),read(HERE/(label+'.source-after.json'))
    changed_in_suite = [p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)]
    assert all(p.endswith(('/.timings.json','/.timings-t3.json')) for p in changed_in_suite),changed_in_suite
    command=read(HERE/(label+'.command.json'))
    summary={'label':label,'selected':len(report['selected']),'unique_rows':len(row_ids),
        'counts':report['counts'],'fixture_counts':report['fixture_counts'],
        'exit_code':command['exit_code'],'complete':report['complete'],'successful':report['successful'],
        'source_count':len(current_source),'changed_during_run':report['changed_during_run'],
        'seconds':report['total_seconds'],'nonpassed':[r for r in rows if r['outcome']!='passed'],
        'worker_errors':[part for part in report['reports'] if part.get('worker_error')],
        'cost_cache_changes':changed_in_suite}
    if listing:
        listed = [line.split('\t')[1] for line in (HERE/(listing+'.stdout')).read_text(encoding='utf-8').splitlines() if line.startswith('boundary\t')]
        assert listed==report['selected'],label
        t4=report['t4_adapter']
        assert read(directory/'adapter-coverage.json')==t4
        layers = next(ast.literal_eval(n.value) for n in ast.parse((scripts/'do_math/layers.py').read_text(encoding='utf-8')).body
                      if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='LAYERS' for t in n.targets))
        modules={p for p,layer in layers.items() if layer=='adapter'}
        assert set(t4['modules'])==modules
        worker_reports={part['directory']:part for part in report['reports'] if 'directory' in part}
        assert {w['directory'] for w in t4['workers']}==set(worker_reports)
        for worker in t4['workers']:
            part=worker_reports[worker['directory']]
            assert worker['requested']==part['requested']
            if worker['status']=='merged':
                worker_path=Path(worker['directory'])
                manifest=read(worker_path/'adapter-measurement.json')
                assert manifest['request']['run_id']==t4['run_id']
                assert manifest['request']['requested']==part['requested']
                assert manifest['request']['source_sha256']==current_source==manifest['source_after']
                assert all(digest(worker_path/name)==h for name,h in manifest['artifacts'].items())
                data=coverage.CoverageData(basename=str(worker_path/'coverage.data'))
                data.read(); assert data.has_arcs()
        # Re-analyse the actual parent's raw union, independent of T4 serialization.
        tracer=coverage.Coverage(data_file=str(directory/'adapter.data'),branch=True,config_file=False)
        tracer.set_option('report:exclude_lines',[REASONED_EXCLUSION])
        tracer.set_option('report:partial_branches',[])
        tracer.load()
        raw_analysis=HERE/(label+'-raw-analysis.json')
        tracer.json_report(morfs=[str(scripts/p) for p in sorted(modules)],outfile=str(raw_analysis))
        analysis=read(raw_analysis)
        analyzed={(Path.cwd()/p).resolve():entry for p,entry in analysis['files'].items()}
        for module in modules:
            entry=t4['modules'][module]
            assert entry['path']==(scripts/module).relative_to(ROOT).as_posix()
            assert entry['source_sha256']==current_source[module]
            for key in ('executed_lines','missing_lines','excluded_lines','executed_branches','missing_branches','summary'):
                assert entry[key]==analyzed[(scripts/module).resolve()][key],(label,module,key)
        assert t4['totals']==analysis['totals']
        assert not any(key in report for key in ('branch_gate','selection_index','mutation','t3_store'))
        summary['adapter']={'complete':t4['complete'],'problems':t4['problems'],'workers':len(t4['workers']),
            'worker_statuses':dict(Counter(w['status'] for w in t4['workers'])),'tests_complete':t4['tests_complete'],
            'totals':t4['totals'],'modules':{p:{'sha256':entry['source_sha256'],'summary':entry['summary']} for p,entry in t4['modules'].items()}}
    suites.append(summary)

old_task=read(RUN/'phases/014/tasks/scholarly-smoke/evidence/verification-final.json')
host=[]
for row in old_task['host_recordings_reused']:
    path=RUN/row['path']; actual=digest(path)
    assert actual==row['sha256']
    host.append({'path':row['path'],'sha256':actual})
tool_conditions=old_task['host_tool_conditions']
tools={tool_conditions['python']:tool_conditions['python_sha256'],
       tool_conditions['pythonw']:tool_conditions['pythonw_sha256'],
       tool_conditions['powershell']:tool_conditions['powershell_sha256_now'],
       **old_task['lean_tool_executables_preserved']}
assert all(digest(Path(p))==h for p,h in tools.items())

out={'source_start_count':len(start),'source_final_count':len(now),'changes':changes,'outside_writes':outside,
     'suites':suites,'runtime_and_inputs_preserved':len(reused),'reused_inputs':reused,
     'corpus_paths_preserved':len(corpus),'host_recordings_preserved':host,'tool_sha256_preserved':tools,
     'selection_index_and_pseudo_list_preserved':True,
     'limitations':['T4 adapter reach is informational; no threshold was introduced.',
          'No general whole run, fresh whole T3, whole mutation or new paid/scheduler/scholarly smoke call.',
          'Existing smoke reuse is limited to previously approved properties and unchanged inputs/tools.',
          'Historical PowerShell binary identity before phase014 was not recorded.']}
dump(HERE/'verification.json',out)
print(json.dumps({'changes':changes,'suites':[{k:v for k,v in s.items() if k in ('label','selected','counts','exit_code','complete','successful')} for s in suites],
                 'runtime_and_inputs_preserved':len(reused),'corpus_preserved':len(corpus)},ensure_ascii=False))
