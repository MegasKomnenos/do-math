import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
HERE = Path(__file__).resolve().parent
PYTHON = sys.executable
TEMP = Path('C:/Temp/dm027').resolve()

def save(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def snapshot():
    return {p.relative_to(REPO).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for root in ('.claude/skills', '.agents/skills', '.agents/diff')
            for p in (REPO / root).rglob('*') if p.is_file()
            and '__pycache__' not in p.parts and p.suffix != '.pyc'}

def difference(a, b):
    return [p for p in sorted(a.keys() | b.keys()) if a.get(p) != b.get(p)]

def environment():
    TEMP.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TEMP=str(TEMP), TMP=str(TEMP), TMPDIR=str(TEMP), PYTHONDONTWRITEBYTECODE='1')
    return env

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'start':
        before = json.loads((RUN / 'phases/026/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
        current = snapshot()
        save('source-start.json', current)
        probe = subprocess.run(['git', '-C', str(TEMP), 'rev-parse', '--show-toplevel'], env=environment(), capture_output=True)
        result = {'files': len(current), 'previous_files': len(before), 'differences': difference(before, current),
                  'git_temp_exit': probe.returncode, 'git_temp_stdout': probe.stdout.decode(),
                  'git_temp_stderr': probe.stderr.decode(), 'previous_sample': next(iter(before.items()))}
        save('start-verification.json', result)
        print(json.dumps(result, ensure_ascii=False))
        assert not result['differences'] and probe.returncode != 0
    elif action == 'run':
        label, script, *arguments = sys.argv[2:]
        before = snapshot()
        save(label + '-source-before.json', before)
        command = [PYTHON, '-u', '-B', script, *arguments]
        with (HERE / (label + '.stdout')).open('wb') as out, (HERE / (label + '.stderr')).open('wb') as err:
            child = subprocess.Popen(command, cwd=REPO, env=environment(), stdout=out, stderr=err)
            save(label + '-process.json', {'command': command, 'pid': child.pid, 'state': 'running'})
            code = child.wait()
        after = snapshot()
        save(label + '-source-after.json', after)
        result = {'command': command, 'pid': child.pid, 'state': 'finished', 'exit_code': code,
                  'source_changes': difference(before, after)}
        save(label + '-process.json', result)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(code)
    elif action == 'end':
        current = snapshot()
        save('source-end.json', current)
        before = json.loads((HERE / 'source-start.json').read_text())
        changed = difference(before, current)
        writes = json.loads((RUN / 'phases/027/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
        outside = [p for p in changed if p not in writes]
        result = {'files': len(current), 'changes': changed, 'outside_writes': outside}
        save('end-verification.json', result)
        print(json.dumps(result, ensure_ascii=False))
        assert not outside
