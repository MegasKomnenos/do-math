"""Promote this single completed real call without altering historical recordings."""
import hashlib
import json
from pathlib import Path
import sys
from run_command import ROOT, EVIDENCE, write_json

sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))
from do_math.codex_worker import build_argv
from do_math.codex_stream import parse_jsonl
from do_math.provider_final import output_contract, semantic_output
from do_math.contracts import action_schema
import jsonschema

def sha(data):
    return hashlib.sha256(data).hexdigest()

smoke_path, = (EVIDENCE / 'live').rglob('smoke.json')
smoke = json.loads(smoke_path.read_bytes())
root = smoke_path.parent
call = root / 'call'
assert smoke['passed'] and smoke['runner_calls'] == 1 and all(smoke['checks'].values())
schema = json.loads((call / 'output.schema.json').read_bytes())
transport = json.loads((call / 'transport.schema.json').read_bytes())
assert schema == action_schema({'role': 'maintenance'})
assert transport == output_contract('codex', schema)
raw = (call / 'stdout.jsonl').read_bytes()
parsed = parse_jsonl(raw)
final = (root / 'selected-final.txt').read_bytes()
assert final == (call / 'final.txt').read_bytes() == parsed['final_text'].encode('utf-8')
semantic = semantic_output('codex', final)
assert semantic == smoke['expected_output'] == smoke['result']['output']
jsonschema.validate(semantic, schema)
collected = smoke['result']['execution']['collect']
request = json.loads(collected['source_request']['raw']['text'])
argv = build_argv(request)
status = json.loads((call / 'worker-status.json').read_bytes())
assert status['schema_sha256'] == sha((call / 'transport.schema.json').read_bytes())
assert status['argv_sha256'] == sha('\0'.join(argv).encode('utf-8'))
assert status['state'] == 'exited' and status['cli_exit_code'] == 0
assert Path(request['output_schema_path']).read_bytes() == (call / 'transport.schema.json').read_bytes()
assert Path(request['prompt_path']).read_bytes() == (call / 'input.txt').read_bytes()

corpus = ROOT / '.claude/skills/do-math/scripts/tests/corpus'
manifest_path = corpus / 'manifest.json'
original = manifest_path.read_bytes()
(EVIDENCE / 'manifest-before.json').write_bytes(original)
manifest = json.loads(original)
old_entries = json.loads(original)['entries']
name = 'codex-maintenance-transport-20261014'
entry = {'id': name, 'kind': 'codex_stream', 'path': 'codex/' + name + '.jsonl',
         'tool_version': smoke['version']['text'], 'recorded_at': smoke['ended_at'],
         'command': argv, 'command_sha256': status['argv_sha256'],
         'command_binding': 'Current codex_worker.build_argv from preserved source_request; digest equals exited worker status.',
         'role': 'maintenance', 'source': (call / 'stdout.jsonl').relative_to(ROOT).as_posix(),
         'source_sha256': sha(raw), 'live_passed': smoke['passed'], 'live_checks': smoke['checks'],
         'model': smoke['inputs']['model'], 'effort': smoke['inputs']['effort'], 'host': smoke['inputs']['host'],
         'reported_models': smoke['result'].get('reported_models', []),
         'prompt_sha256': smoke['prompt_sha256'], 'schema_sha256': smoke['schema_sha256'],
         'transport_schema_sha256': smoke['transport_schema_sha256'],
         'scope': 'One unbound maintenance call. schema_path is the complete semantic role contract; transport_schema_path is the Codex JSON-string envelope. Native replay and original-schema semantic receipt are separately checked.',
         'response_transport': 'codex_output_json', 'semantic_output': smoke['expected_output'], 'recordings': []}
sources = [('schema.json', call / 'output.schema.json'), ('transport.schema.json', call / 'transport.schema.json'),
           ('stderr.txt', call / 'stderr.txt'), ('worker-status.json', call / 'worker-status.json'),
           ('prompt.txt', call / 'input.txt'), ('final.txt', root / 'selected-final.txt')]
assert not (corpus / entry['path']).exists()
(corpus / entry['path']).write_bytes(raw)
for suffix, source in sources:
    rel = 'codex/' + name + '.' + suffix
    assert not (corpus / rel).exists()
    data = source.read_bytes()
    (corpus / rel).write_bytes(data)
    entry['recordings'].append({'path': rel, 'sha256': sha(data), 'bytes': len(data),
                                'source': source.relative_to(ROOT).as_posix()})
entry.update(schema_path='codex/' + name + '.schema.json',
             transport_schema_path='codex/' + name + '.transport.schema.json',
             worker_status_path='codex/' + name + '.worker-status.json', final_path='codex/' + name + '.final.txt',
             verdict={'turn_completed': parsed['turn_completed'], 'turn_failed': parsed['turn_failed'],
                      'parse_complete': parsed['parse_complete'], 'usage_fields': sorted(parsed['usage'][0]),
                      'unknown_events': [row['kind'] for row in parsed['unknown_events']],
                      'final_sha256': sha(final), 'final_is_selected_text': True})
manifest['entries'].append(entry)
assert manifest['entries'][:-1] == old_entries
text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
if b'\r\n' in original:
    text = text.replace('\n', '\r\n')
manifest_path.write_bytes(text.encode('utf-8'))
write_json(EVIDENCE / 'promotion.json', {'smoke': str(smoke_path), 'entries_before': len(old_entries),
    'entries_after': len(manifest['entries']), 'entry': entry, 'checks': smoke['checks'],
    'worker_schema_snapshot_matches': True, 'worker_prompt_snapshot_matches': True,
    'new_model_calls': 1, 'reported_cost': None, 'reported_cost_note': 'Native Codex stream reports token counters, not a price or invoice.',
    'reported_usage': smoke['result']['usage']})
print(json.dumps({'entry': name, 'recordings': len(sources) + 1, 'checks': smoke['checks']},ensure_ascii=False))
