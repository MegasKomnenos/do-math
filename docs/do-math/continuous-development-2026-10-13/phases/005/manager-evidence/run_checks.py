import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def record(name, argv):
    before = datetime.datetime.now(datetime.timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    result = dict(argv=argv, cwd=str(ROOT), pid=p.pid, started_at=before,
                  ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  exit_code=p.returncode, stdout=stdout.decode('utf-8'), stderr=stderr.decode('utf-8'))
    (OUT / name).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n',encoding='utf-8',newline='')
    print(name, result['exit_code'], result['stdout'], result['stderr'])
    if p.returncode:
        raise SystemExit(p.returncode)

record('memory-check.json', [sys.executable, '-B', '기억/scripts/validate_memory_index.py'])
# Check relevant code/evidence has not changed while the manager wrote the handoff.
final=json.loads((RUN/'phases/005/tasks/corpus-git-bytes/evidence/source-final.json').read_bytes())
assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in final.items())
record('handoff-check.json', [sys.executable, '-B', 'services/continuous-development/check.py',
                             'handoff', str(ROOT), str(RUN), '005'])

