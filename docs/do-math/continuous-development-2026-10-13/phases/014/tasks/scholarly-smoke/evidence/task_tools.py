import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

REPO = Path('C:/math')
OUT = Path(__file__).parent
PYTHON = sys.executable


def run(name, argv, *, live=False):
    env = dict(os.environ)
    if live:
        import shutil
        env.update(DO_MATH_SMOKE_CODEX_CLI=shutil.which('codex'), DO_MATH_SMOKE_CODEX_MODEL='gpt-6-astra',
                   DO_MATH_SMOKE_CODEX_EFFORT='low', DO_MATH_SMOKE_HOST=platform.node())
    record = {'command': argv, 'cwd': str(REPO), 'started_at': datetime.now(timezone.utc).isoformat(),
              'explicit_inputs': {k: v for k, v in env.items() if k.startswith('DO_MATH_SMOKE_')} if live else {}}
    path = OUT / (name + '.command.json')
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    with (OUT / (name + '.stdout')).open('wb') as out, (OUT / (name + '.stderr')).open('wb') as err:
        process = subprocess.Popen(argv, cwd=REPO, env=env, stdout=out, stderr=err,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        record['pid'] = process.pid
        path.write_text(json.dumps(record, indent=2), encoding='utf-8')
        record['exit_code'] = process.wait()
    record['ended_at'] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(record, indent=2), encoding='utf-8')
    print(json.dumps(record, ensure_ascii=False))
    return record['exit_code']


if __name__ == '__main__':
    mode, name, *args = sys.argv[1:]
    if mode == 'tests':
        tree = args.pop(0)
        live = name.startswith('live')
        command = [PYTHON, '-u', '-B', tree + '/scripts/run_tests.py', *args,
                   '--jobs', '1', '--output', str(OUT / name)]
        raise SystemExit(run(name, command, live=live))
    if mode == 'run':
        raise SystemExit(run(name, args))
