"""Select this handoff's records and preserve the pending product bytes separately."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/004/manager-evidence'
TASK = RUN / 'phases/004/tasks/mirror-corpus'


def read(path):
    return json.loads(path.read_bytes())


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


pending = set()
for name in ['003/tasks/provider-smoke', '004/tasks/mirror-corpus']:
    pending.update(row['path'] for row in read(RUN / 'phases' / name / 'report.json')['changes'])
assert len(pending) == 68
final = read(TASK / 'evidence/source-final.json')
assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == value for p, value in final.items())
archive = OUT / 'pending-product-working-tree.zip'
rows = []
with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as handle:
    for path in sorted(pending):
        data = (ROOT / path).read_bytes()
        handle.writestr(path, data)
        rows.append(dict(path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
with zipfile.ZipFile(archive) as handle:
    assert set(handle.namelist()) == pending
    assert all(hashlib.sha256(handle.read(r['path'])).hexdigest() == r['sha256'] for r in rows)
save(OUT / 'product-snapshot.json', dict(
    meaning='Exact pending phase-003/004 product bytes; failure-state evidence, not approval or an instruction to restore.',
    archive=archive.name, archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(), files=rows))

selected = {RUN / n for n in ('context.md', 'plan.md', 'seams.md')}
selected.update({TASK / 'report.json', RUN / 'phases/004/manager.json', ROOT / '기억/layer1/M-0554.md', ROOT / '기억/색인.md'})
excluded = []
for path in (TASK / 'evidence').rglob('*'):
    if not path.is_file():
        continue
    if '__pycache__' in path.parts or path.suffix == '.pyc' or (
        path.parent != TASK / 'evidence' and path.name in ('source-before.json', 'source-after.json')
    ):
        excluded.append(path.relative_to(ROOT).as_posix())
    else:
        selected.add(path)
for path in OUT.iterdir():
    if path.is_file() and not path.name.endswith('.before') and path.name != 'commit-paths.nul':
        selected.add(path)
for name in ('preservation.json', 'handoff-check.json', 'handoff-check.stdout.txt', 'handoff-check.stderr.txt'):
    selected.add(OUT / name)
selected.update(p for p in (RUN / 'phases/005').rglob('*') if p.is_file())
paths = sorted(p.relative_to(ROOT).as_posix() for p in selected)
assert all(p.startswith('docs/do-math/continuous-development-2026-10-13/') or p.startswith('기억/') for p in paths)
save(OUT / 'preservation.json', dict(
    commit_scope='Administrative handoff, raw task evidence, exact pending product archive and one memory node; no product paths.',
    selected_files=paths, locally_retained_duplicate_snapshots=sorted(excluded),
    other_local_only=['phases/004/logs/', 'runtime', 'manager-evidence/*.before', 'manager-evidence/commit-paths.nul'],
    raw_evidence_policy='Keep report/evidence/archive bytes unchanged; compare staged Git blobs before committing.',
    pending_product_files=len(rows)))
(OUT / 'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in paths) + b'\0')
print(json.dumps(dict(selected_files=len(paths), duplicate_snapshots_local=len(excluded),
                      archive_files=len(rows), archive_bytes=archive.stat().st_size), ensure_ascii=False))
