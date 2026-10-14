from pathlib import Path
import hashlib, json, subprocess, sys, os, datetime

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
E = Path(__file__).parent
PY = sys.executable

def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def digest(path):
    raw = path.read_bytes()
    return {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}

def snapshot(name):
    files = {}
    for base in ('.claude/skills', '.agents/skills', '.agents/diff'):
        for p in (REPO / base).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc':
                files[p.relative_to(REPO).as_posix()] = digest(p)
    save(name + '.json', files)
    return files

def command(name, argv, cwd=REPO):
    before = snapshot(name + '-before')
    env = os.environ.copy()
    temp = Path('C:/t/p023')
    temp.mkdir(parents=True, exist_ok=True)
    env.update(TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp), PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
    info = {'argv': argv, 'cwd': str(cwd), 'environment': {k: env[k] for k in ('TEMP','TMP','TMPDIR','PYTHONDONTWRITEBYTECODE','PYTHONUTF8')}, 'start': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'exit_code': None}
    with (E / (name + '.stdout')).open('wb') as out, (E / (name + '.stderr')).open('wb') as err:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=out, stderr=err)
        info['pid'] = proc.pid
        save(name + '-process.json', info)
        info['exit_code'] = proc.wait()
    after = snapshot(name + '-after')
    info.update(end=datetime.datetime.now(datetime.timezone.utc).isoformat(), changes=sorted(p for p in set(before)|set(after) if before.get(p) != after.get(p)))
    save(name + '-process.json', info)
    print(name, 'exit', info['exit_code'], flush=True)
    for suffix in ('stdout','stderr'):
        print((E / (name + '.' + suffix)).read_text(encoding='utf-8', errors='replace')[-2500:])
    return info['exit_code']

if __name__ == '__main__':
    if sys.argv[1] == 'start':
        current = snapshot('start')
        for name, argv in [('git-status',['git','status','--porcelain=v1']), ('git-head',['git','rev-parse','HEAD']), ('git-diff',['git','diff','--no-ext-diff']), ('git-index',['git','diff','--cached','--no-ext-diff'])]:
            p = subprocess.run(argv,cwd=REPO,capture_output=True)
            (E/(name+'.stdout')).write_bytes(p.stdout)
            (E/(name+'.stderr')).write_bytes(p.stderr)
        old = json.loads((RUN/'phases/022/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
        save('start-comparison.json', {'previous_count':len(old), 'current_count':len(current), 'differences':sorted(p for p in set(old)|set(current) if old.get(p)!=current.get(p, {}).get('sha256'))})
        print((E/'start-comparison.json').read_text(encoding='utf-8'))
    elif sys.argv[1] == 'test':
        name, tree, *ids = sys.argv[2:]
        command(name, [PY, '-u','-B',str(REPO/tree/'skills/do-math/scripts/run_tests.py'), *ids,'--jobs','1','--output',str(E/name)])
    elif sys.argv[1] == 'cmd':
        command(sys.argv[2],sys.argv[3:])
    elif sys.argv[1] == 'snapshot':
        snapshot(sys.argv[2])

