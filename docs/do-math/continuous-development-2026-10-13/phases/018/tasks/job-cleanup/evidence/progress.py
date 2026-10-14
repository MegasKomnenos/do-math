import collections
import json
import sys
from pathlib import Path
from task_driver import E, REPO
sys.path.insert(0,str(REPO/'.claude/skills/do-math/scripts'))
from do_math.file_io import read_bytes_shared
root = E/sys.argv[1]
counts = collections.Counter()
completed = []
for p in root.glob('*/result.json'):
    try:
        d = json.loads(read_bytes_shared(p))
    except (OSError, ValueError, TypeError):
        continue
    rows = [r for r in d.get('rows',[]) if not r.get('fixture')]
    counts.update(r['outcome'] for r in rows)
    completed.append((p.parent.name,len(rows)))
log = E/('canonical-t4-short.stderr' if sys.argv[1] == 'c4' else 'mirror-t4-short.stderr')
log_passed = sum(line.endswith('... ok') for line in log.read_text(encoding='utf-8',errors='replace').splitlines()) if log.exists() else 0
print(json.dumps({'inprocess_log_passed':log_passed,'output':str(root),'groups_with_result':len(completed),'outcomes':dict(counts),
                  'recent':sorted(completed)[-4:]},ensure_ascii=False))
