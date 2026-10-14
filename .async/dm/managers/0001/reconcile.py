"""Reconcile the interrupted legacy result without rerunning product tests."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile

REPO = Path('C:/math')
RECORDS = REPO / '.async/dm'
LEGACY = REPO / 'docs/do-math/continuous-development-2026-10-13'
OLD = LEGACY / 'phases/029'
OUT = Path(__file__).resolve().parent

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

previous = read(OLD / 'manager-evidence/verification.json')
inspected = read(OLD / 'manager-evidence/source-inspected.json')
current = {p.relative_to(REPO).as_posix(): sha(p)
           for root in ('.claude/skills', '.agents/skills', '.agents/diff')
           for p in (REPO / root).rglob('*')
           if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
assert current == inspected == read(OLD / 'tasks/doc-names/evidence/source-end.json')
start = read(OLD / 'tasks/doc-names/evidence/source-start.json')
assert start == read(LEGACY / 'phases/028/manager-evidence/source-inspected.json')
changes = sorted(p for p in current if current[p] != start[p])
report = read(OLD / 'tasks/doc-names/report.json')
assert changes == previous['changes']
assert set(changes) == {row['path'] for row in report['changes']}
assert set(changes) <= set(read(OLD / 'phase.json')['tasks'][0]['writes'])
task_files = read(OLD / 'manager-evidence/task-files.json')
actual_task_files = {p.relative_to(LEGACY).as_posix(): sha(p)
                     for p in (OLD / 'tasks/doc-names').rglob('*') if p.is_file()}
assert task_files == actual_task_files
snap = read(RECORDS / 'sources/source-hashes.json')
assert all(sha(REPO / p) == digest for p, digest in snap.items())
runs = []
selections = []
for folder, tree in [('c2', '.claude'), ('m2', '.agents')]:
    evidence = OLD / 'tasks/doc-names/evidence'
    r = read(evidence / folder / 'report.json')
    rows = [row for group in r['reports'] for row in group['rows']]
    ids = [row['id'] for row in rows]
    assert len(ids) == len(set(ids)) == 183 and set(ids) == set(r['selected'])
    assert Counter(row['outcome'] for row in rows) == {'passed': 183}
    assert r['complete'] and r['successful'] and not r['changed_during_run']
    execution = read(evidence / ('final-' + folder + '.execution.json'))
    assert execution['exit_code'] == 0
    assert all(sha(REPO / tree / 'skills/do-math/scripts' / p) == digest
               for p, digest in r['source_sha256'].items())
    assert set(previous['old_document_ids']) <= set(ids)
    selections.append(r['selected'])
    runs.append({'folder': folder, 'selected': len(ids), 'passed': len(ids), 'exit_code': 0,
                 'python_sources': len(r['source_sha256']), 'report_sha256': sha(evidence / folder / 'report.json')})
assert selections[0] == selections[1]
for row in previous['closure']:
    assert set(row['canonical_passed_test_ids']) <= set(selections[0])
    assert set(row['mirror_passed_test_ids']) <= set(selections[1])
for label in ('mirror-check', 'skill-c', 'skill-m'):
    assert read(OLD / 'tasks/doc-names/evidence' / (label + '.execution.json'))['exit_code'] == 0
assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=REPO).strip()
save('source-inspected.json', current)

# Keep the interrupted drafts and original raw outputs in a durable artifact.
preserve = [LEGACY / p for p in task_files]
preserve += [REPO / p for p in previous['product_paths']]
preserve += [p for p in (OLD / 'manager-evidence').rglob('*') if p.is_file()]
preserve += [OLD / 'manager.pending.json', OLD / 'logs/manager.log', REPO / '기억/layer1/M-0579.md']
preserve += [p for p in (LEGACY / 'phases/030').rglob('*') if p.is_file()]
preserve = sorted(set(preserve))
archive_map = {p.relative_to(REPO).as_posix(): sha(p) for p in preserve}
with zipfile.ZipFile(OUT / 'legacy-029-raw.zip', 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for path in preserve:
        z.write(path, path.relative_to(REPO).as_posix())
with zipfile.ZipFile(OUT / 'legacy-029-raw.zip') as z:
    assert set(z.namelist()) == set(archive_map)
    assert all(hashlib.sha256(z.read(p)).hexdigest() == digest for p, digest in archive_map.items())
save('preservation.json', {'archive': 'legacy-029-raw.zip', 'sha256': sha(OUT / 'legacy-029-raw.zip'),
                          'files': archive_map, 'originals_unchanged': True,
                          'restore_policy': 'Preservation only; no automatic restore or legacy publication.'})
result = {'decision': 'Accept the scoped legacy 029 result as the inherited starting edition; no async task acceptance.',
          'source_count': len(current), 'migration_snapshot_files': len(snap), 'source_differences': [],
          'task_file_count': len(task_files), 'task_bytes_unchanged': True,
          'changes': changes, 'product_paths': previous['product_paths'], 'final_runs_reused': runs,
          'closed_findings': [row['finding'] for row in previous['closure']],
          'new_product_tests': 0, 'new_external_calls': 0,
          'legacy_publication_missing': not (OLD / 'manager.json').exists(),
          'head_before': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
          'remaining': ['L01 Q1/Q2 and UTF-8 byte requirement', 'Windows 1314 symlink rejection not exercised',
                        'G4-G8 final gates', 'R02/R07/R18 and other explicitly open semantic questions'],
          'basis': ['legacy manager verification/review and original reports', 'current diff and parser/helper/test reading',
                    'fresh current-source/raw-result hash comparison']}
save('inheritance-review.json', result)
print(json.dumps({k: result[k] for k in ('source_count', 'migration_snapshot_files', 'task_file_count',
                                      'source_differences', 'new_product_tests')}, ensure_ascii=False))
