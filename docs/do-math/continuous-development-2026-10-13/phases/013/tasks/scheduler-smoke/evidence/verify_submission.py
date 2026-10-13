"""Reconcile actual task outputs and preserved bytes; no product execution."""
import hashlib
import json
from pathlib import Path
import subprocess
from datetime import datetime, timezone

R = Path('C:/math')
RUN = R / 'docs/do-math/continuous-development-2026-10-13'
E = RUN / 'phases/013/tasks/scheduler-smoke/evidence'


def read(p):
    return json.loads(p.read_bytes())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(name, value):
    (E / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


start, final = read(E / 'source-start.json'), read(E / 'source-final.json')
changes = {p: {'before': start.get(p), 'after': final.get(p)}
           for p in sorted(set(start) | set(final)) if start.get(p) != final.get(p)}
writes = read(RUN / 'phases/013/phase.json')['tasks'][0]['writes']
outside = [p for p in changes if not any(p == w or w.endswith('/') and p.startswith(w) for w in writes)]
assert not outside, outside
assert all(sha(R / p) == h for p, h in final.items())
assert not read(E / 'start-comparison.json')['differences']

suites = []
for folder in ['live-01', 'live-02', 'live-03', 'live-final', 'canonical-related', 'mirror-related']:
    result = read(E / folder / 'report.json')
    rows = [row for group in result['reports'] for row in group['rows']]
    selected = result['selected']
    record = {'folder': folder, 'selected': selected, 'rows': rows,
              'complete': result['complete'], 'successful': result['successful'],
              'actual_exit': read(E / (folder + '.command.json'))['exit_code'],
              'counts': result['counts'], 'source_file_count': len(result['source_sha256']),
              'changed_during_run': result['changed_during_run'], 'seconds': result['total_seconds']}
    assert len(rows) == len({row['id'] for row in rows}) == len(selected)
    assert set(selected) == {row['id'] for row in rows}
    assert not result['changed_during_run']
    if folder in ['canonical-related', 'mirror-related']:
        prefix = '.claude' if folder == 'canonical-related' else '.agents'
        assert result['complete'] and result['successful'] and record['actual_exit'] == 0
        assert all(row['outcome'] == 'passed' for row in rows)
        differences = {p: [h, sha(R / prefix / 'skills/do-math/scripts' / p)]
                       for p, h in result['source_sha256'].items()
                       if sha(R / prefix / 'skills/do-math/scripts' / p) != h}
        record['source_current_differences'] = differences
        assert not differences
    suites.append(record)
assert suites[-1]['selected'] == suites[-2]['selected']

live = []
for folder in ['live-final', 'canonical-related', 'mirror-related']:
    p = next((E / folder).rglob('smoke.json'))
    s = read(p)
    assert s['passed'] and all(s['checks'].values()) and not s['cleanup']['errors']
    assert s['cleanup']['final_status'] == {'operator': None, 'engine': None, 'wake': None}
    assert s['cleanup']['final_observation']['processes'] == []
    run_evidence = {}
    for role, current in s['runs'].items():
        binding = s['run_bindings'][role]
        assert int(current['last_run_ticks']) > int(binding['before']['last_run_ticks'])
        assert binding['before']['last_result'] == 267011
        assert current['state'] == 'Ready' and current['last_result'] == 0
        run_evidence[role] = {'before': binding['before']['last_run_utc'], 'after': current['last_run_utc'],
                              'result': current['last_result'], 'binding': binding}
    assert set(run_evidence) == {'operator', 'engine', 'wake'}
    names = s['names']
    assert s['cancelled']['wake'] is None
    live.append({'folder': folder, 'path': p.relative_to(RUN).as_posix(), 'checks': s['checks'],
                 'names': names, 'environment': s['environment'], 'executables': s['executables'],
                 'run_evidence': run_evidence, 'wake_request': s['wake_request'],
                 'cleanup': s['cleanup'], 'fast_process_pid_observed': any(o['processes'] for o in s['observations'])})
    save(folder + '-observation.json', live[-1])

old = read(RUN / 'phases/012/tasks/lean-smoke/evidence/verification-final.json')
reused_paths = old['runtime_paths'] + old['provider_inputs'] + old['host_inputs']
for tree in ['.claude', '.agents']:
    reused_paths.extend([f'{tree}/skills/do-math/scripts/tests/{p}' for p in
                        ['smoke/test_lean_live.py', 'support/lean_live.py']])
assert all(start[p] == final[p] for p in reused_paths)
host_records = []
for row in old['host_recordings_reused']:
    p = RUN / row['path']
    assert p.is_file() and sha(p) == row['sha256']
    host_records.append({'path': row['path'], 'sha256': sha(p)})
tool = old['host_tool_conditions_reused']
assert sha(Path(tool['python'])) == tool['python_sha256']
assert sha(Path(tool['pythonw'])) == tool['pythonw_sha256']
assert live[-1]['environment']['powershell'] == tool['powershell_version']
assert sha(Path(tool['powershell'])) == tool['powershell_sha256_now']
lean = read(RUN / 'phases/012/tasks/lean-smoke/evidence/live-final-observation.json')
assert all(sha(Path(p)) == h for p, h in lean['executables'].items())

corpus_start, corpus_final = read(E / 'corpus-start.json'), read(E / 'corpus-final.json')
old_files = []
for tree, before in corpus_start['trees'].items():
    now = {row['path']: row for row in corpus_final['trees'][tree]['rows']}
    for row in before['rows']:
        if not row['path'].endswith('/manifest.json'):
            assert row['sha256'] == now[row['path']]['sha256']
            old_files.append(row['path'])
    current_entries = read(R / tree / 'manifest.json')['entries']
    # The unchanged opposite-tree baseline was hashed before promotion; each
    # historical entry is also present verbatim in the baseline source manifest.
    original_bytes = subprocess.run(['git', 'show', 'HEAD:' + tree + '/manifest.json'],
        cwd=R, capture_output=True, check=True).stdout
    assert hashlib.sha256(original_bytes).hexdigest() == start[tree + '/manifest.json']
    initial_manifest = json.loads(original_bytes)
    assert current_entries[:-2] == initial_manifest['entries']
assert all(corpus_final[k] for k in ['raw_clean_equal', 'sha_refs_match', 'mirrored_bytes_equal'])
for name in ['mirror-plan-initial', 'mirror-plan-cache']:
    assert not read(E / (name + '.json'))['outside_writes']

record = {'at': datetime.now(timezone.utc).isoformat(), 'source_start_count': len(start),
          'source_final_count': len(final), 'changes': changes, 'outside_writes': outside,
          'suites': suites, 'live': live, 'runtime_preserved': len(old['runtime_paths']),
          'provider_inputs_preserved': old['provider_inputs'], 'host_inputs_preserved': old['host_inputs'],
          'lean_inputs_preserved': reused_paths[-4:], 'host_recordings_reused': host_records,
          'lean_tool_executables_preserved': lean['executables'],
          'host_tool_conditions': tool, 'old_nonmanifest_corpus_preserved': old_files,
          'corpus_final': corpus_final,
          'limitations': ['OS task stdout is not observed; separate real pythonw held/freeze stdout is corroboration.',
                         'Task Scheduler operational event log disabled; rapid pythonw PID may evade polling.',
                         'LastRunTime service sample differs from observer wall clock; fresh prior/after ticks and exit prove new runs.',
                         'No whole ordinary/T3/mutation/G7/G8 gate was executed.']}
save('verification-final.json', record)
print('verified', len(changes), 'changes;', [(r['folder'], r['counts']) for r in suites], '; corpus paths', sum(t['file_count'] for t in corpus_final['trees'].values()))
