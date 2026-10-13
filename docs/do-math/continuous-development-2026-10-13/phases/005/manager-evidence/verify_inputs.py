"""Read-only manager cross-check of task outputs and current files."""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent
TASK = RUN / 'phases/005/tasks/corpus-git-bytes/evidence'
OLD = RUN / 'phases/004/tasks/mirror-corpus/evidence'


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def delta(a, b):
    return [k for k in sorted(a.keys() | b.keys()) if a.get(k) != b.get(k)]


def command(argv):
    before = datetime.datetime.now(datetime.timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return dict(argv=argv, cwd=str(ROOT), pid=p.pid, started_at=before,
                ended_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                exit_code=p.returncode, stdout=stdout.decode('utf-8'), stderr=stderr.decode('utf-8'))


check = command([sys.executable, '-B', str(ROOT / 'services/continuous-development/check.py'),
                 'report', str(ROOT), str(RUN), '005', 'corpus-git-bytes'])
save('report-check.json', check)
assert check['exit_code'] == 0, check
for name in ('context.md', 'plan.md', 'seams.md'):
    target = OUT / (name + '.before')
    if not target.exists():
        target.write_bytes((RUN / name).read_bytes())

start, final = [read(TASK / f'source-{s}.json') for s in ('start', 'final')]
current = {p: sha(ROOT / p) for p in final}
assert current == final, delta(current, final)
assignment = read(RUN / 'phases/005/phase.json')['tasks'][0]
report = read(TASK.parent / 'report.json')
changes = delta(start, final)
assert sorted(assignment['writes']) == changes == sorted(r['path'] for r in report['changes'])
prior = read(OLD / 'source-final.json')
assert delta(prior, start) == ['services/continuous-development/protocol.md']
result = dict(head=command(['git', 'rev-parse', 'HEAD'])['stdout'].strip(),
              report_sha256=sha(TASK.parent / 'report.json'), source_count=len(final),
              source_mismatches=delta(current, final), task_changes=changes,
              preexisting_changes=[dict(path=p, before=prior.get(p), after=start.get(p)) for p in delta(prior, start)])

begin, end = [read(TASK / f'corpus-{s}.json') for s in ('start', 'final')]
result['corpus'] = {}
for runtime, tree in end['trees'].items():
    base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
    files = {p.relative_to(base).as_posix(): p for p in base.rglob('*') if p.is_file()}
    assert set(files) == set(tree['files'])
    assert all(sha(files[k]) == v['sha256'] and files[k].stat().st_size == v['bytes'] for k, v in tree['files'].items())
    manifest = read(files['manifest.json'])
    assert manifest == tree['manifest'] == begin['trees'][runtime]['manifest']
    assert len(manifest['entries']) == 17
    bindings = []
    for entry in manifest['entries']:
        for pathfield, hashfield in [('path', 'source_sha256'), ('schema_path', 'schema_sha256')]:
            if hashfield in entry:
                bindings.append((entry[pathfield], entry[hashfield]))
        bindings.extend((r['path'], r['sha256']) for r in entry.get('recordings', []))
    assert len(bindings) == 41 and all(sha(files[p]) == h for p, h in bindings)
    changed = delta(begin['trees'][runtime]['files'], tree['files'])
    assert changed == ['.gitattributes']
    result['corpus'][runtime] = dict(entries=len(manifest['entries']), files=len(files),
                                   bytes=sum(p.stat().st_size for p in files.values()),
                                   sha_bindings=len(bindings), changes=changed)
assert {k: v['sha256'] for k,v in end['trees']['.claude']['files'].items()} == {k: v['sha256'] for k,v in end['trees']['.agents']['files'].items()}
paths = [r['path'] for r in end['git_rows']]
assert len(paths) == len(set(paths)) == 88
assert set(paths) == {v['path'] for t in end['trees'].values() for v in t['files'].values()}
for label, old_commands in [('start', begin['git_commands']), ('final', end['git_commands'])]:
    assert all(c['exit_code'] == 0 and c['cwd'] == str(ROOT) for c in old_commands)
    raw, clean = [c['stdout'].splitlines() for c in old_commands[:2]]
    assert len(raw) == len(clean) == 88
    assert old_commands[0]['argv'] == ['git', 'hash-object', '--no-filters', *paths]
    assert old_commands[1]['argv'] == ['git', 'hash-object', *paths]
    assert old_commands[2]['argv'] == ['git', 'check-attr', '--all', '--', *paths]
    differences = [p for p,a,b in zip(paths,raw,clean,strict=True) if a != b]
    assert differences == ([] if label == 'final' else [p for p in paths if p.endswith('/manifest.json')])
actual = [command(['git', 'hash-object', '--no-filters', *paths]),
          command(['git', 'hash-object', *paths]),
          command(['git', 'check-attr', '--all', '--', *paths])]
save('git-clean-observation.json', actual)
assert all(c['exit_code'] == 0 for c in actual)
assert all(a['stdout'] == b['stdout'] for a,b in zip(actual, end['git_commands'], strict=True))
result['git_paths'] = len(paths)
result['git_differences'] = []
result['commands'] = {}
for name, expected in [('start-command', 1), ('complete-start-command', 0), ('mirror-build', 0), ('mirror-check', 0), ('skill-check', 0), ('final-command', 0), ('attribute-diff', 0)]:
    c = read(TASK / name / 'command.json')
    assert c['exit_code'] == expected
    a,b = [read(TASK / name / f'source-{s}.json') for s in ('before','after')]
    changed = delta(a,b)
    assert changed == (['.agents/skills/do-math/scripts/tests/corpus/.gitattributes'] if name == 'mirror-build' else [])
    result['commands'][name] = dict(exit_code=c['exit_code'], changes=changed,
                                  stdout_sha256=sha(TASK / name / 'stdout.txt'), stderr_sha256=sha(TASK / name / 'stderr.txt'))
assert '1297' in (TASK / 'mirror-check/stdout.txt').read_text(encoding='utf-8')
skill = read(TASK / 'skill-check/stdout.txt')
assert skill['status'] == 'verified', skill
result['reuse'] = {}
for runtime, label in [('.claude', 'canonical-replay'), ('.agents', 'mirror-replay')]:
    old = read(OLD / label / 'report.json')
    pybase = ROOT / runtime / 'skills/do-math/scripts'
    python_files = {p.relative_to(pybase).as_posix(): sha(p) for p in pybase.rglob('*.py')}
    assert python_files == old['source_sha256'] and len(python_files) == 864
    rows = [r for group in old['reports'] for r in group['rows']]
    assert len(old['selected']) == len(set(old['selected'])) == len(rows) == 14
    assert set(old['selected']) == {r['id'] for r in rows}
    assert all(r['outcome'] == 'passed' for r in rows)
    assert old['counts'] == {'passed': 14} and old['complete'] and old['successful']
    assert not old['fixture_counts'] and not old['changed_during_run']
    assert read(OLD / (label + '-command') / 'command.json')['exit_code'] == 0
    result['reuse'][label] = dict(python_files=864, selected=14, passed=14, exit_code=0,
                                report_sha256=sha(OLD / label / 'report.json'), rerun=False)
g = read(TASK / 'verification-final.json')['reused']['generator-tests']
assert all(sha(ROOT / p) == h for p,h in g['input_sha256'].items())
assert read(OLD / 'generator-tests/command.json')['exit_code'] == 0
assert sha(OLD / 'generator-tests/stderr.txt') == g['stderr_sha256']
assert 'Ran 22 tests' in (OLD / 'generator-tests/stderr.txt').read_text(encoding='utf-8')
assert (OLD / 'generator-tests/stderr.txt').read_text(encoding='utf-8').rstrip().endswith('OK')
result['reuse']['generator-tests'] = g
save('verification.json', result)
print(json.dumps(result, ensure_ascii=False, indent=2))
