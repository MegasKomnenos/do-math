"""Record actual subprocess output, lifetime, and source hashes for this task."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
EVIDENCE = Path(__file__).resolve().parent


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def snapshot():
    paths = set()
    for rel in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
        paths.update(p for p in (ROOT / rel).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc')
    paths.add(ROOT / '.gitattributes')
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def changed(before, after):
    return [p for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]


def run(label, argv):
    output = EVIDENCE / label
    output.mkdir(exist_ok=False)
    before = snapshot()
    write_json(output / 'source-before.json', before)
    record = {'argv': argv, 'cwd': str(ROOT), 'wrapper_pid': os.getpid(),
              'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with (output / 'stdout.txt').open('wb') as stdout, (output / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(argv, cwd=ROOT, stdout=stdout, stderr=stderr)
        record.update(pid=process.pid, state='running')
        write_json(output / 'command.json', record)
        code = process.wait()
    after = snapshot()
    write_json(output / 'source-after.json', after)
    record.update(ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  exit_code=code, state='exited', changed_sources=changed(before, after))
    write_json(output / 'command.json', record)
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return code


if __name__ == '__main__':
    raise SystemExit(run(sys.argv[1], sys.argv[2:]))
