"""Publish checked manager input, then commit only the reviewed file set."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
PHASE = OUT.parent

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def cmd(argv, payload=None):
    return subprocess.run(argv, cwd=ROOT, input=payload, capture_output=True)

def record(name, argv):
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    row = dict(argv=argv, cwd=str(ROOT), pid=p.pid, started_at=started,
               ended_at=datetime.now(timezone.utc).isoformat(), exit_code=p.returncode,
               stdout=stdout.decode('utf-8', errors='replace'), stderr=stderr.decode('utf-8', errors='replace'))
    (OUT / name).write_text(json.dumps(row, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    assert p.returncode == 0, row
    return row

def paths(result):
    assert result.returncode == 0, result.stderr
    return set(result.stdout.decode('utf-8').rstrip('\0').split('\0')) if result.stdout else set()

assert not (PHASE / 'manager.json').exists()
assert (PHASE / 'manager.pending.json').is_file()
status = read(OUT / 'writing-status.json')
assert status['status'] in {'ready', 'completed'} and status.get('completion_problem') is None
for p,h in read(OUT / 'reading-inputs.json').items():
    assert sha(ROOT / p) == h, p
sources = read(PHASE / 'tasks/provider-consumers/evidence/source-final.json')
operator = read(OUT / 'verification.json')['current_differences']
for p,h in sources.items():
    expected = operator[p]['current'] if p in operator else h
    assert sha(ROOT / p) == expected, p
assert not paths(cmd(['git', 'diff', '--cached', '--name-only', '-z']))
head = cmd(['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
assert head == '61f9e06fc15fb49ef30bf7d93c83c92e275eebad'
preservation = read(OUT / 'preservation.json')
selected = preservation['selected_files']
future = {p.relative_to(ROOT).as_posix() for p in (PHASE/'manager.json', OUT/'handoff-check.json', OUT/'memory-check.json')}
assert all((ROOT / p).is_file() or p in future for p in selected)
for p,h in preservation['task_evidence_sha256'].items():
    assert sha(ROOT / p) == h
record('memory-check.json', [sys.executable, '-B', '기억/scripts/validate_memory_index.py'])
pending_sha = sha(PHASE / 'manager.pending.json')
record('handoff-check.json', [sys.executable, '-B', 'services/continuous-development/check.py', 'handoff', str(ROOT), str(RUN), '007'])
assert sha(PHASE / 'manager.pending.json') == pending_sha
(PHASE / 'manager.pending.json').rename(PHASE / 'manager.json')

# Do not change any submitted handoff content after this publication.
result = cmd(['git', 'add', '-f', '--pathspec-from-file='+str(OUT / 'commit-paths.nul'), '--pathspec-file-nul'])
assert result.returncode == 0, result.stderr
staged = paths(cmd(['git', 'diff', '--cached', '--name-only', '-z']))
assert staged and staged <= set(selected)
assert {p for p in staged if p.startswith('기억/layer1/')} == {'기억/layer1/M-0557.md'}
product_staged = {p for p in staged if p.startswith(('.claude/', '.agents/'))}
assert product_staged == set(preservation['product_files']) and len(product_staged) == 124
index = {}
result = cmd(['git', 'ls-files', '-s', '-z'])
assert result.returncode == 0
for row in result.stdout.split(b'\0'):
    if row:
        meta, p = row.split(b'\t',1)
        index[p.decode('utf-8')] = meta.decode().split()[1]
assert all(p in index for p in selected)
raw_paths = [p for p in selected if '/phases/007/tasks/provider-consumers/' in p or '/phases/007/manager-evidence/' in p]
raw_paths += [row['path'] for row in read(OUT / 'git-clean-observation.json')]
raw_paths = sorted(set(raw_paths))
result = cmd(['git', 'hash-object', '--no-filters', '--stdin-paths'], ('\n'.join(raw_paths)+'\n').encode('utf-8'))
assert result.returncode == 0, result.stderr
raw_oids = result.stdout.decode().splitlines()
assert len(raw_oids) == len(raw_paths)
assert all(index[p] == oid for p,oid in zip(raw_paths, raw_oids)), [p for p,oid in zip(raw_paths,raw_oids) if index[p]!=oid]
for row in read(OUT / 'product-commit-plan.json'):
    assert index[row['path']] == row['candidate_blob'], row['path']
assert cmd(['git','rev-parse','HEAD']).stdout.decode().strip() == head
state = cmd(['git', '--no-optional-locks', '-c', 'core.quotepath=false', 'status', '--porcelain=v1', '--untracked-files=no'])
(OUT / 'stage.json').write_text(json.dumps({'staged': sorted(staged), 'raw_verified': len(raw_paths),
    'corpus_verified': 102, 'status': state.stdout.decode('utf-8')},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
(OUT / 'commit-message.txt').write_text('공급자 전송과 직접 소비 회귀를 마감하고 운영 복구 문서 결속을 배정\n',encoding='utf-8',newline='\n')
record('commit.json', ['git', 'commit', '-F', str(OUT / 'commit-message.txt')])
new_head = cmd(['git','rev-parse','HEAD']).stdout.decode().strip()
actual = paths(cmd(['git','diff-tree','--no-commit-id','--name-only','-r','-z',new_head]))
assert actual == staged
assert not paths(cmd(['git','diff','--cached','--name-only','-z']))
assert sha(PHASE/'manager.json') == pending_sha
for p,h in sources.items():
    assert sha(ROOT/p) == (operator[p]['current'] if p in operator else h), p
receipt = dict(commit=new_head, parent=head, committed_files=len(actual), provider_product_files=len(product_staged),
               raw_objects_verified=len(raw_paths), corpus_objects_verified=102, source_files_verified=len(sources),
               documented_operator_differences=4, manager_sha256=pending_sha, next='008', pushed=False)
(OUT/'post-commit.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt,ensure_ascii=False))
