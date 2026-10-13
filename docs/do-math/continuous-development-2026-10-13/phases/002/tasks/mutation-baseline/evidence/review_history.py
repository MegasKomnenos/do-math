"""Retain the exact PR01/B56 slice and observe availability of its historical raw reports."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path('C:/math')
OUT = Path(__file__).resolve().parent
board = json.loads((ROOT / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_text(encoding='utf-8-sig'))
history = board['current_work']['measurement_integration']
reports = []
for key in ('changed_area', 'structure', 'timing_red', 'exact_baseline_comparison'):
    declaration = history[key]
    path = Path(declaration['path'])
    item = {'selector': '/current_work/measurement_integration/' + key, 'declaration': declaration,
            'exists': path.is_file()}
    if path.is_file():
        raw = path.read_bytes()
        item['sha256'] = hashlib.sha256(raw).hexdigest()
        (OUT / ('B56-' + key + '.json')).write_bytes(raw)
    reports.append(item)
paths = ['.claude/skills/do-math/scripts/' + p for p in (
    'tests/support/mutation.py', 'tests/unit/test_mutation.py', 'tests/unit/test_runner_tiers.py', 'run_tests.py')]
for commit in ('bbe64043', 'f56a2772'):
    raw = subprocess.check_output(['git', 'show', commit, '--', *paths], cwd=ROOT)
    (OUT / (commit + '.patch')).write_bytes(raw)
(OUT / 'prior-review.json').write_text(json.dumps({'history': 'PR01/B56', 'reports': reports,
    'diffs': ['bbe64043.patch', 'f56a2772.patch'], 'scope': 'mutation child evidence, baseline and shared passed consumer'},
    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps([{'selector': r['selector'], 'exists': r['exists']} for r in reports]))
