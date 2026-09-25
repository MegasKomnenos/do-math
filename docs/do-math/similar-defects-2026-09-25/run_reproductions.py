"""Reproduce the audited current defects in disposable test instances.

This is an audit harness, not a passing post-repair regression suite. Several
scripts deliberately assert the current wrong behavior; convert those
expectations before using them as repair acceptance tests.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ['repro_payload_storage.py', 'repro_checkpoints.py', 'reproduce_relation_reader.py',
           'probe_c.py', 'repro_trust_input.py', 'reproduce_control_boundary.py', 'probe_control_types.py']

def run(name):
    started = time.monotonic()
    command = [sys.executable, str(HERE / name)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0), timeout=240)
    for suffix, raw in [('stdout', result.stdout), ('stderr', result.stderr)]:
        (HERE / (name + '.' + suffix + '.txt')).write_bytes(raw)
    return {'script': name, 'sha256': hashlib.sha256((HERE / name).read_bytes()).hexdigest(),
        'exit_code': result.returncode, 'elapsed_seconds': round(time.monotonic() - started, 3),
        'stdout': name + '.stdout.txt', 'stderr': name + '.stderr.txt'}

if __name__ == '__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run, SCRIPTS))
    result = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        'observed_at': datetime.now(timezone.utc).isoformat(), 'scope': 'disposable fixtures; no real model service',
        'meaning': 'Zero means the current diagnostic script completed; this does not mean the product has no defects.',
        'scripts': rows}
    (HERE / 'reproductions.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(int(any(row['exit_code'] != 0 for row in rows)))
