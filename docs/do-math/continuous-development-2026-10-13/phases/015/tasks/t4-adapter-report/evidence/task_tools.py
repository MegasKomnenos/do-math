import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('C:/math')
HERE = Path(__file__).resolve().parent

def snapshot():
    paths = []
    for base in ('.claude/skills', '.agents/skills', '.agents/diff'):
        paths.extend(p for p in (ROOT / base).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and '.t3-store' not in p.parts)
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    label, *command = sys.argv[1:]
    if label == 'snapshot':
        dump(HERE / command[0], snapshot())
    else:
        target = HERE / (label + '.command.json')
        if target.exists():
            raise ValueError('Existing evidence: ' + str(target))
        record = {'command': command, 'cwd': str(ROOT),
                  'started': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        dump(HERE / (label + '.source-before.json'), snapshot())
        with (HERE / (label + '.stdout')).open('wb') as out, (HERE / (label + '.stderr')).open('wb') as err:
            child = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err)
            record['pid'] = child.pid
            dump(HERE / (label + '.started.json'), record)
            record['exit_code'] = child.wait()
        record['finished'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        dump(HERE / (label + '.source-after.json'), snapshot())
        dump(target, record)
        print(json.dumps(record, ensure_ascii=False))
        print((HERE / (label + '.stdout')).read_text(encoding='utf-8', errors='replace')[-2400:])
        print((HERE / (label + '.stderr')).read_text(encoding='utf-8', errors='replace')[-1600:])
        sys.exit(record['exit_code'])
