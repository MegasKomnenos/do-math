"""Promote complete observed streams; retain prior bytes and failing verdicts."""
import copy
import difflib
import hashlib
import json
from pathlib import Path
import sys
from run_command import REPO, EVIDENCE, write

scripts = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(scripts), str(scripts / 'tests')]
from do_math.claude_adapter import ADAPTERS
from unit.test_corpus_replay import _codex_stream, _claude_stream

corpus = scripts / 'tests/corpus'
manifest = json.loads((corpus / 'manifest.json').read_text(encoding='utf-8'))
original_entries = copy.deepcopy(manifest['entries'])
promotion = {'streams': [], 'surfaces': []}


def preserve(source, name):
    target = corpus / name
    if target.exists():
        raise FileExistsError(target)
    raw = source.read_bytes()
    target.write_bytes(raw)
    return {'path': name, 'sha256': hashlib.sha256(raw).hexdigest(),
            'source': source.relative_to(REPO).as_posix(), 'bytes': len(raw)}


for run in ('live-01', 'live-02'):
    for smoke_path in sorted((EVIDENCE / run).glob('smoke-isolated-*/scratch/provider-smoke-*/smoke.json')):
        smoke = json.loads(smoke_path.read_text(encoding='utf-8'))
        provider = smoke['provider']
        root = smoke_path.parent
        identifier = provider + '-maintenance-' + run + '-20261013'
        main = preserve(root / 'call/stdout.jsonl', provider + '/' + identifier + '.jsonl')
        collected = smoke['result']['execution']['collect']
        request = json.loads(collected['source_request']['raw']['text'])
        argv = ADAPTERS[provider].worker_module.build_argv(request)
        argv_sha256 = hashlib.sha256('\0'.join(argv).encode('utf-8')).hexdigest()
        assert argv_sha256 == collected['worker_status']['argv_sha256']
        entry = {'id': identifier, 'kind': provider + '_stream', 'path': main['path'],
                 'tool_version': smoke['version']['text'], 'recorded_at': smoke['started_at'],
                 'command': argv, 'command_sha256': argv_sha256,
                 'command_binding': 'Current worker.build_argv from preserved source_request; digest equals the exited worker status.',
                 'role': 'maintenance', 'source': main['source'], 'source_sha256': main['sha256'],
                 'live_passed': smoke['passed'], 'live_checks': smoke['checks'], 'model': smoke['inputs']['model'],
                 'effort': smoke['inputs']['effort'], 'host': smoke['inputs']['host'],
                 'prompt_sha256': smoke['prompt_sha256'], 'schema_sha256': smoke['schema_sha256'],
                 'scope': 'Complete native stream from one unbound maintenance role call; no research control binding or central submission.',
                 'recordings': []}
        for source_name, suffix in [('call/output.schema.json', '.schema.json'), ('call/stderr.txt', '.stderr.txt'),
                                    ('call/worker-status.json', '.worker-status.json'), ('call/input.txt', '.prompt.txt')]:
            recording = preserve(root / source_name, provider + '/' + identifier + suffix)
            entry['recordings'].append(recording)
            if suffix == '.schema.json':
                entry['schema_path'] = recording['path']
        if (root / 'selected-final.txt').exists():
            recording = preserve(root / 'selected-final.txt', provider + '/' + identifier + '.final.txt')
            entry['final_path'] = recording['path']
            entry['recordings'].append(recording)
        # The metadata records observed parser behavior. Live acceptance remains independent.
        entry['verdict'] = {'turn_failed': collected['jsonl']['turn_failed']}
        entry['verdict'] = (_codex_stream if provider == 'codex' else _claude_stream)(entry)
        if provider == 'codex':
            entry['recorded_error'] = smoke['result'].get('error')
        if run == 'live-01' and provider == 'claude':
            entry['scope'] += ' Native response/files succeeded; smoke failed because the read tool appended checkpoint JSON. Historical failure retained.'
        manifest['entries'].append(entry)
        manifest['supported_stream_versions'][provider] = smoke['version']['text']
        promotion['streams'].append({'id': identifier, 'live_passed': smoke['passed'], 'source': str(smoke_path),
                                     'worker_cli_exit': collected['worker_status']['cli_exit_code'],
                                     'command_sha256_matches': True, 'raw_bytes': main['bytes']})

for provider in ADAPTERS:
    surface = json.loads((EVIDENCE / 'surfaces' / (provider + '.json')).read_text(encoding='utf-8'))
    old = next(entry for entry in manifest['entries'] if entry['id'] == provider + '-current-command-surface')
    archived = copy.deepcopy(old)
    archived['id'] = provider + '-command-surface-20261004'
    manifest['entries'].append(archived)
    recordings = []
    diffs = []
    for index, row in enumerate(surface['recordings']):
        preserved = preserve(Path(row['path']), f'capabilities/{provider}-20261013-{index}.txt')
        recordings.append({**preserved, 'command': row['command'], 'exit_code': row['exit_code']})
        before = (corpus / archived['recordings'][index]['path']).read_bytes()
        after = Path(row['path']).read_bytes()
        diff = '\n'.join(difflib.unified_diff(before.decode('utf-8').splitlines(), after.decode('utf-8').splitlines(),
                                             fromfile=archived['recordings'][index]['path'], tofile=preserved['path']))
        (EVIDENCE / f'{provider}-surface-{index}.diff.txt').write_text(diff, encoding='utf-8')
        diffs.append({'command': row['command'], 'same_bytes': before == after,
                      'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': preserved['sha256']})
    parsed = surface['report']
    old.update(path=recordings[0]['path'], source=recordings[0]['source'], source_sha256=recordings[0]['sha256'],
               tool_version=Path(surface['recordings'][0]['path']).read_text(encoding='utf-8').strip(),
               recorded_at='2026-10-13', recordings=recordings,
               verdict={key: parsed[key] for key in ('verified', 'supported', 'scope', 'unknown', 'version_sha256', 'exec_help_sha256')})
    promotion['surfaces'].append({'provider': provider, 'archived_id': archived['id'], 'diffs': diffs,
                                  'verified': parsed['verified']})

assert all(entry in manifest['entries'] for entry in original_entries if entry['kind'] != 'cli_surface')
(corpus / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
promotion['total_corpus_bytes'] = sum(path.stat().st_size for path in corpus.rglob('*') if path.is_file())
write(EVIDENCE / 'promotion.json', promotion)
print(json.dumps(promotion, ensure_ascii=False))
