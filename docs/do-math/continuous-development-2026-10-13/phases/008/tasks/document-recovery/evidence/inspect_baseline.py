import hashlib
import json
import subprocess
from run_command import ROOT, EVIDENCE
start = json.loads((EVIDENCE / 'source-start.json').read_bytes())
for path in ['.claude/skills/do-math/scripts/tests/support/doc_code.py', '.claude/skills/do-math/references/CLI-실행-계약.md']:
    raw = subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT)
    print(path, 'start', start[path], 'raw', hashlib.sha256(raw).hexdigest(),
          'lf', hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest(),
          'crlf', hashlib.sha256(raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest())
