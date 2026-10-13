import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='')

old = json.loads((RUN / 'phases/004/manager-evidence/product-snapshot.json').read_bytes())
assert all(sha(ROOT / row['path']) == row['sha256'] for row in old['files'])
paths = json.loads((RUN / 'phases/005/phase.json').read_bytes())['tasks'][0]['writes']
assert not (set(paths) & {r['path'] for r in old['files']})
archive = OUT / 'pending-attributes.zip'
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as z:
    for p in paths:
        z.writestr(p, (ROOT / p).read_bytes())
with zipfile.ZipFile(archive) as z:
    assert all(z.read(p) == (ROOT / p).read_bytes() for p in paths)
save('product-snapshot.json', {
    'meaning': 'Phase-005 pending attribute bytes; combine with the unchanged phase-004 68-file archive. Candidate evidence, not product approval or a restore instruction.',
    'prior_snapshot': 'run:phases/004/manager-evidence/product-snapshot.json',
    'prior_archive': 'run:phases/004/manager-evidence/' + old['archive'],
    'prior_archive_sha256': old['archive_sha256'],
    'prior_files_unchanged': len(old['files']),
    'archive': archive.name, 'archive_sha256': sha(archive),
    'files': [{'path': p, 'bytes': (ROOT/p).stat().st_size, 'sha256': sha(ROOT/p)} for p in paths]})
assert sha(RUN / 'phases/004/manager-evidence' / old['archive']) == old['archive_sha256']

selected = {RUN / name for name in ('context.md','plan.md','seams.md')}
selected.update([RUN / 'phases/005/manager.json', ROOT / '기억/layer1/M-0555.md', ROOT / '기억/색인.md'])
local = []
for p in (RUN / 'phases/005/tasks/corpus-git-bytes').rglob('*'):
    if not p.is_file():
        continue
    if p.name in {'source-before.json','source-after.json'}:
        local.append(p.relative_to(ROOT).as_posix())
    else:
        selected.add(p)
for p in (RUN / 'phases/006').rglob('*'):
    if p.is_file():
        selected.add(p)
for p in OUT.rglob('*'):
    if not p.is_file() or p.suffix in {'.before','.nul'} or p.name in {'commit.json','post-commit.json'}:
        continue
    selected.add(p)
# These administrative outputs are created after this preparation and before staging.
selected.update(OUT / name for name in ('memory-check.json','handoff-check.json','preservation.json'))
rels = sorted(p.relative_to(ROOT).as_posix() for p in selected)
assert not any(p.startswith(('.claude/', '.agents/', 'services/')) for p in rels)
raw = {p.relative_to(ROOT).as_posix(): sha(p)
       for p in selected if p.is_file() and '/tasks/corpus-git-bytes/evidence/' in p.as_posix()}
save('preservation.json', {
    'commit_scope': 'Administrative handoff, unchanged task report/evidence, pending attributes archive, next assignment and one memory node; no product paths.',
    'selected_files': rels,
    'task_evidence_sha256': raw,
    'locally_retained_duplicate_snapshots': sorted(local),
    'other_local_only': ['phase-005 runtime/session logs', 'manager .before snapshots', 'commit pathspec and post-commit administrative receipts'],
    'pending_product_prior_files': 68, 'pending_product_new_files': 2,
    'raw_evidence_policy': 'Stage exact report/evidence bytes; compare staged blobs before commit. Previous phase outputs are immutable.'})
(OUT / 'commit-paths.nul').write_bytes(b''.join(p.encode('utf-8') + b'\0' for p in rels))
print(json.dumps({'selected_files':len(rels),'local_duplicate_snapshots':len(local),'pending_product_prior_files':68,'pending_product_new_files':2},ensure_ascii=False))

