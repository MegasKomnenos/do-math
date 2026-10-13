"""Audit preserved observations and handoff scope; exit zero is not provider success."""
from collections import Counter
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from run_command import REPO, EVIDENCE, snapshot, write
scripts = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts / 'tests')]
from do_math.claude_stream import parse_stream
from do_math.codex_stream import parse_jsonl
from do_math.contracts import action_schema, schema_reference
from do_math.engine import ResearchEngine
from do_math.provider_final import final_bytes
from support.provider_live import smoke_read_events

before = json.loads((EVIDENCE / 'initial-status/source-before.json').read_text(encoding='utf-8'))
after = snapshot()
changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
phase = json.loads((EVIDENCE.parents[2] / 'phase.json').read_text(encoding='utf-8'))
writes = phase['tasks'][0]['writes']
outside = [path for path in changed if not any(path == allowed or allowed.endswith('/') and path.startswith(allowed)
                                            for allowed in writes)]
assert not outside, outside
write(EVIDENCE / 'source-final.json', after)
schema = action_schema({'role': 'maintenance'})
# This plain branch uses no instance state; do not initialize or start a research instance.
engine_schema = ResearchEngine._response_schema(object.__new__(ResearchEngine), {'role': 'maintenance'})
assert engine_schema == schema
verification = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
                'changed_sources': changed, 'outside_writes': outside,
                'plain_engine_schema_equals_action_schema': engine_schema == schema,
                'schema_reference': schema_reference(schema), 'runs': {}, 'attempts': []}
for name in ('preparation-results', 'live-01', 'live-02', 'offline-01', 'mirror-replay'):
    path = EVIDENCE / name / 'report.json'
    report = json.loads(path.read_text(encoding='utf-8'))
    rows = [row for group in report['reports'] for row in group['rows'] if not row.get('fixture')]
    assert sorted(row['id'] for row in rows) == sorted(report['selected'])
    root = REPO / ('.agents' if name == 'mirror-replay' else '.claude') / 'skills/do-math/scripts'
    different = [key for key, digest in report['source_sha256'].items()
                 if hashlib.sha256((root / key).read_bytes()).hexdigest() != digest]
    verification['runs'][name] = {'selected_count': len(report['selected']),
        'rows': [{'id': row['id'], 'outcome': row['outcome']} for row in rows],
        'counts': dict(Counter(row['outcome'] for row in rows)), 'complete': report['complete'],
        'successful': report['successful'], 'selection_matches_rows': True,
        'changed_during_run': report['changed_during_run'], 'python_files_different_at_handoff': different,
        'total_seconds': report['total_seconds']}
assert not verification['runs']['offline-01']['python_files_different_at_handoff']
assert not verification['runs']['offline-01']['changed_during_run']

reported_cost = Decimal(0)
for path in sorted(EVIDENCE.glob('live-*/smoke-isolated-*/scratch/provider-smoke-*/smoke.json')):
    smoke = json.loads(path.read_text(encoding='utf-8'))
    root = path.parent
    provider = smoke['provider']
    collected = smoke['result']['execution']['collect']
    raw = (root / 'call/stdout.jsonl').read_bytes()
    parsed = (parse_jsonl if provider == 'codex' else parse_stream)(raw)
    native_events = [json.loads(row, parse_float=Decimal) for row in raw.splitlines()]
    assert json.loads((root / 'call/output.schema.json').read_bytes()) == schema
    assert hashlib.sha256((root / 'call/output.schema.json').read_bytes()).hexdigest() == smoke['schema_sha256']
    assert collected['worker_status']['schema_sha256'] == smoke['schema_sha256']
    assert collected['worker_status']['stdin_sha256'] == smoke['prompt_sha256']
    final = final_bytes(parsed)
    if final is not None:
        assert final == (root / 'selected-final.txt').read_bytes()
        assert final == collected['final']['raw']['text'].encode('utf-8')
        assert hashlib.sha256(final).hexdigest() == collected['final']['sha256']
        assert json.loads(final) == smoke['expected_output']
    else:
        assert collected['final']['present'] is False
    cost = sum((row.get('total_cost_usd', Decimal(0)) for row in native_events if row.get('type') == 'result'), Decimal(0))
    if provider == 'claude':
        reported_cost += cost
    verification['attempts'].append({'source': path.relative_to(REPO).as_posix(), 'provider': provider,
        'runner_calls': smoke['runner_calls'], 'passed': smoke['passed'], 'checks': smoke['checks'],
        'inputs': smoke['inputs'], 'version': smoke['version'], 'reported_models': parsed.get('reported_models'),
        'worker': smoke['result']['execution']['started'], 'worker_status': collected['worker_status'],
        'started_at': smoke['started_at'], 'ended_at': smoke['ended_at'],
        'schema_sha256': smoke['schema_sha256'], 'prompt_sha256': smoke['prompt_sha256'],
        'stdout_sha256': hashlib.sha256(raw).hexdigest(), 'stdout_bytes': len(raw),
        'final_matches_collected_artifact': final is not None,
        'termination_barrier': collected['termination_barrier'],
        'native_read_events': smoke_read_events(provider, native_events, smoke['nonce']),
        'reported_cost_usd': str(cost) if provider == 'claude' else None,
        'native_num_turns': [row.get('num_turns') for row in native_events if row.get('type') == 'result'],
        'error': smoke['result'].get('error')})
verification['runner_call_counts'] = dict(Counter(row['provider'] for row in verification['attempts']))
verification['claude_reported_cost_usd_total'] = str(reported_cost)
verification['cost_scope'] = 'Native reported list-cost only; Codex rejection has no usage/cost. CLI invocation counts do not claim internal model-request counts or actual billed amount.'
old_raw = [key for key in before if key.startswith('.claude/skills/do-math/scripts/tests/corpus/')
           and not key.endswith('manifest.json')]
verification['old_corpus_raw_changed'] = [key for key in old_raw if before[key] != after[key]]
assert not verification['old_corpus_raw_changed']
verification['mirror_help_hashes'] = {prefix: {version: after[f'{prefix}/skills/do-math/scripts/tests/corpus/capabilities/claude-{version}.txt']
        for version in ('surface-1', '20261013-1')} for prefix in ('.claude', '.agents')}
verification['preexisting_mirror_help_mismatch'] = before['.claude/skills/do-math/scripts/tests/corpus/capabilities/claude-surface-1.txt'] != before['.agents/skills/do-math/scripts/tests/corpus/capabilities/claude-surface-1.txt']
old_worker = subprocess.check_output(['git', 'show', '87fd1c1b:.claude/skills/do-math/scripts/do_math/claude_worker.py'], cwd=REPO)
current_worker = (scripts / 'do_math/claude_worker.py').read_bytes()
verification['historical_worker_only_newline_difference'] = old_worker != current_worker and old_worker.replace(b'\r\n', b'\n') == current_worker.replace(b'\r\n', b'\n')
verification['mirror_configuration_diff'] = subprocess.check_output(['git', 'diff', '--', '.agents/diff/_manifest.json', '.agents/diff/_rules.json'], cwd=REPO, text=True)
verification['final_scope'] = 'No product runtime/schema/parser edits; canonical smoke path fixed before live-02. Subsequent Python edits are only offline corpus readers/comparisons. Codex remains a schema rejection before prompt execution; no successful Codex claim. Generated mirror help recordings remain invalid pending an out-of-scope verbatim rule repair.'
write(EVIDENCE / 'verification.json', verification)
print(json.dumps({'changed': len(changed), 'outside': outside, 'schema_equal': engine_schema == schema,
                  'calls': verification['runner_call_counts'], 'offline': verification['runs']['offline-01']['counts'],
                  'mirror': verification['runs']['mirror-replay']['counts'], 'old_raw_changed': verification['old_corpus_raw_changed'],
                  'historical_worker_only_newline_difference': verification['historical_worker_only_newline_difference']}))
