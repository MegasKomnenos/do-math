"""Prepare an exact administrative path list, then stage/commit only that list."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
O = Path(__file__).resolve().parent

def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))

def save(n, value):
    (O / n).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def git(*args, data=None):
    p = subprocess.run(['git', *args], cwd=R, input=data, capture_output=True)
    if p.returncode:
        raise RuntimeError((args, p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')))
    return p.stdout

def main():
    mode = sys.argv[1]
    if mode == 'prepare':
        assert not git('diff', '--cached', '--name-only', '-z'), 'Existing staged changes must not be mixed'
        tasks = read(O / 'task-files.json')
        paths = [RUN / name for name in tasks]
        excluded = {'context.md.before', 'plan.md.before', 'seams.md.before', 'preservation.json',
                    'stage.json', 'commit.json', 'commit-paths.nul', 'handoff-check.txt'}
        paths += [p for p in O.iterdir() if p.is_file() and p.name not in excluded]
        paths += [O / 'preservation.json', O / 'handoff-check.txt', RUN / 'phases/028/manager.json',
                  RUN / 'context.md', RUN / 'plan.md', RUN / 'seams.md',
                  RUN / 'phases/029/phase.json', RUN / 'phases/029/tasks/doc-names/objective.md',
                  R / '기억/layer1/M-0578.md', R / '기억/색인.md']
        rels = sorted({p.relative_to(R).as_posix() for p in paths})
        known = {p.relative_to(R).as_posix(): sha(p) for p in paths
                 if p.exists() and p.name not in ('preservation.json', 'handoff-check.txt')}
        known[(RUN / 'phases/028/manager.json').relative_to(R).as_posix()] = sha(RUN / 'phases/028/manager.pending.json')
        save('preservation.json', dict(
            head_before=git('rev-parse', 'HEAD').decode().strip(),
            policy='Directly track all 92 task files and selected manager/next-phase/memory files. No product file changes; no redundant archive.',
            tracked_paths=rels, expected_raw_sha256=known, task_raw_sha256=tasks,
            local_only=['context.md.before', 'plan.md.before', 'seams.md.before', 'commit-paths.nul', 'stage.json', 'commit.json', '../logs/manager.log'],
            limitations='Local administrative receipts and active logs may be removed by local cleanup. Task report/evidence bytes are preserved under the existing -text attributes. Historical task objectives retain Git text normalization. Handoff output is created by the final check; preservation excludes its own recursive hash.'))
        print(json.dumps({'prepared_paths': len(rels), 'task_files': len(tasks)}))
        return
    manifest = read(O / 'preservation.json')
    rels = manifest['tracked_paths']
    assert git('rev-parse', 'HEAD').decode().strip() == manifest['head_before'], 'HEAD advanced'
    assert (RUN / 'phases/028/manager.json').is_file()
    assert not (RUN / 'phases/028/manager.pending.json').exists()
    for name, digest in manifest['expected_raw_sha256'].items():
        assert sha(R / name) == digest, name
    for name, digest in manifest['task_raw_sha256'].items():
        assert sha(RUN / name) == digest, name
    if mode == 'stage':
        assert not git('diff', '--cached', '--name-only', '-z')
        (O / 'commit-paths.nul').write_bytes(b'\0'.join(s.encode('utf-8') for s in rels) + b'\0')
        git('add', '-f', '--pathspec-from-file=' + str(O / 'commit-paths.nul'), '--pathspec-file-nul')
        entries = {}
        for row in git('ls-files', '--stage', '-z').split(b'\0'):
            if not row: continue
            meta, path = row.split(b'\t', 1)
            mode_bits, oid, stage = meta.split()
            assert stage == b'0'
            entries[path.decode('utf-8')] = oid.decode('ascii')
        blob_data = git('cat-file', '--batch', data=''.join(entries[p] + '\n' for p in rels).encode('ascii'))
        offset = 0
        raw_exact = []; text_normalized = []
        for name in rels:
            end = blob_data.index(b'\n', offset)
            oid, kind, size = blob_data[offset:end].split()
            assert kind == b'blob'
            offset = end + 1; size = int(size)
            data = blob_data[offset:offset+size]; offset += size + 1
            current = (R / name).read_bytes()
            if data == current:
                raw_exact.append(name)
            else:
                assert name.endswith('/objective.md') and data == current.replace(b'\r\n', b'\n'), name
                text_normalized.append(name)
        changed = [x.decode('utf-8') for x in git('diff', '--cached', '--name-only', '-z').split(b'\0') if x]
        assert set(changed) <= set(rels)
        assert [p for p in changed if p.startswith('기억/layer1/')] == ['기억/layer1/M-0578.md']
        git('diff', '--cached', '--check')
        save('stage.json', dict(paths=changed, tree=git('write-tree').decode().strip(),
                               raw_exact=raw_exact, text_normalized=text_normalized,
                               head_before=manifest['head_before']))
        print(json.dumps({'staged_changes': len(changed), 'raw_exact': len(raw_exact), 'text_normalized': len(text_normalized)}, ensure_ascii=False))
        return
    assert mode == 'commit'
    stage = read(O / 'stage.json')
    assert git('write-tree').decode().strip() == stage['tree'], 'Staged tree changed'
    assert max(p.name for p in (R / '기억/layer1').glob('M-*.md')) == 'M-0578.md'
    receipt = git('commit', '-m', 'N01 문서 조사 검수와 공통 수리 배정을 마감함').decode('utf-8', 'replace')
    head = git('rev-parse', 'HEAD').decode().strip()
    committed = [x.decode('utf-8') for x in git('diff-tree', '--no-commit-id', '--name-only', '-r', '-z', 'HEAD').split(b'\0') if x]
    assert set(committed) == set(stage['paths'])
    assert not git('diff', '--cached', '--name-only', '-z')
    save('commit.json', dict(exit_code=0, head=head, head_before=manifest['head_before'],
                            paths=committed, stdout=receipt, pushed=False))
    print(json.dumps({'head': head, 'committed_files': len(committed), 'push': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
