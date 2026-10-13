"""The B49 receipt/validation slice, with actual diff and original report existence."""
import hashlib
import json
from pathlib import Path
import subprocess
from run_command import ROOT, EVIDENCE, write_json

board = json.loads((ROOT / 'docs/do-math/시험-재편-2026-09-29/단계-전환표-2026-10-03.json').read_bytes())
record = board['current_work']['provider_population_integration']
reports = {}
for key in ('changed_area', 'structure'):
    source = record[key]
    p = Path(source['path'])
    row = {'historical_claim': source, 'exists': p.is_file()}
    if p.is_file():
        raw = p.read_bytes()
        data = json.loads(raw)
        row.update(actual_sha256=hashlib.sha256(raw).hexdigest(), counts=data.get('counts'),
                   selected=data.get('selected'), complete=data.get('complete'), successful=data.get('successful'))
    reports[key] = row
argv = ['git', 'show', '065a323a', '--',
        '.claude/skills/do-math/scripts/tests/sim/test_provider_runner_gaps.py',
        '.claude/skills/do-math/scripts/tests/sim/test_provider_close_worker_rejections.py']
p = subprocess.run(argv, cwd=ROOT, capture_output=True)
(EVIDENCE / 'history-b49.diff').write_bytes(p.stdout)
write_json(EVIDENCE / 'history-review.json', {'argv': argv, 'exit_code': p.returncode, 'reports': reports,
    'scope': 'B49 runner invalid-input, canonical-number rejection, pinned seal and local termination only; not PR15 as a whole.'})
print(json.dumps({'diff_exit': p.returncode, 'original_reports_exist': {k:v['exists'] for k,v in reports.items()}}))
