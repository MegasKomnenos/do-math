import json
from pathlib import Path
import hashlib
import subprocess
from task_tools import ROOT, HERE, dump

run = ROOT / 'docs/do-math/continuous-development-2026-10-13'
prior = json.loads((run/'phases/001/tasks/closure-map/evidence/prior-review-state.json').read_text(encoding='utf-8-sig'))
units = prior['review_units']
print('review units', type(units).__name__)
if isinstance(units, dict):
    entries = [(key,value) for key,value in units.items() if 'PR01' in key]
else:
    entries = [(str(i), value) for i,value in enumerate(units) if 'PR01' in str(value.get('id',value.get('unit','')))]
dump(HERE/'history-pr01.json', dict(entries))
for key,value in entries:
    print(key, list(value) if isinstance(value,dict) else str(value)[:1000])

summary_path = ROOT/'docs/do-math/시험-재편-2026-09-29/전체-T3-2026-10-03.json'
summary = json.loads(summary_path.read_text(encoding='utf-8-sig'))
original = Path(summary['report_path'])
out = {'summary': str(summary_path), 'summary_sha256': hashlib.sha256(summary_path.read_bytes()).hexdigest(),
       'original_path':str(original), 'original_exists':original.is_file(),
       'scope':summary['scope_limit'], 'counts_are_historical':True}
if original.is_file():
    out['original_sha256'] = hashlib.sha256(original.read_bytes()).hexdigest()
    out['matches_recorded_digest'] = out['original_sha256'] == summary['report_sha256']
    raw = json.loads(original.read_text(encoding='utf-8-sig'))
    out['original_summary'] = {key:raw.get(key) for key in ('complete','successful','counts','passed','measurement_missing','closing_eligible')}
dump(HERE/'history-original-observation.json',out)
print(json.dumps(out,ensure_ascii=False))
dump(HERE/'history-log.json', {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'log':subprocess.check_output(['git','log','-12','--oneline','--','.claude/skills/do-math/scripts/run_tests.py',
        '.claude/skills/do-math/scripts/tests/support/branch_gate.py'],cwd=ROOT,text=True)})
