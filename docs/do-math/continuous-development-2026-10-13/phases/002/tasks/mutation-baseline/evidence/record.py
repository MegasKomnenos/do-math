"""Record immutable command output and source editions for this task."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path('C:/math')
EVIDENCE = Path(__file__).resolve().parent


def snapshot():
    paths = [p for base in ('.claude/skills/do-math', '.agents/skills/do-math')
             for p in (ROOT / base).rglob('*')
             if p.is_file() and '__pycache__' not in p.parts]
    return {'time': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            'status': subprocess.check_output(['git', '-c', 'core.quotepath=false', 'status', '--short'],
                                             cwd=ROOT, text=True, encoding='utf-8'),
            'files': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(paths)}}


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    label, *command = sys.argv[1:]
    if not command:
        write(EVIDENCE / f'{label}.json', snapshot())
    else:
        directory = EVIDENCE / label
        directory.mkdir()
        write(directory / 'source-before.json', snapshot())
        started = time.monotonic()
        record = {'command': command, 'cwd': str(ROOT),
                  'started': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        with (directory / 'stdout.txt').open('w', encoding='utf-8') as stdout, \
             (directory / 'stderr.txt').open('w', encoding='utf-8') as stderr:
            process = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
            record['pid'] = process.pid
            write(directory / 'process.json', record)
            record['exit_code'] = process.wait()
        record.update(ended=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      seconds=time.monotonic() - started)
        write(directory / 'process.json', record)
        write(directory / 'source-after.json', snapshot())
        print(json.dumps(record))
        print((directory / 'stdout.txt').read_text(encoding='utf-8')[-7000:])
        print((directory / 'stderr.txt').read_text(encoding='utf-8')[-3000:])
        raise SystemExit(record['exit_code'])
