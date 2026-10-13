import hashlib
import json
from pathlib import Path
import sys

REPO = Path('C:/math')
OUT = Path(__file__).parent
SCRIPTS = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from do_math.codex_stream import parse_jsonl
from support.scholarly_live import list_sources_observation

smoke_path = next((OUT / 'live-final').rglob('smoke.json'))
smoke = json.loads(smoke_path.read_bytes())
assert smoke['passed'] and smoke['runner_calls'] == 1 and all(smoke['checks'].values())
root = smoke_path.parent
call = root / 'files/evidence'
corpus = SCRIPTS / 'tests/corpus'
manifest_path = corpus / 'manifest.json'
manifest_raw = manifest_path.read_bytes()
manifest = json.loads(manifest_raw)
(OUT / 'manifest-before.json').write_bytes(manifest_raw)
assert len(manifest['entries']) == 21
stem = 'scholarly/codex-list-sources-20261014'
files = {'path': (call / 'stdout.jsonl', '.jsonl'), 'final_path': (call / 'final.txt', '.final.txt'),
         'schema_path': (call / 'output.schema.json', '.schema.json'),
         'transport_schema_path': (call / 'transport.schema.json', '.transport.schema.json'),
         'worker_status_path': (call / 'worker-status.json', '.worker-status.json'),
         'registry_path': (root / 'registry.stdout.json', '.registry.json'),
         'request_path': (Path(smoke['worker_snapshot']['path']), '.request.json'),
         'prompt_path': (call / 'input.txt', '.prompt.txt'),
         'stderr_path': (call / 'stderr.txt', '.stderr.txt'),
         'version_path': (root / 'version.stdout.txt', '.version.txt')}
recordings = []
paths = {}
for field, (source, suffix) in files.items():
    path = stem + suffix
    raw = source.read_bytes()
    dest = corpus / path
    assert not dest.exists()
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(raw)
    paths[field] = path
    recordings.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(),
                       'source': source.relative_to(REPO).as_posix(), 'bytes': len(raw), 'transformation': 'none; exact original bytes'})
raw = (call / 'stdout.jsonl').read_bytes()
registry = json.loads((root / 'registry.stdout.json').read_bytes())
observation = list_sources_observation(raw, registry['sources'])
# Expected list identity is independently derived from the installed registry,
# and native tool ID is checked directly in the original event, not copied from
# the observer alone. Source.summary equality was checked in the live smoke.
events = [json.loads(line) for line in raw.splitlines() if line.strip()]
tool = next(e['item'] for e in events if e['type'] == 'item.completed' and e.get('item', {}).get('type') == 'mcp_tool_call')
assert tool['server'] == 'scholarly' and tool['tool'] == 'list_sources' and tool['status'] == 'completed' and tool['error'] is None
assert observation['sources'] == registry['sources']
entry = {'id': 'codex-scholarly-list-sources-20261014', 'kind': 'scholarly_stream', **paths,
         'source_sha256': hashlib.sha256(raw).hexdigest(), 'tool_version': smoke['version']['text'],
         'recorded_at': smoke['started_at'], 'ended_at': smoke['ended_at'],
         'command': smoke['worker_snapshot']['argv'], 'command_sha256': hashlib.sha256('\0'.join(smoke['worker_snapshot']['argv']).encode()).hexdigest(),
         'role': 'protocol_probe', 'source': smoke_path.relative_to(REPO).as_posix(), 'live_passed': True,
         'cli_exit_code': 0, 'server': smoke['server'], 'cli_identity': smoke['cli_identity'],
         'server_python': smoke['server_python'], 'configuration_source': smoke['configuration_source'],
         'server_packages': registry['packages'], 'server_python_version': registry['python'],
         'server_source_sha256': registry['source_sha256'],
         'initialization_observation': smoke['initialization'],
         'verdict': {'turn_completed': True, 'turn_failed': False, 'parse_complete': True,
                     'tool_id': tool['id'], 'server': 'scholarly', 'tool': 'list_sources', 'status': 'ok',
                     'source_ids': sorted(source['id'] for source in registry['sources']),
                     'structured_content_present': tool['result'].get('structured_content') is not None},
         'recordings': [{k: row[k] for k in ('path', 'sha256')} for row in recordings],
         'scope': 'Complete native stdout/stderr and safe original request/schema/prompt/final/status; registry summary snapshot is a dated observation, not a second source contract. No environment/authentication dump. No search/fetch evidence.'}
manifest['entries'].append(entry)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'promotion.json').write_text(json.dumps({'entry_id': entry['id'], 'recordings': recordings,
    'raw_stream_sha256': entry['source_sha256'], 'independent_expected_source': 'installed registry.Source.summary via actual server Python',
    'initial_failures': ['live-01 error: report bytes serialization', 'live-02 failed: nonexistent lazy artifact directory assertion'],
    'actual_calls': 3, 'promotion': 'Only live-final is promoted as a passed recording; earlier reports/raw files remain unchanged.'}, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'entry': entry['id'], 'files': len(recordings), 'bytes': sum(row['bytes'] for row in recordings), 'sources': len(registry['sources'])}))
