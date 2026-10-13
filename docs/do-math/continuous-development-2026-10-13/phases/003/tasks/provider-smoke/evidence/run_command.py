"""Capture a task command without time limits or ambient environment disclosure."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[8]
EVIDENCE = Path(__file__).resolve().parent


def snapshot():
    files = {}
    for directory in ('.claude/skills/do-math', '.agents/skills/do-math'):
        for path in (REPO / directory).rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                files[path.relative_to(REPO).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    destination = EVIDENCE / sys.argv[1]
    destination.mkdir(parents=True, exist_ok=False)
    command = sys.argv[2:]
    write(destination / 'source-before.json', snapshot())
    metadata = {'argv': command, 'cwd': str(REPO),
                'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'environment': {key: value for key, value in os.environ.items()
                                if key.startswith('DO_MATH_SMOKE_')}}
    with (destination / 'stdout.txt').open('wb') as stdout, (destination / 'stderr.txt').open('wb') as stderr:
        process = subprocess.Popen(command, cwd=REPO, stdout=stdout, stderr=stderr)
        metadata['pid'] = process.pid
        write(destination / 'command.json', metadata)
        metadata['exit_code'] = process.wait()
    metadata['ended_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    after = snapshot()
    write(destination / 'source-after.json', after)
    before = json.loads((destination / 'source-before.json').read_text(encoding='utf-8'))
    metadata['changed_sources'] = sorted(key for key in before.keys() | after.keys()
                                         if before.get(key) != after.get(key))
    write(destination / 'command.json', metadata)
    print(json.dumps(metadata, ensure_ascii=False))
    sys.exit(metadata['exit_code'])
