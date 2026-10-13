import ast
import hashlib
import json
from pathlib import Path
import subprocess
from task_tools import REPO, RUN, HERE, write

paths = ['support/knowledge_roundtrip.py', 'support/knowledge_installed_lean.py',
         'boundary/test_observation_real_job.py', 'boundary/test_scheduling_host_processes.py',
         'boundary/test_scheduling_background_processes.py', 'boundary/test_submission_lean_preview.py']
rows = []
for relative in paths:
    path = '.claude/skills/do-math/scripts/tests/' + relative
    log = subprocess.run(['git', 'log', '--format=%H %s', '--', path], cwd=REPO, capture_output=True, check=True)
    (HERE / (Path(relative).stem + '.history.log')).write_bytes(log.stdout)
    commits = [line.split()[0] for line in log.stdout.decode('utf-8').splitlines()]
    selected = commits[-1:]
    if commits[0] not in selected:
        selected.insert(0, commits[0])
    for commit in selected:
        result = subprocess.run(['git', 'show', commit, '--', path], cwd=REPO, capture_output=True, check=True)
        output = Path(relative).stem + '-' + commit[:8] + '.diff'
        (HERE / output).write_bytes(result.stdout)
        rows.append({'path':path,'commit':commit,'diff':output,'sha256':hashlib.sha256(result.stdout).hexdigest()})
start = json.loads((HERE / 'source-start.json').read_bytes())
verification = json.loads((RUN / 'phases/015/manager-evidence/verification.json').read_bytes())
source_checks = []
for tree, label in [('.claude', 'canonical-t4-final'), ('.agents', 'mirror-t4-full')]:
    prior = json.loads((RUN / 'phases/015/tasks/t4-adapter-report/evidence' / label / 'report.json').read_bytes())
    bad = []
    for p, h in prior['source_sha256'].items():
        rel = tree + '/skills/do-math/scripts/' + p
        if start[rel] != h:
            bad.append(rel)
    source_checks.append({'label':label,'python_count':len(prior['source_sha256']),'start_mismatches':bad})
    assert not bad
consumer = {}
for p in (REPO / '.claude/skills/do-math/scripts/tests').rglob('*.py'):
    tree = ast.parse(p.read_text(encoding='utf-8-sig'))
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)
               and n.module in ('support.knowledge_roundtrip', 'support.knowledge_installed_lean')]
    if imports:
        consumer[p.relative_to(REPO).as_posix()] = imports
write('history-review.json', {'slices':rows,'prior_red_source_checks':source_checks,
                              'direct_consumers':consumer})
print(json.dumps({'slices':rows,'prior_red_source_checks':source_checks,'direct_consumers':consumer}, ensure_ascii=False))
