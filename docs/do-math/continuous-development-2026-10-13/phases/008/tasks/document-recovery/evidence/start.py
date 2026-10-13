import json
from pathlib import Path
import subprocess
from run_command import ROOT, EVIDENCE, snapshot, write_json, changed

current = snapshot()
write_json(EVIDENCE / 'source-start.json', current)
prior = json.loads((EVIDENCE.parents[3] / '007/tasks/provider-consumers/evidence/source-final.json').read_text(encoding='utf-8-sig'))
state = {name: subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout
         for name, args in [('head', ['rev-parse', 'HEAD']), ('status', ['status', '--porcelain=v1']), ('diff', ['diff', '--stat'])]}
state['difference_from_007'] = changed(prior, current)
write_json(EVIDENCE / 'start-state.json', state)
run = EVIDENCE.parents[4]
for filename in ('followup-packets.json', 'binding-inventory.json'):
    data = json.loads((run / 'phases/001/tasks/document-closeout/evidence' / filename).read_text(encoding='utf-8-sig'))
    def select(value):
        if isinstance(value, dict):
            if value.get('id') in ('P01', 'N03', 'N03-003') or 'LIVE_INSTALLATION_ROOT' in str(value.get('name', '')):
                print(json.dumps(value, ensure_ascii=False, indent=2))
            else:
                for child in value.values(): select(child)
        elif isinstance(value, list):
            for child in value: select(child)
    select(data)
print(json.dumps({'head': state['head'], 'prior_differences': state['difference_from_007']}, ensure_ascii=False))
