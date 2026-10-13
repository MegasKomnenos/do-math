import hashlib
import json
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = OUT.parent / 'tasks/provider-consumers'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

products = [r['path'] for r in json.loads((OUT / 'product-commit-plan.json').read_text(encoding='utf-8'))]
selected = {ROOT / p for p in products}
byte_repairs = [r['path'] for r in json.loads((OUT / 'staged-corpus-difference.json').read_text(encoding='utf-8'))]
selected.update(ROOT / p for p in byte_repairs)
selected.update(RUN / p for p in ('context.md', 'plan.md', 'seams.md', 'sources/model-policy-2026-10-14.md', 'phases/007/manager.json'))
selected.update((ROOT / '기억/색인.md', ROOT / '기억/layer1/M-0557.md', TASK / 'report.json'))
required_commands = {name + '-command' for name in ('pair-red', 'pair-green', 'consumers', 'raw-green', 'consumers-final', 'boundaries', 'corpus', 'mirror')}
local = []
for p in (TASK / 'evidence').rglob('*'):
    if not p.is_file():
        continue
    if p.name in {'source-before.json', 'source-after.json'} and p.parent.name not in required_commands:
        local.append(p.relative_to(ROOT).as_posix())
    else:
        selected.add(p)
selected.update(p for p in (RUN / 'phases/008').rglob('*') if p.is_file())
excluded = {'handoff-reading.md', 'commit-paths.nul', 'commit-message.txt', 'commit.json', 'post-commit.json',
            'stage.json', 'context.md.before', 'plan.md.before', 'seams.md.before'}
for p in OUT.rglob('*'):
    if p.is_file() and p.name not in excluded:
        selected.add(p)
selected.update(OUT / p for p in ('preservation.json', 'handoff-check.json', 'memory-check.json',
                                'writing-status.json', 'handoff-recheck.json'))
paths = sorted(p.relative_to(ROOT).as_posix() for p in selected)
value = {
    'commit_scope': 'Reviewed provider products from phases 003-007, phase 007 task evidence and manager handoff, phase 008 assignment, current model-policy source, M-0557 and memory index. No push.',
    'selected_files': paths, 'product_files': products,
    'git_byte_repairs': byte_repairs,
    'git_byte_repair_reason': 'The final staged-object audit found two existing Lean recordings stored with three CRLF sequences normalized to LF in HEAD/index. The working bytes already match the reviewed task-final corpus. Stage those exact bytes without editing products, task reports or the published manager decision. These two Git delivery corrections are separate from the 124 reviewed task-change paths.',
    'task_evidence_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in selected if p.is_file() and p.is_relative_to(TASK)},
    'locally_retained_duplicate_snapshots': sorted(local),
    'other_local_only': ['Service session/runtime logs', 'before copies recoverable from common-docs.diff and current tracked documents',
                        'assembled handoff-reading.md; its component hashes are tracked in reading-inputs.json',
                        '.codex/writing-flow full executor events and copies; reader result/execution metadata/decision are tracked',
                        'stage.json, commit.json, post-commit.json, commit-message.txt, commit-paths.nul'],
    'operator_changes_excluded': ['.claude/skills/write-for-reader/scripts/writing_flow.py',
        '.claude/skills/write-for-reader/references/독해_검토.md', '.agents counterparts',
        'run:settings.json', 'run:start.py', 'run:README.md'],
    'raw_evidence_policy': 'Preserve selected task and manager evidence bytes. Compare all 102 corpus index blobs and selected evidence objects against raw files before commit.',
}
(OUT / 'preservation.json').write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
(OUT / 'commit-paths.nul').write_bytes(b''.join(p.encode('utf-8')+b'\0' for p in paths))
print(json.dumps({'selected_files': len(paths), 'product_files': len(products), 'local_duplicate_snapshots': len(local),
                  'current_bytes': sum(p.stat().st_size for p in selected if p.is_file())}))
