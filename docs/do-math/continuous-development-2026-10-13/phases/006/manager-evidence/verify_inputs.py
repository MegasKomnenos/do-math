"""Read-only checks of phase 006 claims against files and original command output."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = OUT.parent / 'tasks/codex-schema'
EV = TASK / 'evidence'


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run(argv):
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.run(argv, cwd=REPO, capture_output=True)
    return {'argv': argv, 'cwd': str(REPO), 'started_at': started,
            'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': p.returncode,
            'stdout': p.stdout.decode('utf-8', errors='replace'),
            'stderr': p.stderr.decode('utf-8', errors='replace')}


checked = run([sys.executable, '-B', 'services/continuous-development/check.py',
               'report', str(REPO), str(RUN), '006', 'codex-schema'])
save('report-check.json', checked)
assert checked['exit_code'] == 0, checked
start, final = read(EV / 'source-start.json'), read(EV / 'source-final.json')
previous = read(RUN / 'phases/005/tasks/corpus-git-bytes/evidence/source-final.json')
assert start == previous
mismatch = [p for p, digest in final.items() if not (REPO / p).is_file() or sha(REPO / p) != digest]
assert not mismatch, mismatch
changes = sorted(p for p in start.keys() | final.keys() if start.get(p) != final.get(p))
report = read(TASK / 'report.json')
phase = read(OUT.parent / 'phase.json')
writes = phase['tasks'][0]['writes']
assert set(changes) == {row['path'] for row in report['changes']}
assert all(any(p == w or (w.endswith('/') and p.startswith(w)) for w in writes) for p in changes)

checks = {}
for name in ('red', 'semantic', 'related-01', 'related-02', 'consumers', 'semantic-final',
             'live', 'corpus', 'mirror-corpus'):
    f = EV / name / 'report.json'
    r = read(f)
    rows = [row for group in r['reports'] for row in group['rows']]
    selected = r['selected']
    ids = [row['id'] for row in rows]
    assert len(ids) == len(set(ids)) and set(ids) == set(selected), name
    assert Counter(row['outcome'] for row in rows) == r['counts'], name
    assert r['complete'] and not r['changed_during_run'], name
    command = read(EV / (name + '-command') / 'command.json')
    assert command['state'] == 'exited'
    assert command['exit_code'] == (0 if r['successful'] else 1), name
    tree = '.agents' if name == 'mirror-corpus' else '.claude'
    prefix = f'{tree}/skills/do-math/scripts/'
    changed_since = [key for key, digest in r['source_sha256'].items()
                     if sha(REPO / (prefix + key)) != digest]
    if name in ('corpus', 'mirror-corpus'):
        assert not changed_since, changed_since
    checks[name] = {'report_sha256': sha(f), 'selected': len(selected), 'rows': len(rows),
                    'counts': r['counts'], 'exit_code': command['exit_code'],
                    'source_count': len(r['source_sha256']), 'changed_since': changed_since,
                    'failures': [row for row in rows if row['outcome'] != 'passed']}

final_audit = read(EV / 'verification-final.json')
live_before = read(EV / 'live-command/source-before.json')
runtime = final_audit['runtime_unchanged_since_live']
assert all(final[p] == live_before[p] for p in runtime)
helper = '.claude/skills/do-math/scripts/tests/support/provider_live.py'
assert final[helper] == live_before[helper]

corpus_info = {}
git_paths = []
baseline_manifest = read(EV / 'manifest-before.json')
for tree in ('.claude', '.agents'):
    root = REPO / tree / 'skills/do-math/scripts/tests/corpus'
    manifest = read(root / 'manifest.json')
    entries = manifest['entries'] if isinstance(manifest, dict) else manifest
    old = baseline_manifest['entries'] if isinstance(baseline_manifest, dict) else baseline_manifest
    current_by_id = {e['id']: e for e in entries}
    assert all(current_by_id[e['id']] == e for e in old)
    refs = []
    for e in entries:
        for path_key, hash_key in [('path', 'source_sha256'), ('schema_path', 'schema_sha256'),
                                   ('transport_schema_path', 'transport_schema_sha256')]:
            if path_key in e and hash_key in e:
                digest = sha(root / e[path_key])
                assert digest == e[hash_key], (tree, e['id'], hash_key)
                refs.append({'entry': e['id'], 'key': hash_key, 'path': e[path_key], 'sha256': digest})
        for recording in e.get('recordings', []):
            f = root / recording['path']
            assert sha(f) == recording['sha256']
            if 'bytes' in recording:
                assert f.stat().st_size == recording['bytes']
            refs.append({'entry': e['id'], 'key': 'recordings', 'path': recording['path'], 'sha256': sha(f)})
    files = sorted(p for p in root.rglob('*') if p.is_file())
    for f in files:
        rel = f.relative_to(REPO).as_posix()
        git_paths.append(rel)
        if f.name != 'manifest.json' and rel in start:
            assert sha(f) == start[rel], rel
    corpus_info[tree] = {'entries': len(entries), 'files': len(files),
                         'bytes': sum(f.stat().st_size for f in files), 'hash_references': refs,
                         'old_entries_unchanged': len(old),
                         'manifest_sha256': sha(root / 'manifest.json')}
assert corpus_info['.claude']['manifest_sha256'] == corpus_info['.agents']['manifest_sha256']
raw = run(['git', 'hash-object', '--no-filters', *git_paths])
clean = run(['git', 'hash-object', *git_paths])
assert raw['exit_code'] == clean['exit_code'] == 0
raw_ids, clean_ids = raw['stdout'].splitlines(), clean['stdout'].splitlines()
assert len(raw_ids) == len(clean_ids) == len(git_paths)
assert raw_ids == clean_ids
save('git-clean-observation.json', {'commands': [raw, clean],
     'rows': [{'path': p, 'raw': r, 'clean': c} for p, r, c in zip(git_paths, raw_ids, clean_ids)]})

promotion = read(EV / 'promotion.json')
smoke_path = Path(promotion['smoke'])
smoke = read(smoke_path)
call = smoke_path.parent / 'call'
entry = promotion['entry']
assert smoke['runner_calls'] == 1 and smoke['passed'] and len(smoke['checks']) == 11
assert all(smoke['checks'].values()) and smoke['checks'] == promotion['checks'] == entry['live_checks']
assert smoke['result']['status'] == 'completed'
assert smoke['result']['output'] == smoke['expected_output'] == entry['semantic_output']
assert (call / 'final.txt').read_bytes() == (smoke_path.parent / 'selected-final.txt').read_bytes()
final_value = json.loads((call / 'final.txt').read_bytes())
assert set(final_value) == {'output_json'} and isinstance(final_value['output_json'], str)
assert json.loads(final_value['output_json']) == smoke['expected_output']
original, transport = read(call / 'output.schema.json'), read(call / 'transport.schema.json')
description = transport['properties']['output_json']['description']
assert json.loads(description.split('original JSON Schema:\n', 1)[1]) == original
assert transport['required'] == ['output_json'] and transport['additionalProperties'] is False
assert (smoke_path.parent / 'workspace/probe-evidence.txt').read_text('utf-8') == smoke['nonce']
assert read(smoke_path.parent / 'workspace/checkpoint.json') == smoke['expected_checkpoint']
worker = read(call / 'worker-status.json')
assert worker['state'] == 'exited' and worker['cli_exit_code'] == 0
assert worker['schema_sha256'] == sha(call / 'transport.schema.json') == entry['transport_schema_sha256']
assert sha(call / 'input.txt') == entry['prompt_sha256']
assert sha(call / 'output.schema.json') == entry['schema_sha256']
snapshots = list(smoke_path.parent.glob('do-math-cli-*'))
assert len(snapshots) == 1
assert (snapshots[0] / 'schema.json').read_bytes() == (call / 'transport.schema.json').read_bytes()
assert (snapshots[0] / 'prompt.bin').read_bytes() == (call / 'input.txt').read_bytes()
for recording in entry['recordings']:
    assert sha(REPO / recording['source']) == recording['sha256']
assert sha(REPO / entry['source']) == entry['source_sha256']

reuse = read(EV / 'claude-reuse.json')
old_smoke = read(Path(reuse['original_smoke']))
old_sources = read(RUN / 'phases/003/tasks/provider-smoke/evidence/source-final.json')
assert all(final[p] == old_sources[p] for p in reuse['unchanged_modules'])
assert reuse['result_status'] == 'completed' and reuse['result_output'] == old_smoke['expected_output']
assert reuse['collection_reasons'] == [] and reuse['prompt_unchanged'] and reuse['schema_unchanged']
assert reuse['historical_cli_identity'] == {}

archive = OUT / 'pending-products.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in changes:
        z.write(REPO / p, p)
with zipfile.ZipFile(archive) as z:
    assert set(z.namelist()) == set(changes)
    assert all(hashlib.sha256(z.read(p)).hexdigest() == final[p] for p in changes)
save('product-snapshot.json', {'meaning': 'Unapproved candidate bytes, not a product commit or restoration instruction.',
     'archive': archive.name, 'archive_sha256': sha(archive),
     'files': {p: final[p] for p in changes}})
head = run(['git', 'rev-parse', 'HEAD'])
status = run(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=all'])
save('start-git-state.json', {'head': head, 'status': status})
save('verification.json', {'head': head['stdout'].strip(), 'source_count': len(final),
     'start_count': len(start), 'start_matches_phase005_end': True, 'current_mismatches': mismatch,
     'changes': changes, 'checks': checks, 'corpus': corpus_info, 'git_clean_paths': len(git_paths),
     'runtime_unchanged_since_live': runtime, 'smoke_helper_unchanged': True,
     'live': {'smoke': str(smoke_path), 'checks': smoke['checks'], 'worker': worker,
              'original_schema_sha256': sha(call / 'output.schema.json'),
              'transport_schema_sha256': sha(call / 'transport.schema.json'),
              'expected_output_matches': True, 'file_checkpoint_matches': True,
              'raw_and_snapshot_matches': True},
     'claude_reuse': {'unchanged_modules': reuse['unchanged_modules'],
                      'result_status': reuse['result_status'], 'new_calls': 0,
                      'historical_cli_identity': reuse['historical_cli_identity']}})
print(json.dumps({'source_count': len(final), 'changes': len(changes), 'git_clean_paths': len(git_paths),
                  'checks': {k: v['counts'] for k, v in checks.items()}}, ensure_ascii=False))
