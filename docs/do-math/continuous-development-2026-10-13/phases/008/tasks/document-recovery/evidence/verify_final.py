import collections
import hashlib
import json
from pathlib import Path
from run_command import ROOT, EVIDENCE, snapshot, changed, write_json
from audit_delivery import allowed, corpus, command, read

def verification():
    sources = snapshot()
    write_json(EVIDENCE / 'source-final.json', sources)
    initial = read(EVIDENCE / 'source-start.json')
    changes = changed(initial, sources)
    assert allowed(changes), changes
    suites = {}
    for label in ('red', 'focused-01', 'focused-02', 'canonical-final', 'canonical-final-02',
                  'shared-consumers-final', 'canonical-joined-final', 'mirror-final'):
        report = read(EVIDENCE / label / 'results/report.json')
        process = read(EVIDENCE / label / 'command.json')
        rows = [row for group in report['reports'] for row in group['rows']]
        ids = [row['id'] for row in rows]
        base = ROOT / ('.agents' if label == 'mirror-final' else '.claude') / 'skills/do-math/scripts'
        current = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in base.rglob('*.py')}
        mismatches = [p for p in current.keys() | report['source_sha256'].keys()
                      if current.get(p) != report['source_sha256'].get(p)]
        failures = [{k: v for k, v in row.items() if k in ('id', 'outcome', 'traceback', 'message', 'detail', 'details')}
                    for row in rows if row['outcome'] != 'passed']
        suites[label] = {'selected': len(report['selected']), 'rows': len(ids), 'unique_rows': len(set(ids)),
                        'counts': report['counts'], 'complete': report['complete'], 'successful': report['successful'],
                        'exit_code': process['exit_code'], 'changed_during_run': report['changed_during_run'],
                        'python_changes_since_run': mismatches, 'failures': failures,
                        'python_source_count': len(current), 'argv': process['argv']}
        assert len(ids) == len(set(ids)) and set(ids) == set(report['selected'])
        assert dict(collections.Counter(row['outcome'] for row in rows)) == report['counts']
        assert report['complete'] and not report['changed_during_run']
        if label in ('canonical-joined-final', 'mirror-final'):
            assert not mismatches, mismatches
            assert all(row['outcome'] in ('passed', 'failed') for row in rows), failures
            assert all('provider_final.output_contract' in str(row) for row in rows if row['outcome'] != 'passed'), failures
    prior = read(EVIDENCE.parents[3] / '007/manager-evidence/verification.json')
    runtime = prior['runtime_unchanged_since_live']
    assert len(runtime) == 124
    assert all(sources[p] == initial[p] for p in runtime)
    smoke = ['.claude/skills/do-math/scripts/' + p for p in
             ('tests/support/provider_live.py', 'tests/smoke/test_provider_live.py', 'probe_cli.py')]
    assert all(sources[p] == initial[p] for p in smoke)
    result = {'source_count': len(sources), 'changes': changes, 'suites': suites,
              'runtime_unchanged_since_start': runtime, 'smoke_inputs_unchanged': smoke,
              'corpus': corpus(), 'head': command(['git', 'rev-parse', 'HEAD']),
              'status': command(['git', '--no-optional-locks', 'status', '--porcelain=v1'])}
    assert result['head']['stdout'] == read(EVIDENCE / 'start-state.json')['head']
    for label, plan in [('mirror-build', 'mirror-plan-final'), ('cache-sync', 'cache-plan')]:
        assert set(read(EVIDENCE / label / 'command.json')['changed_sources']) == set(read(EVIDENCE / (plan + '.json'))['changed'])
    write_json(EVIDENCE / 'verification-final.json', result)
    print(json.dumps({'changes': len(changes), 'suites': {k: {x: v[x] for x in
                     ('selected', 'unique_rows', 'counts', 'exit_code')} for k, v in suites.items()},
                     'runtime': len(runtime), 'corpus': result['corpus']}, ensure_ascii=False))

if __name__ == '__main__':
    verification()
