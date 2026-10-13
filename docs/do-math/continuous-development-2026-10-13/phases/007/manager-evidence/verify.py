"""Manager's independent comparison of submitted evidence with current files."""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = RUN / 'phases/007/manager-evidence'
E = RUN / 'phases/007/tasks/provider-consumers/evidence'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def command(argv, name):
    started = datetime.now(timezone.utc).isoformat()
    p = subprocess.Popen(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    (OUT / (name + '.stdout.txt')).write_bytes(stdout)
    (OUT / (name + '.stderr.txt')).write_bytes(stderr)
    row = dict(argv=argv, cwd=str(ROOT), pid=p.pid, started_at=started,
               ended_at=datetime.now(timezone.utc).isoformat(), exit_code=p.returncode)
    write(name + '.json', row)
    assert p.returncode == 0, (name, stderr.decode('utf-8', errors='replace'))
    return stdout

report = read(E.parent / 'report.json')
phase = read(E.parents[2] / 'phase.json')
command([sys.executable, '-B', 'services/continuous-development/check.py', 'report',
         str(ROOT), str(RUN), '007', 'provider-consumers'], 'report-check')
start, final = read(E / 'source-start.json'), read(E / 'source-final.json')
previous = read(RUN / 'phases/006/tasks/codex-schema/evidence/source-final.json')
assert start == previous
changed = sorted(p for p in start.keys() | final.keys() if start.get(p) != final.get(p))
assert changed == sorted(c['path'] for c in report['changes'])
writes = phase['tasks'][0]['writes']
assert all(any(p == w or w.endswith('/') and p.startswith(w) for w in writes) for p in changed)
current_differences = {p: {'task_final': h, 'current': sha(ROOT / p) if (ROOT / p).is_file() else None}
                       for p, h in final.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h}
operator_paths = [prefix + '/skills/write-for-reader/' + suffix
                  for prefix in ('.claude', '.agents')
                  for suffix in ('scripts/writing_flow.py', 'references/독해_검토.md')]
assert set(current_differences) == set(operator_paths)
checks = {}
all_current_rows = {}
for label in ('pair-red', 'pair-green', 'consumers', 'raw-green', 'consumers-final', 'boundaries', 'corpus', 'mirror'):
    r = read(E / label / 'report.json')
    c = read(E / (label + '-command') / 'command.json')
    rows = [row for group in r['reports'] for row in group['rows']]
    ids = [row['id'] for row in rows]
    assert len(ids) == len(set(ids)) == len(r['selected'])
    assert set(ids) == set(r['selected'])
    assert dict(Counter(row['outcome'] for row in rows)) == r['counts']
    assert sum(g['tests_run'] for g in r['reports']) == len(ids)
    assert r['complete'] and all(g['complete'] for g in r['reports'])
    expected_exit = 1 if label in ('pair-red', 'consumers') else 0
    assert c['state'] == 'exited' and c['exit_code'] == expected_exit
    assert r['successful'] == (expected_exit == 0)
    assert not r['changed_during_run']
    before = read(E / (label + '-command') / 'source-before.json')
    after = read(E / (label + '-command') / 'source-after.json')
    delta = sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p))
    assert delta == sorted(c['changed_sources'])
    assert all(p.endswith('/tests/.timings.json') for p in delta)
    prefix = '.agents' if label == 'mirror' else '.claude'
    scripts = ROOT / prefix / 'skills/do-math/scripts'
    python_delta = [p for p, h in r['source_sha256'].items() if sha(scripts / p) != h]
    if label in ('raw-green', 'consumers-final', 'boundaries', 'corpus', 'mirror'):
        assert not python_delta
    checks[label] = dict(selected=len(ids), unique_rows=len(ids), counts=r['counts'], exit_code=c['exit_code'],
                         python_count=len(r['source_sha256']), python_changes_since_run=python_delta,
                         during_run_changes=delta, report_sha256=sha(E / label / 'report.json'),
                         pid=c['pid'], started_at=c['started_at'], ended_at=c['ended_at'])
    if label == 'consumers-final':
        all_current_rows = {row['id']: row['outcome'] for row in rows}
old = read(RUN / 'phases/006/tasks/codex-schema/evidence/consumers/report.json')
old_failed = [row['id'] for g in old['reports'] for row in g['rows'] if row['outcome'] == 'failed']
assert len(old_failed) == 11
assert all(all_current_rows[i] == 'passed' for i in old_failed)
reuse = read(E / 'live-reuse.json')
for kind in ('runtime', 'smoke_inputs'):
    for p, h in reuse[kind].items():
        assert h['current'] == h['live'] == sha(ROOT / p)
for provider, surface in reuse['surfaces'].items():
    assert surface['path'] == surface['previous_path']
    assert surface['sha256'] == surface['previous_sha256'] == sha(Path(surface['path']))
assert reuse['new_model_calls'] == 0
corpus = read(E / 'corpus-final.json')
paths = []
trees = {}
for prefix, tree in corpus['trees'].items():
    base = ROOT / prefix / 'skills/do-math/scripts/tests/corpus'
    manifest = read(base / 'manifest.json')
    entries = manifest['entries']
    assert len(entries) == tree['entry_count'] == 18
    actual = {p.relative_to(base).as_posix(): sha(p) for p in base.rglob('*') if p.is_file()}
    assert actual == {p: v['sha256'] for p, v in tree['files'].items()}
    assert len(actual) == tree['file_count'] == 51
    assert sum((base / p).stat().st_size for p in actual) == tree['bytes'] == 223685
    manifest_bindings = []
    for entry in entries:
        for key, path_key in (('source_sha256', 'path'), ('schema_sha256', 'schema_path'),
                              ('transport_schema_sha256', 'transport_schema_path')):
            if key in entry and path_key in entry:
                manifest_bindings.append((entry['id'], key, entry[path_key], entry[key]))
        for recording in entry.get('recordings', []):
            manifest_bindings.append((entry['id'], 'recordings.sha256', recording['path'], recording['sha256']))
            if 'bytes' in recording:
                assert (base / recording['path']).stat().st_size == recording['bytes']
    assert sorted(manifest_bindings) == sorted((b['entry'], b['key'], b['path'], b['expected']) for b in tree['bindings'])
    for binding in tree['bindings']:
        assert sha(base / binding['path']) == binding['expected'] == binding['actual']
    assert len(tree['bindings']) == 50
    paths.extend(v['path'] for v in tree['files'].values())
    trees[prefix] = dict(entries=len(entries), files=len(actual), bytes=tree['bytes'], bindings=len(tree['bindings']))
assert {p: v['sha256'] for p, v in corpus['trees']['.claude']['files'].items()} == {
    p: v['sha256'] for p, v in corpus['trees']['.agents']['files'].items()}
raw = command(['git', 'hash-object', '--no-filters', *paths], 'corpus-raw').decode().splitlines()
clean = command(['git', 'hash-object', *paths], 'corpus-clean').decode().splitlines()
assert len(raw) == len(clean) == 102 and raw == clean
write('git-clean-observation.json', [dict(path=p, raw=a, clean=b) for p, a, b in zip(paths, raw, clean)])
result = dict(head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              source_count=len(final), changes=changed, current_differences=current_differences,
              operator_change_basis='run:sources/model-policy-2026-10-14.md', checks=checks,
              recovered_failures=old_failed, runtime_unchanged_since_live=list(reuse['runtime']),
              smoke_inputs_unchanged=list(reuse['smoke_inputs']), corpus=trees,
              corpus_raw_clean_count=len(raw), new_model_calls=0)
write('verification.json', result)
print(json.dumps({k: v for k, v in result.items() if k in ('head', 'source_count', 'corpus_raw_clean_count')}, ensure_ascii=False))
print('PASS: 26 task changes, four documented operator differences, eight test runs, eleven recovered failures.')
