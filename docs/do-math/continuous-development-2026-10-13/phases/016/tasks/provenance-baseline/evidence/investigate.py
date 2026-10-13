"""Read-only Git/source inspection. Never imports project modules."""
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path('C:/math')
RUN = REPO / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
PREFIX = '.claude/skills/do-math/scripts'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(name, *args):
    argv = ['git', *args]
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.run(argv, cwd=REPO, capture_output=True)
    (OUT / (name + '.stdout')).write_bytes(p.stdout)
    (OUT / (name + '.stderr')).write_bytes(p.stderr)
    write(name + '.command.json', dict(argv=argv, cwd=str(REPO), started=started,
          ended=datetime.now(timezone.utc).isoformat(), exit_code=p.returncode,
          stdout=name+'.stdout', stderr=name+'.stderr', stdout_sha256=sha(p.stdout)))
    if p.returncode:
        raise RuntimeError((argv, p.returncode, p.stderr.decode('utf-8', errors='replace')))
    return p.stdout


def main():
    task = json.loads((RUN/'phases/016/phase.json').read_text(encoding='utf-8-sig'))['tasks'][1]
    inputs = []
    for ref in task['inputs'] + ['run:context.md', 'run:plan.md', 'run:seams.md',
                               'run:phases/016/tasks/provenance-baseline/objective.md']:
        kind, rel = ref.split(':', 1)
        path = (REPO if kind == 'repo' else RUN) / rel
        data = path.read_bytes()
        inputs.append(dict(reference=ref, sha256=sha(data), bytes=len(data)))
    write('input-manifest.json', inputs)
    head = git('head', 'rev-parse', 'HEAD').decode().strip()
    git('git-version', '--version')
    git('provenance-log', 'log', '--format=fuller', '--', PREFIX+'/tests/support/branch_gate.py',
        PREFIX+'/tests/boundary/test_shared_input_provenance.py')
    fix = 'bbe64043f49d46fb7c3b6e768b99a8acbaa125cf'
    parent = git('fix-parent', 'rev-parse', fix+'^').decode().strip()
    git('fix-metadata', 'show', '--no-patch', '--format=fuller', fix)
    git('fix-diff', 'diff', parent, fix, '--', PREFIX+'/tests/support/branch_gate.py',
        PREFIX+'/tests/support/t3_store.py', PREFIX+'/tests/boundary/test_shared_input_provenance.py',
        PREFIX+'/run_tests.py')
    git('fix-search', 'log', '--format=%H %s', '-S', 'input_dependencies', '--',
        PREFIX+'/tests/support/branch_gate.py')
    git('baseline-metadata', 'show', '--no-patch', '--format=fuller', parent)
    git('baseline-tree', 'ls-tree', '-r', '-z', parent, '--', PREFIX+'/')
    for label, commit in [('baseline', parent), ('fix', fix), ('head', head)]:
        for file in ['run_tests.py','tests/support/branch_gate.py','tests/support/t3_store.py']:
            git(label+'-'+Path(file).stem, 'show', commit+':'+PREFIX+'/'+file)
    write('history-selection.json', dict(inspected_head=head, introduction_commit=fix,
                                      baseline_commit=parent, selection='First parent immediately before input_dependencies/shared producer provenance introduction; source/API validation still required.'))
    inspected = json.loads((RUN/'phases/015/manager-evidence/source-inspected.json').read_text(encoding='utf-8-sig'))
    write('source-inspected-shape.json', dict(type=type(inspected).__name__, keys=list(inspected)[:15]))
    print(json.dumps(dict(head=head, fix=fix, baseline=parent, inputs=len(inputs), source_shape=list(inspected)[:10]), ensure_ascii=False))


if __name__ == '__main__':
    main()
