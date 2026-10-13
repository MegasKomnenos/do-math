import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(r'C:\math')
out = Path(__file__).resolve().parent
paths = [r['path'] for r in json.loads((out / 'product-commit-plan.json').read_text(encoding='utf-8'))]
before = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in paths}
rows = []
for name, arguments in (
    ('generator-tests', ['.claude/skills/writing-skills/scripts/test_build_skill_mirrors.py']),
    ('mirror-check', ['.claude/skills/writing-skills/scripts/build_skill_mirrors.py', '--check']),
    ('skill-check', ['.claude/skills/do-math/scripts/probe_cli.py', '--skill-only']),
):
    argv = [sys.executable, '-u', '-B', *arguments]
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    (out / (name + '.stdout.txt')).write_bytes(stdout)
    (out / (name + '.stderr.txt')).write_bytes(stderr)
    rows.append(dict(name=name, argv=argv, pid=p.pid, started_at=started,
                     ended_at=datetime.now(timezone.utc).isoformat(), exit_code=p.returncode))
    (out / 'supplementary-checks.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(name, p.returncode, flush=True)
    assert p.returncode == 0
assert all(hashlib.sha256((root / p).read_bytes()).hexdigest() == h for p,h in before.items())
