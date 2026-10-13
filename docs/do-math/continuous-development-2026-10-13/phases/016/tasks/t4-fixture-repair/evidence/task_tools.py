import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
HERE = Path(__file__).resolve().parent

def now():
    return datetime.now(timezone.utc).isoformat()

def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def snapshot():
    result = {}
    for base in ('.claude/skills', '.agents/skills', '.agents/diff'):
        for p in (REPO / base).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                result[p.relative_to(REPO).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result

def execute(label, args):
    command = [sys.executable, '-u', '-B', *args]
    before = snapshot()
    write(label + '.source-before.json', before)
    with (HERE / (label + '.stdout')).open('wb') as out, (HERE / (label + '.stderr')).open('wb') as err:
        started = now()
        child = subprocess.Popen(command, cwd=REPO, stdout=out, stderr=err,
                                 creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        write(label + '.started.json', {'command': command, 'cwd': str(REPO), 'pid': child.pid, 'started': started})
        code = child.wait()
    write(label + '.source-after.json', snapshot())
    write(label + '.command.json', {'command': command, 'cwd': str(REPO), 'pid': child.pid,
                                  'started': started, 'ended': now(), 'exit_code': code})
    print(json.dumps({'label': label, 'exit_code': code}), flush=True)
    return code

if __name__ == '__main__':
    if sys.argv[1] == 'start':
        current = snapshot()
        write('source-start.json', current)
        prior = json.loads((RUN / 'phases/015/manager-evidence/source-inspected.json').read_bytes())
        differences = {p: {'prior': h, 'current': current.get(p)} for p, h in prior.items() if current.get(p) != h}
        phase = json.loads((RUN / 'phases/016/phase.json').read_bytes())
        task = next(x for x in phase['tasks'] if x['id'] == 't4-fixture-repair')
        inputs = {}
        for ref in task['inputs']:
            root, relative = ref.split(':', 1)
            p = (REPO if root == 'repo' else RUN) / relative
            data = p.read_bytes()
            inputs[ref] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        write('input-source-comparison.json', {'source_count': len(current), 'prior_count': len(prior),
                                              'differences': differences, 'inputs': inputs})
        verification = json.loads((RUN / 'phases/015/manager-evidence/verification.json').read_bytes())
        write('prior-nonpassed.json', {s['label']: s['nonpassed'] for s in verification['suites']})
        print(json.dumps({'source_count': len(current), 'prior_count': len(prior), 'differences': differences}))
    elif sys.argv[1] == 'exec':
        sys.exit(execute(sys.argv[2], sys.argv[3:]))
