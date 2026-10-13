import json
import hashlib
from pathlib import Path
from task_tools import ROOT, HERE, dump

run = ROOT / 'docs/do-math/continuous-development-2026-10-13'
paths = [
 'phases/001/tasks/gate-readiness/evidence/gate-readiness.json',
 'phases/002/tasks/mutation-baseline/report.json',
 'phases/014/tasks/scholarly-smoke/report.json',
 'phases/014/manager-evidence/verification.json',
 'phases/014/manager-evidence/source-inspected.json']
for relative in paths:
    value = json.loads((run / relative).read_text(encoding='utf-8-sig'))
    print(relative, 'keys:', list(value))
    if relative.endswith('report.json'):
        for key in ('status', 'narrative', 'acceptance', 'findings', 'checks'):
            print(key, json.dumps(value[key], ensure_ascii=False))
    elif 'source-inspected' in relative:
        mismatch = [p for p,h in value.items() if not (ROOT/p).is_file()
                    or hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != h]
        dump(HERE/'input-source-comparison.json', {'count':len(value), 'mismatch':mismatch})
        print('source comparison',len(value),mismatch)
    else:
        for key, item in value.items():
            encoded = json.dumps(item, ensure_ascii=False)
            if 'gate-readiness' in relative or len(encoded) < 7000:
                print(key, encoded)
            else:
                print(key, 'large field:',len(encoded))
