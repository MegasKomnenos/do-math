"""Select this administrative handoff; preserve task evidence bytes exactly."""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[6]
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = OUT.parent / 'tasks/codex-schema'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


selected = {RUN / p for p in ('context.md', 'plan.md', 'seams.md', 'phases/006/manager.json')}
selected.update((REPO / '기억/layer1/M-0556.md', REPO / '기억/색인.md', TASK / 'report.json'))
local = []
for p in (TASK / 'evidence').rglob('*'):
    if not p.is_file():
        continue
    if p.name in {'source-before.json', 'source-after.json'} and p != TASK / 'evidence/live-command/source-before.json':
        local.append(p.relative_to(REPO).as_posix())
    else:
        selected.add(p)
for p in (RUN / 'phases/007').rglob('*'):
    if p.is_file():
        selected.add(p)
excluded = {'handoff-reading.md', 'commit-paths.nul', 'commit-message.txt', 'commit.json',
            'post-commit.json', 'stage.json', 'handoff-precheck.json'}
for p in OUT.rglob('*'):
    if p.is_file() and p.name not in excluded:
        selected.add(p)
selected.update(OUT / name for name in ('preservation.json', 'handoff-check.json',
                                      'reading-decision-02.json', 'reader-02.json',
                                      'reader-02-execution.json', 'writing-status.json'))
paths = sorted(p.relative_to(REPO).as_posix() for p in selected)
assert not any(p.startswith(('.claude/', '.agents/', 'services/', '.codex/')) for p in paths)
value = {
 'commit_scope': 'Phase 006 manager records, immutable task report/evidence, phase 007 assignment and one memory node. Pending product bytes are archived; product paths are excluded.',
 'selected_files': paths,
 'task_evidence_sha256': {p.relative_to(REPO).as_posix(): sha(p) for p in selected
                           if p.is_file() and p.is_relative_to(TASK)},
 'locally_retained_duplicate_snapshots': sorted(local),
 'other_local_only': ['phase-006 runtime/session logs', 'handoff-reading.md assembled from recorded inputs',
                     '.codex/writing-flow raw reading sessions and draft snapshots',
                     'commit/stage/post-commit receipts and pathspec'],
 'reading_preservation': 'Reader JSON, execution metadata, decisions and input hashes are tracked. The assembled prose and executor copies remain local; common-docs.diff and tracked source files preserve the handoff.',
 'pending_product_archive': 'run:phases/006/manager-evidence/pending-products.zip',
 'pending_product_files': 50,
 'raw_evidence_policy': 'Stage the selected task and manager evidence as original bytes and verify staged object IDs. Do not rewrite task files or older phase records.'}
(OUT / 'preservation.json').write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(OUT / 'commit-paths.nul').write_bytes(b''.join(p.encode('utf-8') + b'\0' for p in paths))
print(json.dumps({'selected_files': len(paths), 'local_duplicate_snapshots': len(local),
                  'current_selected_bytes': sum(p.stat().st_size for p in selected if p.is_file())}))
