"""Read-only audit export of one fixed do-math instance snapshot."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
BASE = Path(r'C:\math\.skill-workspace\parking-unimodality-fresh-20261021-1144')
REPO = BASE / 'repo'
CLI = Path(r'C:\math\.agents\skills\do-math\scripts\do_math.py')
INSTANCE = 'RI-01M5E5GMKK5Q7HBXRQ9QRCVRMD'
SNAPSHOT = 'a5678ee5991aa0680e94680b620efbee8af458b8'

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def cli(*args):
    p = subprocess.run([sys.executable, str(CLI), *args, '--repository', str(REPO), '--instance', INSTANCE], capture_output=True, cwd=r'C:\math')
    if p.returncode:
        raise RuntimeError(p.stdout.decode('utf-8', errors='replace') + p.stderr.decode('utf-8', errors='replace'))
    return json.loads(p.stdout)

def query(kind):
    pages, items, cursor = [], [], None
    while True:
        args = ['query', '--snapshot', SNAPSHOT, '--kind', kind, '--limit', '1000']
        if cursor: args += ['--cursor', cursor]
        result = cli(*args)
        pages.append(result)
        items.extend(result['result']['items'])
        cursor = result['result'].get('next_cursor')
        if not cursor: break
    save(ROOT / 'evidence' / f'{kind}.json', {'snapshot': SNAPSHOT, 'pages': pages, 'records': [x['record'] for x in items]})
    return kind, len(items)

def read(path):
    response = cli('read', '--snapshot', SNAPSHOT, '--path', path)
    raw = response['result']['text']
    return json.loads(raw)

def main():
    kinds = ['execution', 'task', 'activity', 'event', 'question', 'operational_dispositions',
             'self_check_obligations', 'self_check_responses', 'observation_facts',
             'intent_imports', 'knowledge', 'formal_results', 'identity_assessments',
             'review_cycles', 'reservation', 'control_receipts', 'integration', 'question_links']
    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(query, k): k for k in kinds}
        for f in concurrent.futures.as_completed(futures):
            try: outcomes.append({'kind': f.result()[0], 'count': f.result()[1]})
            except Exception as e: outcomes.append({'kind': futures[f], 'error': str(e)})
    save(ROOT/'evidence'/'collection.json', outcomes)
    save(ROOT/'evidence'/'status.json', cli('status', '--json'))
    tree = subprocess.check_output(['git','-C',str(REPO),'ls-tree','-r','--long',SNAPSHOT], text=True, encoding='utf-8')
    (ROOT/'evidence'/'git-tree.txt').write_text(tree, encoding='utf-8')
    save(ROOT/'evidence'/'hold.json', json.loads((BASE/'work/operator/HOLD.json').read_text(encoding='utf-8')))
    # Host-local operational artifacts are separate from the Git snapshot.
    for name, source in [('recovery-result.json', BASE/'work/operator/recovery/EX-01M5E7N1QANYK8Y7060FYA037K/result.json'),
                         ('recovery-verification.json', BASE/'work/operator/recovery/EX-01M5E7N1QANYK8Y7060FYA037K/verification.json'),
                         ('recovery-regression.json', BASE/'work/operator/recovery/EX-01M5E7N1QANYK8Y7060FYA037K/regression-evidence.json'),
                         ('latest-engine.json', BASE/'work/operator/latest-engine.json')]:
        save(ROOT/'evidence'/name, json.loads(source.read_text(encoding='utf-8')))
    manifest = []
    for p in sorted((ROOT/'evidence').glob('*')):
        if p.is_file():
            data = p.read_bytes()
            manifest.append({'path':p.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    save(ROOT/'evidence'/'manifest.json', {'instance':INSTANCE,'snapshot':SNAPSHOT,'files':manifest})
    print(json.dumps(outcomes, ensure_ascii=False))

if __name__ == '__main__': main()
