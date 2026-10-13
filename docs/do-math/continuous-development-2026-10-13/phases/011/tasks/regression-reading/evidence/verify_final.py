from collections import Counter
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from session_tools import REPO, RUN, EVIDENCE, PYTHON, read, save, sha, now, snapshot, compare

start = read(EVIDENCE / 'source-start.json')
end = snapshot()
save(EVIDENCE / 'source-final.json', end)
changes = compare(start, end)
writes = read(RUN / 'phases/011/phase.json')['tasks'][0]['writes']
assert {row['path'] for row in changes} == set(writes)
assert read(EVIDENCE / 'start-verification.json')['versus_010_manager'] == []
for root in ('.claude/skills', '.agents/skills', '.agents/diff', 'services/continuous-development'):
    current = {p.relative_to(REPO).as_posix() for p in (REPO / root).rglob('*') if p.is_file()
               and '__pycache__' not in p.parts and p.suffix != '.pyc'}
    previous = {p for p in start if p.startswith(root + '/')}
    assert current == previous, (root, sorted(current - previous), sorted(previous - current))

selection = read(EVIDENCE / 'selection.json')['selected']
suites = {}
for label, tree in [('focused', '.claude'), ('canonical-final', '.claude'), ('mirror-final', '.agents')]:
    report = read(EVIDENCE / (label + '-results/report.json'))
    execution = read(EVIDENCE / (label + '-execution.json'))
    rows = [row for group in report['reports'] for row in group['rows']]
    assert report['complete'] and report['successful'] and execution['exit_code'] == 0
    assert not report['changed_during_run']
    assert len(rows) == len(set(row['id'] for row in rows)) == len(report['selected'])
    assert set(row['id'] for row in rows) == set(report['selected'])
    assert all(row['outcome'] == 'passed' for row in rows)
    if label != 'focused':
        assert set(report['selected']) == set(selection)
    python_mismatches = [p for p, value in report['source_sha256'].items()
                         if sha(REPO / tree / 'skills/do-math/scripts' / p) != value]
    assert not python_mismatches, python_mismatches
    before = read(EVIDENCE / (label + '-source-before.json'))
    after = read(EVIDENCE / (label + '-source-after.json'))
    assert execution['changes'] == compare(before, after)
    assert all(row['path'] == tree + '/skills/do-math/scripts/tests/.timings.json' for row in execution['changes'])
    suites[label] = {'selected': len(report['selected']), 'unique_rows': len(rows),
        'counts': report['counts'], 'exit_code': execution['exit_code'],
        'total_seconds': report['total_seconds'], 'python_hashes': len(report['source_sha256']),
        'python_hash_mismatches': [], 'changed_during_run': [],
        'source_changes': execution['changes'], 'row_ids': [row['id'] for row in rows]}

failures = {}
for label in ('related-results', 'baseline-repro-02-results'):
    old = read(RUN / 'phases/010/tasks/host-smoke/evidence' / label / 'report.json')
    rejected = [row for group in old['reports'] for row in group['rows'] if row['outcome'] != 'passed']
    assert len(rejected) == 2
    new = read(EVIDENCE / 'canonical-final-results/report.json')
    new_rows = {row['id']: row for group in new['reports'] for row in group['rows']}
    failures[label] = [{'id': row['id'], 'before': row['outcome'], 'after': new_rows[row['id']]['outcome'],
        'original_details': row['details']} for row in rejected]
    assert all(row['after'] == 'passed' for row in failures[label])

prior = read(RUN / 'phases/010/tasks/host-smoke/evidence/verification.json')
runtime = prior['runtime_unchanged']
provider_inputs = prior['provider_smoke_inputs_unchanged']
corpus = [p for p in start if '/scripts/tests/corpus/' in p]
assert len(runtime) == 124 and len(provider_inputs) == 3 and len(corpus) == 102
host_inputs = ['.claude/skills/do-math/scripts/tests/support/host_live.py',
    '.claude/skills/do-math/scripts/tests/smoke/test_host_live.py',
    '.claude/skills/do-math/scripts/tests/boundary/test_scheduling_windows_job.py',
    '.claude/skills/do-math/scripts/tests/boundary/test_scheduling_owned_job_children.py',
    '.claude/skills/do-math/scripts/tests/boundary/test_role_input_snapshot_reach.py',
    '.claude/skills/do-math/scripts/tests/시험-지침.md']
preserved = sorted(set(runtime + provider_inputs + host_inputs + corpus + [
    '.agents/diff/_rules.json', '.agents/diff/_manifest.json',
    '.claude/skills/writing-skills/scripts/build_skill_mirrors.py']))
preserved += [p.replace('.claude/', '.agents/', 1) for p in runtime + provider_inputs + host_inputs]
assert all(start[p] == end[p] for p in preserved)

host_recordings = []
python_sha = sha(PYTHON)
pythonw = PYTHON.with_name('pythonw.exe')
powershell = Path(shutil.which('powershell.exe'))
ps_command = [str(powershell), '-NoProfile', '-NonInteractive', '-Command', '$PSVersionTable.PSVersion.ToString()']
ps = subprocess.run(ps_command, capture_output=True, cwd=REPO)
(EVIDENCE / 'powershell-version.stdout.bin').write_bytes(ps.stdout)
(EVIDENCE / 'powershell-version.stderr.bin').write_bytes(ps.stderr)
assert ps.returncode == 0
ps_version = ps.stdout.decode('utf-8-sig').strip()
for label in ('host-final', 'mirror-host'):
    official = read(RUN / 'phases/010/tasks/host-smoke/evidence' / (label + '-results/report.json'))
    original_execution = read(RUN / 'phases/010/tasks/host-smoke/evidence' / (label + '.command.json'))
    assert official['complete'] and official['successful'] and official['counts'] == {'passed': 3}
    assert original_execution['exit_code'] == 0 and original_execution['cwd'] == str(REPO)
    assert Path(original_execution['argv'][0]) == PYTHON
    for recording in prior['host_recordings'][label]:
        path = RUN / recording['path']
        assert sha(path) == recording['sha256']
        observed = read(path)
        assert observed['passed'] and all(observed['checks'].values())
        if 'mode' in observed:
            assert Path(observed['python']) == PYTHON and observed['python_sha256'] == python_sha
            assert observed['python_version'] == sys.version
        else:
            for name in ('readable', 'supplied_only'):
                parent = read(path.parent / name / 'parent-process.json')
                assert parent['exit_code'] == 0 and parent['pythonw_sha256'] == sha(pythonw)
                assert Path(parent['argv'][0]) == pythonw
                ps_observed = read(path.parent / name / 'powershell-observed.json')
                assert Path(ps_observed['executable']) == powershell and ps_observed['version'] == ps_version
        host_recordings.append({'path': recording['path'], 'sha256': recording['sha256'], 'reused': True})

for operation, plan in [('mirror-build', 'mirror-plan'), ('cache-sync', 'cache-plan')]:
    execution = read(EVIDENCE / (operation + '-execution.json'))
    predicted = read(EVIDENCE / (plan + '.json'))
    assert execution['exit_code'] == 0 and execution['changes'] == predicted['changes']
for operation in ('mirror-check', 'skill-only'):
    execution = read(EVIDENCE / (operation + '-execution.json'))
    assert execution['exit_code'] == 0 and not execution['changes']
assert (REPO / '.claude/skills/do-math/scripts/tests/.timings.json').read_bytes() == (
    REPO / '.agents/skills/do-math/scripts/tests/.timings.json').read_bytes()

save(EVIDENCE / 'verification-final.json', {'at_utc': now(), 'result': 'pass',
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
    'source_count': len(end), 'changes': changes, 'writes_exactly_match': True,
    'suites': suites, 'old_failure_correspondence': failures,
    'runtime_unchanged': runtime, 'provider_inputs_unchanged': provider_inputs,
    'corpus_unchanged': corpus, 'all_preserved_paths': preserved,
    'host_recordings_reused': host_recordings,
    'tool_conditions': {'python': str(PYTHON), 'python_sha256': python_sha, 'python_version': sys.version,
        'pythonw': str(pythonw), 'pythonw_sha256': sha(pythonw), 'powershell': str(powershell),
        'powershell_version': ps_version, 'powershell_sha256_now': sha(powershell),
        'powershell_hash_limit': '010 recorded the path/version, not executable SHA256; do not claim historical binary byte equivalence.',
        'powershell_check_argv': ps_command, 'powershell_check_exit': ps.returncode, 'windows': os.name == 'nt'},
    'cache_synchronized': True, 'limits': 'Host smoke reused, no new paid calls. No full general/T3/mutation, Lean/scheduler/academic chains, or 13-C/L01 capacity certification.'})
print(json.dumps({'result': 'pass', 'source_count': len(end), 'changes': len(changes),
    'suites': {label: {'counts': values['counts'], 'exit_code': values['exit_code']} for label, values in suites.items()},
    'runtime_preserved': len(runtime), 'provider_inputs_preserved': len(provider_inputs),
    'corpus_paths_preserved': len(corpus), 'host_recordings_reused': len(host_recordings)}, ensure_ascii=False))
