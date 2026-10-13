import json
import sys
from run_command import EVIDENCE, ROOT
sys.path.insert(0, str(ROOT / '.claude/skills/do-math/scripts'))
from do_math.file_io import read_bytes_shared
for label in ('canonical-joined-final', 'mirror-final'):
    path = EVIDENCE / label / 'results/report.json'
    if not path.exists():
        print(label, 'running')
        continue
    report = json.loads(read_bytes_shared(path))
    if 'selected' not in report:
        print(label, 'running')
        continue
    rows = [row for group in report['reports'] for row in group['rows']]
    print(label, len(report['selected']), report['counts'])
    for row in rows:
        if row['outcome'] != 'passed':
            print(json.dumps(row, ensure_ascii=False))
