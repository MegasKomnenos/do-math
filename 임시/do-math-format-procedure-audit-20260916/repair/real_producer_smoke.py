"""One real Codex call in an isolated research instance; no live research controls."""
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'full-v2/scripts'))
from do_math.engine import initialize, ResearchEngine
from do_math.repository import canonical_json

root = HERE / 'real-producer-smoke'
repo = root / 'repository'
repo.mkdir(parents=True)
subprocess.run(['git', '-C', str(repo), 'init', '-q'], check=True)
initialized = initialize(repo, workspace=root / 'work', goal_kind='research',
    goal='Verify the installed producer submission procedure with one bounded, nonmathematical maintenance execution.',
    policies='Only the assigned local checker exercise is authorized. No external actions, scholarly search or research scheduling.',
    config={'operator_enabled': False, 'scholarly_enabled': False, 'session_limits': None,
            'model': 'gpt-5.6-terra', 'effort': 'medium', 'work_calls': 1, 'operations_calls': 1,
            'call_timeout_seconds': 600, 'run_timeout_seconds': 660, 'max_output_repairs': 0})
engine = ResearchEngine(repo, initialized['instance_id'])
engine.runtime['queue'] = [{'id': 'AC-producer-smoke', 'role': 'maintenance',
    'procedure': 'Isolated submission-check acceptance exercise', 'stage': 'execute and report',
    'target': 'the supplied submission_contract command and fixed schemas',
    'reason': 'Exercise the real producer pre-submit procedure. First write .scratch/submission.json with the required report field missing and invoke the provided checker; observe the precise rejection. Then write a complete maintenance JSON with summary, used_sources, questions, report and remaining_work, create evidence.txt recording only the actual check observations, and invoke the checker again until it passes. Return exactly that final JSON value. Do not invent a check result. Use your tools to run the actual command. If tool execution fails, report that failure and stop the bounded exercise.',
    'authority': 'The local maintenance grant and this explicitly assigned temporary workspace exercise.',
    'success_conditions': ['Actual checker rejects the missing report.', 'Actual checker accepts the repaired submission.',
                           'Final response matches the checked JSON and cites evidence.txt.'],
    'next_owner': 'The outer repair validator reads the actual command events and received output.'}]
engine._save()
status = engine.run(max_steps=1)
execution = next(iter(engine.runtime['executions'].values()))
workspace = root / 'work/runs' / execution['id'] / 'workspace'
adapter = workspace.parent / 'adapter'
events = []
for file in workspace.parent.rglob('stdout.jsonl'):
    for line in file.read_text(encoding='utf-8', errors='replace').splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        item = event.get('item', {})
        if item.get('type') == 'command_execution':
            events.append(item)
output = json.loads(engine.store.read(f"runtime/artifacts/{execution['artifact_bundle']}/output.json"))
checked = json.loads((workspace / '.scratch/submission.json').read_bytes())
summary = {'instance_id': initialized['instance_id'], 'execution_id': execution['id'],
    'outcome': execution['outcome'], 'error': execution.get('error'), 'model': execution.get('model'),
    'checked_value_equals_received': checked == output, 'output_files': execution.get('output_files'),
    'command_events': events, 'engine_check': engine.check(), 'status': status}
checks = []
for event in events:
    try:
        observation = json.loads(event.get('aggregated_output', ''))
    except ValueError:
        continue
    if 'passed' in observation:
        checks.append({'exit_code': event['exit_code'], **observation})
summary['checker_observations'] = checks
(HERE / 'real-producer-smoke-result.json').write_bytes(canonical_json(summary))
print(json.dumps({key: summary[key] for key in ('instance_id', 'execution_id', 'outcome', 'error', 'model', 'checked_value_equals_received')}, ensure_ascii=False))
assert summary['outcome'] == 'output_accepted', summary['error']
assert summary['checked_value_equals_received']
assert summary['engine_check']['passed'], summary['engine_check']
assert any(row['exit_code'] == 1 and not row['passed'] and 'report' in str(row['issues']) for row in checks)
assert checks[-1]['exit_code'] == 0 and checks[-1]['passed']
assert [(x['path'], x['sha256']) for x in checks[-1]['files']] == [(x['path'], x['sha256']) for x in execution['output_files']]
