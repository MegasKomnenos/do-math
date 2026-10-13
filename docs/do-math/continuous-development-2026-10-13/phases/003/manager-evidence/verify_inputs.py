"""Read-only manager checks against the task's preserved reports and bytes."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(r'C:\math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).parent
EVIDENCE = RUN / 'phases/003/tasks/provider-smoke/evidence'


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    path = Path(path)
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


report = read(EVIDENCE.parent / 'report.json')
task = read(RUN / 'phases/003/phase.json')['tasks'][0]
command = [sys.executable, '-B', str(REPO / 'services/continuous-development/check.py'),
           'report', str(REPO), str(RUN), '003', 'provider-smoke']
checked = subprocess.run(command, cwd=REPO, capture_output=True)
(OUT / 'report-check.stdout.txt').write_bytes(checked.stdout)
(OUT / 'report-check.stderr.txt').write_bytes(checked.stderr)
before = read(EVIDENCE / 'initial-status/source-before.json')
after = read(EVIDENCE / 'source-final.json')
changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
mismatch = [k for k, v in after.items() if sha(REPO / k) != v]
outside = [p for p in changed if not any(p == w or w.endswith('/') and p.startswith(w) for w in task['writes'])]
result = {
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
    'report_check': {'argv': command, 'exit_code': checked.returncode},
    'source_files_checked': len(after), 'current_source_mismatches': mismatch,
    'task_changed_files': changed, 'outside_writes': outside,
    'changes_match_report': changed == sorted(c['path'] for c in report['changes']),
    'runs': {}, 'attempts': [],
}
for name, command_dir, expected in [
    ('live-01', 'live-01-command', (2, {'failed': 2}, 1, False)),
    ('live-02', 'live-02-command', (1, {'passed': 1}, 0, True)),
    ('offline-01', 'offline-01-command', (23, {'passed': 23}, 0, True)),
    ('mirror-replay', 'mirror-replay-command', (4, {'passed': 2, 'failed': 2}, 1, False)),
]:
    data = read(EVIDENCE / name / 'report.json')
    process = read(EVIDENCE / command_dir / 'command.json')
    rows = [r for g in data['reports'] for r in g['rows']]
    root = REPO / ('.agents' if name == 'mirror-replay' else '.claude') / 'skills/do-math/scripts'
    run = {
        'selected': len(data['selected']), 'rows': len(rows),
        'selection_matches_rows': Counter(data['selected']) == Counter(r['id'] for r in rows),
        'unique_rows': len(rows) == len({r['id'] for r in rows}),
        'counts': dict(Counter(r['outcome'] for r in rows)),
        'complete': data['complete'], 'successful': data['successful'],
        'exit_code': process['exit_code'], 'pid': process['pid'],
        'started_at': process['started_at'], 'ended_at': process['ended_at'],
        'changed_during_run': data['changed_during_run'],
        'python_hash_count': len(data['source_sha256']),
        'python_changes_since_run': [p for p, h in data['source_sha256'].items() if sha(root / p) != h],
        'report_sha256': sha(EVIDENCE / name / 'report.json'),
    }
    run['matches_expected_observation'] = (
        (run['selected'], run['counts'], run['exit_code'], run['successful']) == expected
        and run['complete'] and run['selection_matches_rows'] and run['unique_rows']
        and not run['changed_during_run'])
    result['runs'][name] = run

sys.path.insert(0, str(REPO / '.claude/skills/do-math/scripts'))
from do_math.contracts import action_schema

current_schema = action_schema({'role': 'maintenance'})
observed = read(EVIDENCE / 'verification.json')
for recorded in observed['attempts']:
    data = read(REPO / recorded['source'])
    root = Path(data['evidence_directory'])
    call = root / 'call'
    status = read(call / 'worker-status.json')
    collected = data['result']['execution']['collect']
    events = [json.loads(line) for line in (call / 'stdout.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    item = {
        'provider': data['provider'], 'source': recorded['source'], 'runner_calls': data['runner_calls'],
        'passed': data['passed'], 'checks': data['checks'],
        'schema_matches_current': read(call / 'output.schema.json') == current_schema,
        'worker_schema_hash_matches': status['schema_sha256'] == sha(call / 'output.schema.json'),
        'prompt_hash_matches': status['stdin_sha256'] == sha(call / 'input.txt') == data['prompt_sha256'],
        'stdout_hash_matches': sha(call / 'stdout.jsonl') == recorded['stdout_sha256'],
        'worker_exit_code': status['cli_exit_code'], 'worker_state': status['state'],
        'termination_barrier': collected['termination_barrier'],
        'parse_complete': collected['jsonl']['parse_complete'],
        'turn_failed': collected['jsonl']['turn_failed'],
        'nonce_file_matches': (root / 'workspace/probe-evidence.txt').is_file()
            and (root / 'workspace/probe-evidence.txt').read_bytes() == data['nonce'].encode(),
        'checkpoint_json_matches': (root / 'workspace/checkpoint.json').is_file()
            and read(root / 'workspace/checkpoint.json') == data['expected_checkpoint'],
        'selected_final_matches': (root / 'selected-final.txt').is_file()
            and read(root / 'selected-final.txt') == data['expected_output'],
    }
    if data['provider'] == 'codex':
        item['error_messages'] = [e.get('message', e.get('error', {}).get('message')) for e in events if e.get('type') in ('error', 'turn.failed')]
        item['schema_rejection_confirmed'] = all('invalid_json_schema' in s and 'integration_bundles' in s for s in item['error_messages']) and len(item['error_messages']) == 2
    else:
        observed_reads = []
        bash_ids = set()
        for event in events:
            for block in event.get('message', {}).get('content', []):
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use' and block.get('name') == 'Bash':
                    bash_ids.add(block['id'])
                if block.get('type') == 'tool_result' and block.get('tool_use_id') in bash_ids and not block.get('is_error'):
                    try:
                        if json.loads(block.get('content', '')) == {'read_nonce': data['nonce']}:
                            observed_reads.append(block['tool_use_id'])
                    except (ValueError, TypeError):
                        pass
        item['matching_bash_read_results'] = observed_reads
    result['attempts'].append(item)

corpus = REPO / '.claude/skills/do-math/scripts/tests/corpus'
mirror = REPO / '.agents/skills/do-math/scripts/tests/corpus'
manifest = read(corpus / 'manifest.json')
corpus_files = [p for p in corpus.rglob('*') if p.is_file()]
result['corpus'] = {
    'entry_count': len(manifest['entries']), 'file_count': len(corpus_files),
    'bytes': sum(p.stat().st_size for p in corpus_files),
    'old_raw_changes': [p for p in before if '/tests/corpus/' in p and not p.endswith('/manifest.json') and before[p] != after.get(p)],
    'mirror_byte_differences': [p.relative_to(corpus).as_posix() for p in corpus_files if sha(p) != sha(mirror / p.relative_to(corpus))],
    'claude_help_hashes': {runtime: {name: sha(root / 'capabilities' / name) for name in ['claude-surface-1.txt', 'claude-20261013-1.txt']}
                          for runtime, root in [('canonical', corpus), ('mirror', mirror)]},
}
history = read(EVIDENCE / 'background-reuse-review.json')
historical_root = EVIDENCE / 'historical-background-source'
historical_report = read(historical_root / 'report.json')
history_events = [json.loads(s) for s in (historical_root / 'evidence/stdout.jsonl').read_text(encoding='utf-8').splitlines() if s.strip()]
started = [(i, e) for i, e in enumerate(history_events) if e.get('subtype') == 'task_started']
ended = [(i, e) for i, e in enumerate(history_events) if e.get('subtype') == 'task_notification' and e.get('status') == 'completed']
finals = [(i, e) for i, e in enumerate(history_events) if e.get('type') == 'result' and not e.get('is_error')]
identity = any(i < j < k and a.get('task_type') == 'local_bash' and a.get('is_backgrounded') is True
               and a.get('task_id') == b.get('task_id') and a.get('tool_use_id') == b.get('tool_use_id')
               for i, a in started for j, b in ended for k, _ in finals)
result['background'] = {
    'all_preserved_hashes_match': all(sha(historical_root / p) == v['sha256'] for p, v in history['files'].items()),
    'native_identity_and_order': identity,
    'historical_passed': historical_report['passed'],
    'historical_actual_wait_tool': historical_report['checks']['actual_wait_tool'],
    'termination_barrier': historical_report['result']['execution']['collect']['termination_barrier'],
    'file_matches_selected_nonce': (historical_root / 'workspace/completed.txt').read_text(encoding='utf-8').strip()
        == historical_report['result']['output']['nonce'],
    'current_source_hashes_match': all(sha(REPO / '.claude/skills/do-math/scripts' / p) == d['current_sha256'] for p, d in history['current_sources'].items()),
}
for name in ('context.md', 'plan.md', 'seams.md'):
    # Small transient input snapshots used only to produce the manager's edit diff.
    (OUT / (name + '.before')).write_bytes((RUN / name).read_bytes())
result['verification_passed'] = (
    checked.returncode == 0 and not mismatch and not outside and result['changes_match_report']
    and all(r['matches_expected_observation'] for r in result['runs'].values())
    and not result['runs']['offline-01']['python_changes_since_run']
    and not result['runs']['mirror-replay']['python_changes_since_run']
    and all(a['schema_matches_current'] and a['worker_schema_hash_matches'] and a['prompt_hash_matches']
            and a['stdout_hash_matches'] and a['termination_barrier']['confirmed'] for a in result['attempts'])
    and result['background']['all_preserved_hashes_match'] and identity
    and result['background']['file_matches_selected_nonce'] and result['background']['current_source_hashes_match'])
save('verification.json', result)
print(json.dumps({k: result[k] for k in ['head', 'source_files_checked', 'current_source_mismatches', 'outside_writes', 'verification_passed']}, ensure_ascii=False))
print('Runs:', {k: (v['selected'], v['counts'], v['exit_code']) for k, v in result['runs'].items()})
print('Corpus:', result['corpus'])
sys.exit(0 if result['verification_passed'] else 1)
