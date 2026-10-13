"""Validate and atomically publish the manager decision, then commit its exact files."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
PHASE = OUT.parent


def command(argv, *, data=None):
    return subprocess.run(argv, cwd=REPO, input=data, capture_output=True)


def record(name, argv):
    started = datetime.now(timezone.utc).isoformat()
    r = command(argv)
    d = {'argv': argv, 'cwd': str(REPO), 'started_at': started,
         'ended_at': datetime.now(timezone.utc).isoformat(), 'exit_code': r.returncode,
         'stdout': r.stdout.decode('utf-8', errors='replace'),
         'stderr': r.stderr.decode('utf-8', errors='replace')}
    (OUT / name).write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    assert r.returncode == 0, d
    return d


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nul_paths(result):
    assert result.returncode == 0
    return set(result.stdout.decode('utf-8').strip('\0').split('\0')) if result.stdout else set()


assert not (PHASE / 'manager.json').exists()
assert (PHASE / 'manager.pending.json').is_file()
reading = json.loads((OUT / 'writing-status.json').read_text('utf-8'))
assert reading['status'] in {'ready', 'completed'} and reading.get('completion_problem') is None, reading
for row in json.loads((OUT / 'reading-inputs.json').read_text('utf-8')):
    assert sha(REPO / row['path']) == row['sha256'], row['path']
sources = json.loads((PHASE / 'tasks/codex-schema/evidence/source-final.json').read_text('utf-8-sig'))
assert all(sha(REPO / path) == digest for path, digest in sources.items())
assert not nul_paths(command(['git', 'diff', '--cached', '--name-only', '-z']))
head = command(['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
assert head == '9c917b644360ebdb0d6fd0e0cc8ef3191f4956b8', head
preservation = json.loads((OUT / 'preservation.json').read_text('utf-8'))
paths = preservation['selected_files']
allowed_future = {'docs/do-math/continuous-development-2026-10-13/phases/006/manager.json',
                  'docs/do-math/continuous-development-2026-10-13/phases/006/manager-evidence/handoff-check.json'}
assert all((REPO / p).is_file() or p in allowed_future for p in paths)
for path, digest in preservation['task_evidence_sha256'].items():
    assert sha(REPO / path) == digest, path
record('memory-check.json', [sys.executable, '-B', '기억/scripts/validate_memory_index.py'])
pending_sha = sha(PHASE / 'manager.pending.json')
record('handoff-check.json', [sys.executable, '-B', 'services/continuous-development/check.py',
       'handoff', str(REPO), str(RUN), '006'])
assert sha(PHASE / 'manager.pending.json') == pending_sha
(PHASE / 'manager.pending.json').rename(PHASE / 'manager.json')

# Handoff inputs and submitted content are frozen from this point onward.
result = command(['git', 'add', '-f', '--pathspec-from-file=' + str(OUT / 'commit-paths.nul'), '--pathspec-file-nul'])
assert result.returncode == 0, result.stderr.decode('utf-8', errors='replace')
raw_paths = [p for p in paths if '/phases/006/tasks/codex-schema/' in p or '/phases/006/manager-evidence/' in p]
result = command(['git', 'hash-object', '-w', '--no-filters', '--stdin-paths'],
                 data=('\n'.join(raw_paths) + '\n').encode('utf-8'))
assert result.returncode == 0, result.stderr
objects = result.stdout.decode().splitlines()
assert len(objects) == len(raw_paths)
index_data = b''.join(('100644 ' + oid + '\t' + path).encode('utf-8') + b'\0'
                      for path, oid in zip(raw_paths, objects))
result = command(['git', 'update-index', '-z', '--index-info'], data=index_data)
assert result.returncode == 0, result.stderr
staged = nul_paths(command(['git', 'diff', '--cached', '--name-only', '-z']))
assert staged and staged <= set(paths)
assert {p for p in staged if p.startswith('기억/layer1/')} == {'기억/layer1/M-0556.md'}
assert not any(p.startswith(('.claude/', '.agents/', 'services/')) for p in staged)
index_rows = command(['git', 'ls-files', '-s', '-z']).stdout.split(b'\0')
index = {}
for row in index_rows:
    if row:
        meta, path = row.split(b'\t', 1)
        index[path.decode('utf-8')] = meta.decode().split()[1]
assert all(index[p] == oid for p, oid in zip(raw_paths, objects))
assert all(p in index for p in paths)
assert command(['git', 'rev-parse', 'HEAD']).stdout.decode().strip() == head
stage_state = command(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=no'])
(OUT / 'stage.json').write_text(json.dumps({'staged_files': sorted(staged), 'raw_objects_verified': len(raw_paths),
    'status': stage_state.stdout.decode('utf-8')}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'commit-message.txt').write_text('Codex 실호출을 검수하고 직접 소비 회귀 수리를 배정\n', encoding='utf-8')
committed = record('commit.json', ['git', 'commit', '-F', str(OUT / 'commit-message.txt')])
new_head = command(['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
committed_files = nul_paths(command(['git', 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', new_head]))
assert committed_files == staged
assert not nul_paths(command(['git', 'diff', '--cached', '--name-only', '-z']))
assert all(sha(REPO / path) == digest for path, digest in sources.items())
assert sha(PHASE / 'manager.json') == pending_sha
receipt = {'commit': new_head, 'parent': head, 'committed_files': len(committed_files),
           'raw_objects_verified': len(raw_paths), 'product_source_count': len(sources),
           'product_unchanged': True, 'manager_sha256': pending_sha, 'next': '007', 'pushed': False}
(OUT / 'post-commit.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False))
