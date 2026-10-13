"""Read current files and original phase-004 outputs without changing the product."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/004/manager-evidence'
E = RUN / 'phases/004/tasks/mirror-corpus/evidence'


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def git(*args):
    argv = ['git', *args]
    started = datetime.now(timezone.utc).isoformat()
    child = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = child.communicate()
    result = dict(argv=argv, cwd=str(ROOT), pid=child.pid, started_at=started,
                  ended_at=datetime.now(timezone.utc).isoformat(), exit_code=child.returncode,
                  stdout=stdout.decode('utf-8'), stderr=stderr.decode('utf-8'))
    assert child.returncode == 0, result
    return result


report = read(E.parent / 'report.json')
assert read(OUT / 'report-check.json')['exit_code'] == 0
before, final = (read(E / name) for name in ('source-before.json', 'source-final.json'))
current = {path: sha(ROOT / path) if (ROOT / path).is_file() else None for path in final}
mismatches = [path for path in final if final[path] != current[path]]
assert not mismatches, mismatches
changed = sorted(path for path in before.keys() | final.keys() if before.get(path) != final.get(path))
assert changed == sorted(row['path'] for row in report['changes'])
writes = read(RUN / 'phases/004/phase.json')['tasks'][0]['writes']
assert all(any(path.startswith(w) if w.endswith('/') else path == w for w in writes) for path in changed)
prior = read(RUN / 'phases/003/tasks/provider-smoke/evidence/source-final.json')
assert all(before.get(path) == value for path, value in prior.items())
assert report['status'] == 'partial'
assert {a['id']: a['result'] for a in report['acceptance']} == dict(A1='pass', A2='pass', A3='fail', A4='pass')

runs = {}
for name, runtime in [('canonical-replay', '.claude'), ('mirror-replay', '.agents')]:
    original = read(E / name / 'report.json')
    command = read(E / (name + '-command') / 'command.json')
    rows = [row for group in original['reports'] for row in group['rows']]
    assert Counter(original['selected']) == Counter(row['id'] for row in rows)
    assert len(rows) == len({row['id'] for row in rows})
    assert Counter(row['outcome'] for row in rows) == original['counts'] == {'passed': 14}
    assert original['complete'] and original['successful'] and not original['fixture_counts']
    assert sum(group['tests_run'] for group in original['reports']) == len(rows)
    assert not original['changed_during_run'] and command['exit_code'] == 0 and command['state'] == 'exited'
    bad = [p for p, value in original['source_sha256'].items()
           if sha(ROOT / runtime / 'skills/do-math/scripts' / p) != value]
    assert not bad, bad
    pre, post = (read(E / (name + '-command') / f'source-{suffix}.json') for suffix in ('before', 'after'))
    actual_changes = sorted(p for p in pre.keys() | post.keys() if pre.get(p) != post.get(p))
    assert actual_changes == command['changed_sources'] == [runtime + '/skills/do-math/scripts/tests/.timings.json']
    runs[name] = dict(selected=len(original['selected']), rows=len(rows), counts=original['counts'],
                      python_files=len(original['source_sha256']), current_python_mismatches=bad,
                      command=command, report_sha256=sha(E / name / 'report.json'),
                      actual_snapshot_changes=actual_changes)

command_checks = {}
for name, expected_exit in [('generator-red', 1), ('generator-tests', 0), ('mirror-build', 0),
                            ('final-mirror-build', 0), ('final-mirror-check', 0), ('skill-check', 0)]:
    command = read(E / name / 'command.json')
    pre, post = (read(E / name / f'source-{suffix}.json') for suffix in ('before', 'after'))
    changes = sorted(p for p in pre.keys() | post.keys() if pre.get(p) != post.get(p))
    assert changes == command['changed_sources'] and command['exit_code'] == expected_exit
    assert command['state'] == 'exited' and command['started_at'] < command['ended_at']
    command_checks[name] = dict(command=command, actual_snapshot_changes=changes,
                               stdout_sha256=sha(E / name / 'stdout.txt'), stderr_sha256=sha(E / name / 'stderr.txt'))
assert 'Ran 22 tests' in (E / 'generator-tests/stderr.txt').read_text(encoding='utf-8')
assert 'FAILED (failures=5)' in (E / 'generator-red/stderr.txt').read_text(encoding='utf-8')
assert read(E / 'skill-check/stdout.txt')['status'] == 'verified'
assert command_checks['mirror-build']['actual_snapshot_changes'] == read(E / 'build-plan.json')['changed']
assert command_checks['final-mirror-build']['actual_snapshot_changes'] == read(E / 'final-build-plan.json')['changed']

recorded = read(E / 'corpus-final.json')
trees = {}
paths = []
for runtime in ('.claude', '.agents'):
    base = ROOT / runtime / 'skills/do-math/scripts/tests/corpus'
    files = {p.relative_to(base).as_posix(): p for p in base.rglob('*') if p.is_file()}
    assert files.keys() == recorded['trees'][runtime]['files'].keys()
    assert all(sha(p) == recorded['trees'][runtime]['files'][rel]['sha256'] for rel, p in files.items())
    manifest = read(files['manifest.json'])
    bindings, refs = [], set()
    for entry in manifest['entries']:
        for field in ('path', 'final_path', 'source_path', 'compiled_path', 'schema_path'):
            if field in entry:
                refs.add(entry[field])
                assert entry[field] in files
        for path_key, sha_key in [('path', 'source_sha256'), ('schema_path', 'schema_sha256')]:
            if sha_key in entry:
                bindings.append((entry[path_key], entry[sha_key]))
        for recording in entry.get('recordings', []):
            refs.add(recording['path'])
            bindings.append((recording['path'], recording['sha256']))
    assert all(sha(files[path]) == value for path, value in bindings)
    assert not (files.keys() - refs - {'manifest.json', '.gitattributes'})
    trees[runtime] = dict(entries=len(manifest['entries']), files=len(files),
                          bytes=sum(p.stat().st_size for p in files.values()), sha_bindings=len(bindings),
                          file_sha256={rel: sha(p) for rel, p in sorted(files.items())})
    paths.extend(p.relative_to(ROOT).as_posix() for _, p in sorted(files.items()))
assert trees['.claude'] == trees['.agents']
assert all(before.get(path) == final.get(path) for path in final if path.startswith('.claude/skills/do-math/scripts/tests/corpus/'))
raw, clean = git('hash-object', '--no-filters', *paths), git('hash-object', *paths)
attrs = git('check-attr', '--all', '--', *paths)
clean_rows = [dict(path=p, raw_object_id=a, clean_object_id=b, matches=a == b)
              for p, a, b in zip(paths, raw['stdout'].splitlines(), clean['stdout'].splitlines(), strict=True)]
differences = [row for row in clean_rows if not row['matches']]
assert differences == recorded['git_clean_differences']
assert {r['path'] for r in differences} == {r + '/skills/do-math/scripts/tests/corpus/manifest.json' for r in ('.claude', '.agents')}
save('git-clean-observation.json', dict(commands=[raw, clean, attrs], rows=clean_rows, differences=differences))

probe = read(E / 'attribute-probe.json')
observations = []
for row in probe['path_spelling_observations']:
    a, b = git(*row['raw']['argv'][1:]), git(*row['clean']['argv'][1:])
    assert a['stdout'] == row['raw']['stdout'] and b['stdout'] == row['clean']['stdout']
    observations.append(dict(path=row['path'], spelling=row['spelling'], raw=a, clean=b, matches=a['stdout'] == b['stdout']))
assert sha(ROOT / '.claude/skills/do-math/.gitattributes') == probe['parent_original_sha256'] == probe['parent_restored_sha256']
save('path-spelling-observation.json', dict(git_version=git('--version'), observations=observations,
                                         parent_restored=True, parent_trial_repeated=False))

summary = dict(head=git('rev-parse', 'HEAD')['stdout'].strip(), report_status=report['status'],
               source_files=len(final), source_mismatches=mismatches, phase_003_source_files=len(prior),
               changed_files=changed, runs=runs, command_checks=command_checks, corpus=trees,
               git_clean_differences=differences, path_spelling_observations_matched=len(observations),
               product_modified_by_manager=False, product_tests_rerun=False,
               acceptance_decision=dict(A1='pass', A2='pass', A3='fail', A4='pass'))
save('verification.json', summary)
print(json.dumps({k: v for k, v in summary.items() if k not in ('runs', 'command_checks', 'corpus')}, ensure_ascii=False))
